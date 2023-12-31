import requests
import csv
import os
from passlib.context import CryptContext
import random
import matplotlib.pyplot as plt #graficar
import matplotlib.image as mpimg #manipular imagenes
import tempfile #archivos temporales
from datetime import date #para fecha actual
import Utilidades

#ctes
URL = "https://v3.football.api-sports.io"
CLAVE= "b1026f7aeb5dec5f5718843763856307"
API= "v3.football.api-sports.io"
         
def registrar_usuario(usuarios:dict)-> str:
    #permite guardar un nuevo usuario en el diccionario de usuarios, siempre y cuando el mail no exista en el mismo
    #devuelve 0 si el mail ya existe en el diccionario
    myctx: CryptContext= CryptContext(schemes=["sha256_crypt", "md5_crypt"])
    correo:str = Utilidades.ingresar_email()
    if(correo in usuarios):
        print("Ya existe un usuario registrado con ese correo")
        correo=0
    else:
        nombre:str = input("Ingrese su nombre de usuario:")
        contrasena:str = myctx.hash(input("Ingrese su contrasenia: "))
        usuarios[correo] = {
            'nombre': nombre,
            'contrasena': contrasena,
            'cantidad_total_apostada': 0, #dinero total apostado hasta el momento
            'fecha_ultima_apuesta': None,
            'dinero': 0 #actual del usuario
        }
        guardar_usuarios(usuarios) #se guarda en el archivo
        print("Registro realizado, para apostar recuerde cargar dinero por primera vez")
    return correo 

def iniciar_sesion(usuarios:dict) -> str:
    #recibe el diccionario de usuarios y permite que un usuario se identifique, siempre que exista y ingrese su contraseña correctamente
    #devuelve 0 si no se pudo identificar (contraseña incorrecta)
    myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
    myctx.default_scheme() #esquema para cifrado por defecto
    correo:str = input("Ingrese su correo electrónico:")
    contrasena:str = input("Ingrese su contrasenia: ")
    if correo in usuarios:
        if(myctx.verify(contrasena, usuarios[correo]['contrasena'])): #myctx.verify compara la contraseña ingresada, con la guardada que se encuentra cifrada
            print("Inicio de sesión realizado")
        else:
            print("Contrasenia incorrecta")
            correo=0
    else:
        print("No hay ninguna cuenta con ese mail")
        correo=0
    return correo

def mostrar_menu()-> None:
    #No recibe nada por parámetro
    #Muestra lista de opciones
    print("-"*80)
    print("Ingrese el número correspondiente a la opción que desee:")
    print("-"*80)
    print("0) Salir")
    print("1) Mostrar el plantel completo de un equipo ingresado")
    print("2) Mostrar la tabla de posiciones en una temporada")
    print("3) Información sobre el estadio y escudo de un equipo")
    print("4) Gráfico de goles por minuto para un equipo")
    print("5) Cargar dinero en cuenta de usuario") 
    print("6) Usuario que más apostó") 
    print("7) Usuario que más veces ganó")
    print("8) Apostar")
    print("-"*80)
    
