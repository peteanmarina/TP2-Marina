import requests
import os
from passlib.context import CryptContext
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tempfile
import Utilidades
import Manejo_Archivos

URL = "https://v3.football.api-sports.io"
CLAVE= "b1026f7aeb5dec5f5718843763856307"
API= "v3.football.api-sports.io"
         
def registrar_usuario(usuarios:dict)-> str:
    #permite guardar un nuevo usuario en el diccionario de usuarios, siempre y cuando el main no exista en el mismo
    #devuelve 0 si el mail ya existe
    myctx: CryptContext= CryptContext(schemes=["sha256_crypt", "md5_crypt"])
    correo:str = Utilidades.ingresar_email()
    if(correo in usuarios):
        print("Ya existe un usuario registrado con ese correo")
        correo=0
    else:
        nombre:str = input("Ingrese su nombre de usuario:")
        contrasena:str = myctx.hash(input("Ingrese su contraseña: "))
        usuarios[correo] = {
            'nombre': nombre,
            'contrasena': contrasena,
            'cantidad_total_apostada': 0, #dinero total apostado hasta el momento
            'fecha_ultima_apuesta': None,
            'dinero': 0 #actual del usuario
        }
        Manejo_Archivos.guardar_usuarios(usuarios) #se guarda en el archivo
        print("Registro realizado, para apostar recuerde cargar dinero por primera vez")
        
    return correo 

def iniciar_sesion(usuarios:dict) -> str:
    #recibe el diccionario de usuarios y permite que un usuario se identifique, siempre que exista y ingrese su contraseña correctamente
    #devuelve 0 si no se pudo identificar (contraseña incorrecta)
    myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
    myctx.default_scheme() #esquema para cifrado por defecto
    correo:str = input("Ingrese su correo electrónico:")
    contrasena:str = input("Ingrese su contraseña: ")

    if correo in usuarios:
        if(myctx.verify(contrasena, usuarios[correo]['contrasena'])): #myctx.verify compara la contraseña ingresada, con la guardada que se encuentra cifrada
            print("Inicio de sesión realizado")
        else:
            print("Contraseña incorrecta")
            correo=0
    else:
        print("No hay ninguna cuenta con ese mail")
        correo=0
    return correo

def mostrar_menu()-> None:
    #Funcion que muestra lista de opciones
    print("-"*80)
    print("Ingrese el número correspondiente a la opción que desee:")
    print("-"*80)
    print("0) Salir")
    print("1) Mostrar el plantel completo de un equipo ingresado")
    print("2) Mostrar la tabla de posiciones de la Liga profesional de una temporada")
    print("3) Información sobre el estadio y escudo de un equipo")
    print("4) Goles y los minutos en los que fueron realizados para un equipo")
    print("5) Cargar dinero en cuenta de usuario") 
    print("6) Usuario que más apostó") 
    print("7) Usuario que más gano")
    print("8) Apostar")
    print("-"*80)
    
def apostar(equipos:dict, fixtures: dict, id_usuario:str, usuarios:dict, transacciones:dict)->None:
    #Funcion que recibe diccionarios de: equipos, partidos, usuarios y transacciones, además del mail del usuario que actualmente usa el programa
    #Permite al usuario apostar, y al finalizar en el diccionario de usuarios y de transacciones apareceran los cambios o ingresos correspondientes
    print("-"*80)
    print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
    mostrar_equipos(equipos)
    print("-"*80)
    
    id_equipo=0
    while(id_equipo==0):
        print("Ingrese nombre de un equipo para ver un listado de los partidos que jugará el mismo")
        equipo_elegido=input()
        id_equipo= obtener_id_equipo(equipos, equipo_elegido)
        
    informacion_partidos:dict={}
    for partido in fixtures:
        if(partido["teams"]["home"]["id"]==id_equipo or partido["teams"]["away"]["id"]==id_equipo):
            id_partido=partido['fixture']['id']
            local = partido["teams"]["home"]["name"]
            visitante = partido["teams"]["away"]["name"]
            pago_local= partido['teams']['home']['cantidad_veces_pago']
            pago_visitante= partido['teams']['away']['cantidad_veces_pago']
            fecha,hora = partido["fixture"]["date"].split('T')
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
    equipo_win_or_draw = prediccion[0]['predictions']["winner"]["name"]

    if(equipo_win_or_draw == informacion_partidos[fecha][0]):
        informacion_partidos[fecha][2]=informacion_partidos[fecha][2]*10/100
    elif(equipo_win_or_draw == informacion_partidos[fecha][1]):
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
        print("Le solicitaremos la fecha del día de hoy para finalizar la transaccion")
        fecha_actual=Utilidades.validar_fecha()
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
                monto=monto_a_apostar+(informacion_partidos[fecha][2]*monto_a_apostar)
            elif(resultado_simulado==2):#apuesta empate, pagaría la mitad
                monto=monto_a_apostar+(monto_a_apostar/2)
            elif(resultado_simulado==3):#apuesta gana visitante
                monto=monto_a_apostar+(informacion_partidos[fecha][3]*monto_a_apostar)
            ganancia_total=monto-monto_a_apostar
            print(f"Ganaste un total de ", ganancia_total, "pesos y se te devolverá el dinero apostado")
            #la transaccion que guardo contempla la devolucion del dinero + lo que gana como tal
            guardar_transaccion_en_diccionario(id_usuario, transacciones, fecha_actual, "Gana", ganancia_total)
            modificar_dinero_usuario(id_usuario, monto,"Suma",usuarios)

        else: #pierde
            print(f"Perdiste tus ",monto_a_apostar,"pesos, mejor suerte la próxima")
            guardar_transaccion_en_diccionario(id_usuario, transacciones, fecha_actual, "Pierde", -(monto_a_apostar))

    else:
        print("Lamentamos informarle que no tiene dinero suficiente para realizar esta apuesta")