def apostar(equipos:dict, fixtures: dict, id_usuario:str, usuarios:dict, transacciones:dict, fecha_actual:str)->None:
    #Recibe diccionarios de: equipos, partidos, usuarios y transacciones, además del mail del usuario que actualmente usa el programa
    #Permite al usuario apostar, y al finalizar en el diccionario de usuarios y de transacciones apareceran los cambios o ingresos correspondientes
    print("-"*80)
    mostrar_equipos(equipos)
    print("-"*80)
    id_equipo=ingresar_equipo(equipos)
    informacion_partidos:dict={}
    for partido in fixtures:
        fecha,hora = partido["fixture"]["date"].split('T')
        if((partido["teams"]["home"]["id"]==id_equipo or partido["teams"]["away"]["id"]==id_equipo) and validar_fecha_mayor(fecha, fecha_actual)):
            #si el equipo elegido es local o visitante en el partido, y si el partido todavía no se jugó
            id_partido=partido['fixture']['id']
            local = partido["teams"]["home"]["name"]
            visitante = partido["teams"]["away"]["name"]
            pago_local= partido['fixture']['cantidad_veces_pago']
            pago_visitante= partido['fixture']['cantidad_veces_pago']
            informacion_partidos[fecha]=[local, visitante, pago_local, pago_visitante, id_partido]
            print("-"*80)
            print(f"Fecha: ",fecha)
            print(f"Equipo local:", local)
            print(f"Equipo visitante:", visitante)
            print("-"*80)
    
    print("Ingrese la fecha del partido para el que quiere apostar, YYYY-MM-DD")
    fecha= Utilidades.validar_fecha()
    print("-"*80)
    while(fecha not in informacion_partidos):
        print("Error. Ingrese una de las fechas mostradas anteriormente:")
        fecha= Utilidades.validar_fecha()

    params = {
        "fixture":informacion_partidos[fecha][4]
    }
    prediccion= consultar_api("/predictions",params)
    if(prediccion[0]["predictions"]["win_or_draw"]==True): #si winner tiene win or draw
        equipo_win_or_draw = prediccion[0]['predictions']["winner"]["name"] 
    else: #si winner no tiene win or draw, tomo como que lo tiene el otro equipo
        if(prediccion[0]["teams"]["home"]["name"] == prediccion[0]['predictions']["winner"]["name"]): #si winner es local
            equipo_win_or_draw= prediccion[0]["teams"]["away"]["name"] #win or draw lo tiene el visitante
        else: #si winner es visitante
            equipo_win_or_draw= prediccion[0]["teams"]["home"]["name"] #win or draw lo tiene el local

    if(equipo_win_or_draw == informacion_partidos[fecha][0]): #win or draw local
        informacion_partidos[fecha][2]=informacion_partidos[fecha][2]*10/100 #
    elif(equipo_win_or_draw == informacion_partidos[fecha][1]): #win or draw visitante
        informacion_partidos[fecha][3]=informacion_partidos[fecha][3]*10/100
    else:
        print("Se produjo un error al reconocer win_or_draw")

    print(f"Equipo local:", informacion_partidos[fecha][0], "paga: ",informacion_partidos[fecha][2],"veces de lo apostado")
    print(f"Equipo visitante:", informacion_partidos[fecha][1],"paga: ",informacion_partidos[fecha][3],"veces de lo apostado")

    print("Ingrese el monto a apostar")
    monto_a_apostar= Utilidades.ingresar_float(1,999999)
    print("-"*80)
    dinero_suficiente= verificar_si_usuario_tiene_dinero_suficiente(id_usuario, monto_a_apostar, usuarios)

    if (dinero_suficiente):
        print("-"*80)
        print("Descontando dinero... Por favor aguarde")
        registrar_apuesta_en_usuario(id_usuario, monto_a_apostar, fecha_actual, usuarios) #actualiza fecha ultima apuesta y suma monto al total apostado
        modificar_dinero_usuario(id_usuario, monto_a_apostar, "Resta",usuarios)

        print("Momento de apostar, buena suerte!")
        print("-"*80)
        print("Ingrese el número de apuesta que desee hacer")

        posibilidades=["Gana Local","Empate","Gana Visitante"]

        print(f"1)",posibilidades[0])
        print(f"2)",posibilidades[1])
        print(f"3)",posibilidades[2])
        
        respuesta=int(Utilidades.ingresar_entero(1,3)) #apuesta
        print("-"*80)
        print()
        print("Se juega el partido...")
        print()
        print("-"*80)

        resultado_simulado=random.randint(1, 3) #resultado simulado del partido
        print(f"Resultado del partido: ", posibilidades[(int(resultado_simulado)-1)])
        print(f"Tu apuesta: ", posibilidades[(int(respuesta)-1)])
        print("-"*80)
        if(resultado_simulado==respuesta):#gana
            print("Felicidades!")
            if(resultado_simulado==1):#apuesta gana local y gana local
                monto=monto_a_apostar+(informacion_partidos[fecha][2]*monto_a_apostar) #cantidad de veces de local x monto a apostar
            elif(resultado_simulado==2):#apuesta empate, pagaría la mitad
                monto=monto_a_apostar+(monto_a_apostar/2)
            elif(resultado_simulado==3):#apuesta gana visitante
                monto=monto_a_apostar+(informacion_partidos[fecha][3]*monto_a_apostar) #cantidad de veces de visitante x monto a apostar
            ganancia_total=monto-monto_a_apostar
            print(f"Ganaste un total de ", ganancia_total, "pesos y se te devolverá el dinero apostado")
            #la transaccion que guardo contempla la devolucion del dinero + lo que gana como tal
            guardar_transaccion_en_diccionario(id_usuario, transacciones, fecha_actual, "Gana", ganancia_total)
            modificar_dinero_usuario(id_usuario, monto,"Suma",usuarios)
        else: #pierde (sale algo distinto a lo que apostó)
            print(f"Perdiste ",monto_a_apostar,"pesos, mejor suerte la proxima")
            guardar_transaccion_en_diccionario(id_usuario, transacciones, fecha_actual, "Pierde", -(monto_a_apostar))
    else: #no tiene dinero suficiente para la apuesta que quiere hacer
        print("Lamentamos informarle que no tiene dinero suficiente para realizar esta apuesta")

def obtener_usuarios()-> dict:
    #No recibe nada por parámetro
    #Se encarga de guardar en un diccionario la información del archivo de usuarios y devuelve el mismo
    usuarios:dict = {}
    archivo_usuarios:str = 'usuarios.csv'
    try:
        if os.path.isfile(archivo_usuarios): # si el archivo existe
            with open(archivo_usuarios, 'r', encoding='UTF-8') as archivo_csv: # modo lectura
                csv_reader = csv.reader(archivo_csv, delimiter=',')
                next(csv_reader)
                for fila in csv_reader: #por cada fila del archivo csv de usuarios
                    correo = fila[0]
                    usuarios[correo] = { #las claves en el dict son correos
                        'nombre': fila[1],
                        'contrasena': fila[2],
                        'cantidad_total_apostada': float(fila[3]),
                        'fecha_ultima_apuesta': fila[4],
                        'dinero': float(fila[5])
                    }
        else: #si el archivo no existe lo creo escribo el encabezado
            with open(archivo_usuarios, 'w', encoding='UTF-8', newline='') as archivo_csv:
                encabezado = ["Correo", "Nombre", "Contrasenia", "Cantidad Apostada", "Fecha Ultima Apuesta", "Dinero"]
                csv_writer = csv.writer(archivo_csv)
                csv_writer.writerow(encabezado)
    except:
        print("Error al abrir, leer o crear archivo de usuarios")
    return usuarios