def registrar_apuesta_en_usuario(id_usuario:str, monto:float, fecha:str, usuarios:dict)->None:
    #Recibe id_usuario, monto a apostar, fecha de la apuesta y el diccionario de usuarios
    #Modifica el diccionario de usuarios, sumando la nueva apuesta a la cantidad apostada y actualizando la fecha de la ultima apuesta
    usuarios[id_usuario]['cantidad_total_apostada']=(float(usuarios[id_usuario]['cantidad_total_apostada']))+float(monto)
    usuarios[id_usuario]['fecha_ultima_apuesta']+=fecha

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


def modificar_dinero_usuario(id_usuario:str, monto:float, operación:str, usuarios:dict)->None:
    #Recibe id_usuario, monto a modificar, operacion a realizar (suma o resta) y el diccionario de usuarios
    #Agrega o quita dinero al usuario en el diccionario de usuarios y lo informa por consola
    if id_usuario in usuarios:
        dinero_en_cuenta = float(usuarios[id_usuario]['dinero'])
        if(operación=="Suma"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta + float(monto)
        elif(operación=="Resta"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta - float(monto)
        else:
            print("Error al reconocer operación")
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
      
def mostrar_informacion_estadio_y_escudo(id_equipo:int, equipos:dict)->None:
    #Recibe id de un equipo y el diccionario de equipos
    #Muestra información del estado y abre imagen del escudo del equipo ingresado
    estadio:dict={}
    for equipo in equipos:
        if(equipo['team']["id"]==id_equipo):
            estadio=equipo['venue']
            equipo_elegido=equipo['team']
    
    print("Nombre del estadio:", estadio['name'])
    print("Dirección:", estadio['address'])
    print("Ciudad:", estadio['city'])
    print("Capacidad:", estadio['capacity'])
    print("Superficie:", estadio['surface'])

    enlace_imagen:str = equipo_elegido['logo']
    response = requests.get(enlace_imagen)
    # guardo la imagen temporalmente
    with tempfile.NamedTemporaryFile(delete=False) as imagen_temporal: #cargo la imagen
        imagen_temporal.write(response.content)
        nombre_imagen_temporal = imagen_temporal.name
    imagen = mpimg.imread(nombre_imagen_temporal)
    plt.imshow(imagen)
    plt.show() #muestro imagen
    os.remove(nombre_imagen_temporal) #borro imagen

def mostrar_equipos(equipos:dict)->None:
    #Recibe diccionario de equipos
    #Muestra los nombres de los equipos del diccionario
    for equipo in equipos:
        print(equipo['team']['name'])

def obtener_id_equipo(equipos:dict, equipo_elegido:str)->int:
    #Recibe diccionario de equipos y un nombre de equipo
    #Devuelve el id del equipo, 0 si no se encuentra el id_equipo en equipos
    id=0
    for equipo in equipos:
        if(equipo_elegido) == (equipo['team']['name']):
            id=equipo['team']['id']
    return id

def main()->None:
    #Funcion principal del programa
    print("-"*80)
    print("La adicción al juego no es un vicio, sino una peligrosa enfermedad")
    print("-"*80)
    print()
    print("Bienvenidx al portal de apuestas Jugarsela")
    usuarios:dict=Manejo_Archivos.obtener_usuarios() #del archivo usuarios.csv
    transacciones:dict=Manejo_Archivos.obtener_transacciones() #del archivo transacciones.csv

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
    if (not finalizar): #si el usuario decide salir, no hago las consultas a la api
        #cargo mis estructuras
        params = {"league": "128","country": "Argentina","season": 2023}
        equipos:dict= consultar_api("/teams", params)
        params = {"league": "128","season": 2023}
        fixtures:dict= consultar_api("/fixtures", params)
        for partido in fixtures:
                partido['teams']['home']['cantidad_veces_pago'] = Utilidades.obtener_cantidad_de_veces()
                partido['teams']['away']['cantidad_veces_pago'] = Utilidades.obtener_cantidad_de_veces()
    while not finalizar:
        mostrar_menu()
        opcion = Utilidades.ingresar_entero(0,8)
        if opcion!= 0: #opcion distinta de 0)Salir
            if opcion == 1: 
                if(equipos != []):
                    print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
                    mostrar_equipos(equipos)
                    id=0
                    while(id==0):
                        print("Ingrese nombre del equipo que desee ver el plantel")
                        equipo_elegido=input()
                        id= obtener_id_equipo(equipos, equipo_elegido)
                    params = {"league": "128","season": 2023, "team": id}
                    jugadores_del_equipo:dict=consultar_api("/players", params)
                    for jugador in jugadores_del_equipo:
                        print(jugador['player']['name'])
                else:
                    print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")
            elif opcion == 2:
                print("Ingrese el anio del cual desea ver la tabla de posiciones de la Liga Argentina:")
                temporada:int= Utilidades.ingresar_entero(2015, 2023)
                params = {
                    "league": "128",
                    "season": temporada
                }
                posiciones=consultar_api("/standings",params)
                if(posiciones != []):
                    print("Posicion, Equipo, Pts")
                    if(len(posiciones)>0):
                        for equipo in range(len(posiciones[0]['league']['standings'][0])):
                            datos_equipo=posiciones[0]['league']['standings'][0][equipo]                              
                            print(datos_equipo['rank'],",",datos_equipo['team']['name'],",",datos_equipo['points'])
                    else:
                        print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")
            elif opcion == 3:
                if(equipos!=[]):
                    print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
                    mostrar_equipos(equipos)
                    id=0
                    while(id==0):
                        print("Ingrese nombre del equipo que desee ver la información sobre el estadio y su escudo")
                        equipo_elegido= input()
                        id=obtener_id_equipo(equipos, equipo_elegido)
                    mostrar_informacion_estadio_y_escudo(id, equipos)
                else:
                    print("Ups, lo sentimos, no podemos satisfacer su petición. Intente de nuevo más tarde")

            elif opcion == 4:
                if(equipos!= []):
                    id=0
                    while(id==0):
                        print("Ingrese nombre del equipo que desee ver goles por minutos")
                        equipo_elegido=input()
                        id= obtener_id_equipo(equipos, equipo_elegido)
                    params = {
                        "league": "128",
                        "season": 2023,
                        "team": id
                    }
                    estadisticas= consultar_api("/teams/statistics",params)
                    if (estadisticas!=[]):
                        goles_por_minuto=estadisticas['goals']['for']['minute']
                        intervalos_de_tiempo = goles_por_minuto.keys()
                        goles = []
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

            elif opcion == 5:
                print("Elegiste cargar dinero")
                print("Ingrese monto, para cancelar ingrese 0")
                monto=Utilidades.ingresar_entero(0,99999)
                if(monto!=0):
                    modificar_dinero_usuario(id_usuario, monto, "Suma", usuarios)
                    fecha_actual=Utilidades.validar_fecha()
                    guardar_transaccion_en_diccionario(id_usuario,transacciones,fecha_actual,"Deposito",monto)

            elif opcion == 6: 
                cantidad_max=0
                for usuario in usuarios:
                    if usuarios[usuario]['cantidad_total_apostada']>cantidad_max:
                        cantidad_max=usuarios[usuario]['cantidad_total_apostada']
                        usuario_mas_aposto=usuarios[usuario]['nombre']
                print(f"El usuario que más dinero apostó hasta la fecha es:",usuario_mas_aposto," y apostó un total de ",cantidad_max," pesos")

            elif opcion == 7:
                ganado_por_usuario={} #diccionario que tiene de clave, el id_usuario y de dato la cantidad ganada 
                for usuario in transacciones:
                    ganado_por_usuario[usuario]=0
                    for transaccion in transacciones[usuario]:
                        if(transaccion[1]=="Gana"):
                            ganado_por_usuario[usuario]+=transaccion[2]
                max=0
                usuario_mas_gano = ""
                max_ganancia=0
                for usuario, ganancia in ganado_por_usuario.items():
                    if ganancia > max_ganancia:
                        max_ganancia = ganancia
                        usuario_mas_gano = usuario
                print("El usuario que más ganó fue:",usuarios[usuario_mas_gano]['nombre']," (mail",usuario_mas_gano,") y ganó un total de:",max_ganancia)
            elif opcion == 8:
                tiene_dinero= verificar_si_usuario_tiene_dinero_suficiente(id_usuario, 1, usuarios) #se le solicita tener al menos 1 peso
                if(equipos !=[] and fixtures!=[]):
                    if (tiene_dinero):
                        print("Bienvenidx al sistema de apuestas")
                        apostar(equipos, fixtures, id_usuario, usuarios, transacciones)
                    else:
                        print("No tenes dinero, debes cargar algo a tu cuenta para poder apostar")
                else:
                    print("Ups... El sistema de apuestas no funciona actualmente, intente de nuevo mas tarde")
            else:
                print("Error desconocido (revisar validación)")
        else:
            finalizar = True
            Manejo_Archivos.guardar_usuarios(usuarios)
            Manejo_Archivos.guardar_transacciones(transacciones)
    print("-"*80)
    print("Hasta pronto")
    print("-"*80)
    
main()