def guardar_usuarios(usuarios:dict)-> None:
    #Recibe diccionario de usuarios
    #Reescribe el archivo usuarios con el contenido actualizado presente en el diccionario usuarios
    try:
        with open('usuarios.csv', 'w', newline='', encoding='UTF-8') as archivo_csv:
            csv_writer = csv.writer(archivo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
            encabezado = ["Correo", "Nombre", "Contrasenia", "Cantidad Apostada", "Fecha Ultima Apuesta", "Dinero"]
            csv_writer.writerow(encabezado)  #escribir el encabezado
            for correo, datos in usuarios.items():
                csv_writer.writerow([ #escribo los datos separados por comas
                    correo,
                    datos['nombre'],
                    datos['contrasena'],
                    datos['cantidad_total_apostada'],
                    datos['fecha_ultima_apuesta'],
                    datos['dinero']
                ])
    except:
        print("Error al abrir o escribir archivo usuarios")

def obtener_transacciones()->dict:
    #No recibe nada por parámetro
    #Devuelve diccionario con el contenido del archivo transacciones. clave: id_usuario, datos: cada transaccion
    transacciones = {}
    archivo_transacciones = 'transacciones.csv'
    usuarios=[]
    if os.path.isfile(archivo_transacciones): # si el archivo existe
        with open(archivo_transacciones, 'r', encoding='UTF-8') as archivo_csv: # modo lectura
            csv_reader = csv.reader(archivo_csv, delimiter=',')
            next(csv_reader)
            for fila in csv_reader:
                id_usuario = fila[0]
                fecha = fila[1]
                tipo = fila[2]
                importe = float(fila[3])
                if id_usuario not in usuarios: #si es la primera transaccion del usuario
                    usuarios.append(id_usuario)
                    transacciones[id_usuario] = [[fecha, tipo, importe]]
                else: #si el usuario ya tiene transacciones guardadas en el diccionario
                    transacciones[id_usuario].append([fecha, tipo, importe])
    else: #si el archivo no existe
        with open(archivo_transacciones, 'w', encoding='UTF-8', newline='') as archivo_csv:
            encabezado = ["Id Usuario", "Fecha", "Tipo", "Importe"]
            csv_writer = csv.writer(archivo_csv)
            csv_writer.writerow(encabezado)
    return transacciones

def guardar_transacciones(transacciones:dict)->None:
    #Recibe diccionario de transacciones
    #Reescribe el archivo de transacciones con el contenido del diccionario de transacciones
    with open('transacciones.csv', 'w', newline='', encoding='UTF-8') as archivo_csv:
        csv_writer = csv.writer(archivo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        encabezado = ["Id Usuario", "Fecha", "Tipo", "Importe"]
        csv_writer.writerow(encabezado)  # escribo el encabezado    
        for id_usuario, transacciones_del_usuario in transacciones.items():
            for transaccion in transacciones_del_usuario:
                csv_writer.writerow([
                    id_usuario,
                    transaccion[0], #fecha
                    transaccion[1], #tipo
                    transaccion[2] #importe
                ])

def registrar_apuesta_en_usuario(id_usuario:str, monto:float, fecha:str, usuarios:dict)->None:
    #Recibe id_usuario, monto a apostar, fecha de la apuesta y el diccionario de usuarios
    #Modifica el diccionario de usuarios, sumando la nueva apuesta a la cantidad apostada y actualizando la fecha de la ultima apuesta
    usuarios[id_usuario]['cantidad_total_apostada']=(float(usuarios[id_usuario]['cantidad_total_apostada']))+float(monto)
    usuarios[id_usuario]['fecha_ultima_apuesta']=fecha

def guardar_transaccion_en_diccionario(id_usuario:str, transacciones:dict, fecha_actual:str, tipo:str, monto:float)->None:
    #Recibe id_usuario, diccionario transacciones, fecha actual, tipo de transaccion y monto de la misma
    #Guarda la transaccion en el diccionario de transacciones
    transaccion:list = [fecha_actual, tipo, monto]
    if id_usuario in transacciones:
        # usuario ya tiene transacciones
        transacciones[id_usuario].append(transaccion)
    else:
        # usuario no tiene transacciones
        transacciones[id_usuario] = [transaccion]


def modificar_dinero_usuario(id_usuario:str, monto:float, operacion:str, usuarios:dict)->None:
    #Recibe id_usuario, monto a modificar, operacion a realizar (suma o resta) y el diccionario de usuarios
    #Agrega o quita dinero al usuario en el diccionario de usuarios y lo informa por consola
    if id_usuario in usuarios:
        dinero_en_cuenta = float(usuarios[id_usuario]['dinero'])
        if(operacion=="Suma"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta + float(monto)
        elif(operacion=="Resta"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta - float(monto)
        else:
            print("Error al reconocer operacion")
    print (f"Ahora posee {usuarios[id_usuario]['dinero']} disponible en su cuenta. ")

def verificar_si_usuario_tiene_dinero_suficiente(id_usuario:str, monto:float, usuarios:dict)->bool:
    #Recibe id_usuario, monto del que se quiere verificar si dispone o no y el diccionario de usuarios
    #Devuelve True si tiene igual o más de ese monto, False en caso contrario
    dinero_suficiente= False
    if id_usuario in usuarios:
        dinero = float(usuarios[id_usuario]['dinero'])
        if dinero >= float(monto):
            dinero_suficiente= True
    return dinero_suficiente

def ingresar_equipo(equipos: dict)->int:
    id=0
    while(id==0):
        print("Ingrese nombre del equipo: (Respetar mayusculas y minusculas)")
        equipo_elegido=input()
        id= obtener_id_equipo(equipos, equipo_elegido)
    return id

def consultar_api(endpoint:str, params:dict)->dict:
    respuesta=[]
    try:
        url = URL + endpoint
        headers = {
            'x-rapidapi-host': API,
            'x-rapidapi-key': CLAVE
        }
        resultado = requests.get(url, params=params, headers=headers)
    except:
        print("Error al conectarse con el servidor")
    # verifico estado de la solicitud       
    else:
        if resultado.status_code == 200: #si fue exitosa
            data = resultado.json()
            respuesta = data['response']  
    return respuesta

def validar_fecha_mayor(fecha1:str, fecha2:str)->bool:
    if fecha1 > fecha2:
        es_mayor=True
    else:
        es_mayor=False
    return es_mayor

def obtener_cantidad_de_veces()->int:
    #No recibe nada por parámetro
    #Funcion que devuelve un numero random entero entre el 1 y el 4 inclusive, que representa la cantidad de veces base que se le pagara lo que apostó al usuario en caso de ganar
    cantidad_veces=random.randint(1, 4)
    return cantidad_veces
      
def mostrar_informacion_estadio_y_escudo(id_equipo:int, equipos:dict)->None:
    #Recibe id de un equipo y el diccionario de equipos
    #Muestra información del estado y abre imagen del escudo del equipo ingresado
    estadio:dict={}
    print()
    print("Información del estadio y escudo:")
    for equipo in equipos:
        if(equipo['team']["id"]==id_equipo):
            estadio=equipo['venue']
            equipo_elegido=equipo['team']
    
    print("Nombre del estadio:", estadio['name'])
    print("Dirección:", estadio['address'])
    print("Ciudad:", estadio['city'])
    print("Capacidad:", estadio['capacity'])
    print("Superficie:", estadio['surface'])
    enlace_imagen:str = estadio['image']
    response = requests.get(enlace_imagen)
    with tempfile.NamedTemporaryFile(delete=False) as imagen_temporal:
        imagen_temporal.write(response.content)
        nombre_imagen_temporal = imagen_temporal.name
    imagen = mpimg.imread(nombre_imagen_temporal)
    plt.imshow(imagen)
    plt.show() #muestro imagen y se espera a que se cierre
    os.remove(nombre_imagen_temporal)
    print()
    enlace_imagen:str = equipo_elegido['logo']
    response = requests.get(enlace_imagen)
    with tempfile.NamedTemporaryFile(delete=False) as imagen_temporal:
        imagen_temporal.write(response.content)
        nombre_imagen_temporal = imagen_temporal.name
    imagen = mpimg.imread(nombre_imagen_temporal)
    plt.imshow(imagen)
    plt.show() #muestro imagen y se espera a que se cierre
    os.remove(nombre_imagen_temporal)

def mostrar_equipos(equipos:dict)->None:
    #Recibe diccionario de equipos
    #Muestra los nombres de los equipos del diccionario
    print("Equipos de la Liga Profesional Argentina correspondientes a la temporada actual:")
    for equipo in equipos:
        print(equipo['team']['name'])
    print()

def obtener_id_equipo(equipos:dict, equipo_elegido:str)->int:
    #Recibe diccionario de equipos y un nombre de equipo
    #Devuelve el id del equipo, si devuelve 0 significa que no se encuentra el id_equipo en equipos
    id=0
    for equipo in equipos:
        if((equipo_elegido) == (equipo['team']['name'])):
            id=equipo['team']['id']
    return id

def main()->None:
    #Funcion principal del programa
    print("-"*80)
    print("La adicción al juego no es un vicio, sino una peligrosa enfermedad")
    print("-"*80)
    print()
    print("Bienvenidx al portal de apuestas Jugarsela")
    usuarios:dict=obtener_usuarios() #del archivo usuarios.csv
    transacciones:dict=obtener_transacciones() #del archivo transacciones.csv

    finalizar = False #True si el usuario decide salir
    id_usuario:str= 0 #Si hubo problemas al identificarse

    while (id_usuario==0 and not finalizar): #mientras que no se identifique y no decida salir
        print("1)Iniciar sesión")
        print("2)Registrarse")
        print("3)Salir")
        respuesta:int=int(Utilidades.ingresar_entero(1,3))
        if(respuesta == 1):
            id_usuario = iniciar_sesion(usuarios)
        elif(respuesta == 2):
            id_usuario= registrar_usuario(usuarios)
        elif(respuesta == 3):
            finalizar= True

    if (not finalizar): #si el usuario decide salir, no hago las consultas a la api (una sola vez x eso no en el while)
        
        fecha = date.today()
        fecha_actual = fecha.strftime("%Y-%m-%d")
        anio_actual = fecha.year

        #cargo mis estructuras
        params = {"league": "128","country": "Argentina","season": anio_actual}
        equipos:dict= consultar_api("/teams", params)
        params = {"league": "128","season": anio_actual}
        fixtures:dict= consultar_api("/fixtures", params)
        for partido in fixtures:
                partido['fixture']['cantidad_veces_pago'] = obtener_cantidad_de_veces()
    while not finalizar:
        print("-"*80)
        input("apretar ENTER para continuar")
        mostrar_menu()
        opcion = Utilidades.ingresar_entero(0,8)
        print("-"*80)
        if opcion!= 0: #opcion distinta de "0)Salir"

            if opcion == 1: #mostrar plantel de un equipo elegido
                if(equipos != []): #si equipos tiene información
                    mostrar_equipos(equipos)
                    id= ingresar_equipo(equipos)
                    print()
                    params = {"league": "128","season": anio_actual, "team": id}
                    jugadores_del_equipo:dict=consultar_api("/players", params)
                    print(f"Plantel del equipo seleccionado:")
                    for jugador in jugadores_del_equipo:
                        print(f"Nombre:",jugador['player']['name']," Posición:", jugador['statistics'][0]['games']['position'])
                else:
                    print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")
            
            elif opcion == 2: #ver tabla de posiciones
                print("Ingrese el anio del cual desea ver la tabla de posiciones de la Liga Argentina: (2020 no disponible)")
                temporada:int= int(Utilidades.ingresar_entero(2015, anio_actual))
                if(temporada!=2020):
                    params = {
                        "league": "128",
                        "season": temporada
                    }
                    posiciones=consultar_api("/standings",params)
                    if(posiciones != []):
                        if(len(posiciones)>0):
                            print("Posicion, Equipo, Pts")
                            fases= len(posiciones[0]['league']['standings'])
                            for fase in range(fases):
                                print(f"Fase:", (fase+1))
                                for equipo in range(len(posiciones[0]['league']['standings'][fase])):
                                    datos_equipo=posiciones[0]['league']['standings'][fase][equipo]                              
                                    print(datos_equipo['rank'],",",datos_equipo['team']['name'],",",datos_equipo['points'])
                        else:
                            print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")
                    else:
                        print("Parece que no contamos con la información necesaria actualmente, intente más tarde")
                else:
                    print("Lo sentimos... para 2020 no podemos mostrar la información solicitada")
            
            elif opcion == 3: #mostrar información estadio y escudo
                if(equipos!=[]):
                    mostrar_equipos(equipos)
                    id=ingresar_equipo(equipos)
                    mostrar_informacion_estadio_y_escudo(id, equipos)
                else:
                    print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")

            elif opcion == 4: #mostrar goles por minuto
                if(equipos!= []):
                    mostrar_equipos(equipos)
                    print("-"*80)
                    print("Ingrese el equipo para el que desee ver goles por minuto")
                    print("-"*80)
                    id=ingresar_equipo(equipos)
                    params = {
                        "league": "128",
                        "season": 2023,
                        "team": id
                    }
                    estadisticas= consultar_api("/teams/statistics",params)
                    if (estadisticas!=[]):
                        goles_por_minuto:dict=estadisticas['goals']['for']['minute']
                        intervalos_de_tiempo:list = goles_por_minuto.keys()
                        goles=[]
                        for intervalo in goles_por_minuto.values():
                            if intervalo['total'] is None:
                                intervalo['total'] = 0
                            cantidad_goles = intervalo['total']
                            goles.append(cantidad_goles)
                        plt.bar(intervalos_de_tiempo, goles)
                        plt.xlabel('Minutos')
                        plt.ylabel('Cantidad de goles')
                        plt.title('Gráfico de goles por intervalos de minutos')
                        plt.show()
                    else:
                        print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")
                else:
                    print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")

            elif opcion == 5: #cargar dinero a un usuario
                print("Elegiste cargar dinero")
                print("Ingrese monto, para cancelar ingrese 0")
                monto=Utilidades.ingresar_entero(0,99999)
                if(monto!=0):
                    modificar_dinero_usuario(id_usuario, monto, "Suma", usuarios)
                    guardar_transaccion_en_diccionario(id_usuario,transacciones,fecha_actual,"Deposito",monto)

            elif opcion == 6: #usuario que más dinero apostó
                cantidad_max=0
                for usuario in usuarios:
                    if usuarios[usuario]['cantidad_total_apostada']>cantidad_max:
                        cantidad_max=usuarios[usuario]['cantidad_total_apostada']
                        usuario_mas_aposto=usuario
                print(f"El usuario que más dinero apostó hasta la fecha es:",usuario_mas_aposto," y apostó un total de ",cantidad_max," pesos")

            elif opcion == 7: #usuario que mas veces ganó
                cantidad_apuestas_ganadas_por_usuario={} #diccionario que tiene de clave, el id_usuario y de dato la cantidad de veces que ganó
                for usuario in transacciones:
                    cantidad_apuestas_ganadas_por_usuario[usuario]=0
                    for transaccion in transacciones[usuario]: #por cada transaccion del usuario
                        if(transaccion[1]=="Gana"): #si es de tipo gana
                            cantidad_apuestas_ganadas_por_usuario[usuario]+=1
                max=0
                usuario_mas_gano = ""
                max_cant_veces_ganadas=0
                for usuario, cantidad in cantidad_apuestas_ganadas_por_usuario.items():
                    if cantidad > max_cant_veces_ganadas:
                        max_cant_veces_ganadas = cantidad
                        usuario_mas_gano = usuario
                print("El usuario que más veces ganó fue:",usuarios[usuario_mas_gano]['nombre']," (mail",usuario_mas_gano,") y ganó ",max_cant_veces_ganadas, " veces")
            
            elif opcion == 8: #sistema de apuestas
                tiene_dinero= verificar_si_usuario_tiene_dinero_suficiente(id_usuario, 1, usuarios) #verifico si tiene al menos 1 peso
                if(equipos !=[] and fixtures!=[]):
                    if (tiene_dinero): #si el usuario tiene por lo menos 1 peso
                        print("Bienvenidx al sistema de apuestas")
                        apostar(equipos, fixtures, id_usuario, usuarios, transacciones, fecha_actual)
                    else: #no tiene dinero el usuario
                        print("No tenes dinero, debes cargar algo a tu cuenta para poder apostar")
                else: #no hay datos en los diccionarios
                    print("Ups... El sistema de apuestas no funciona actualmente, intente de nuevo mas tarde")
            else: #la opcion no es ninguna de las contempladas
                print("Error desconocido (revisar validación)")
        else: #opcion es 0
            finalizar = True
            guardar_usuarios(usuarios)
            guardar_transacciones(transacciones)
    print("-"*80)
    print("Hasta pronto")
    print("-"*80)
    
main()