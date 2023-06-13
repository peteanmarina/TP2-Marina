import os
import requests
from passlib.context import CryptContext
import csv
import random
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tempfile
#clave prestada del profe: b954d11d14d63f5c19f0eeb8953724c3
#mi clave: 

def ingresar_entero(min: int, max: int)->int:
    #Funcion que recibe un numero número mínimo y uno máximo y permite al usuario ingresar valores hasta que uno sea entero y se encuentre en el rango númerico indicado por esos números
    #Devuelve un entero, ingresado por el usuario
    número=input()
    while (not número.isdigit() or int(número)>max or int(número)<min):
        #Si la primera condicion se cumple, no lee las que siguen y por eso ya puedo convertirlo a int
        print(f"ERROR. Intente de nuevo, recuerde que debe ser un número entero entre {min} y {max}")
        número=input()
        
    return int(número)

def obtener_usuarios()-> dict:
    #Se encarga de guardar en un diccionario la información del archivo de usuarios
    usuarios = {}
    archivo_usuarios = 'usuarios.csv'
    
    if os.path.isfile(archivo_usuarios): # si el archivo existe
        with open(archivo_usuarios, 'r', encoding='UTF-8') as archivo_csv: # modo lectura
            csv_reader = csv.reader(archivo_csv, delimiter=',')
            next(csv_reader)  # Leer la primera línea (encabezado)
            for row in csv_reader:
                correo = row[0]
                usuarios[correo] = {
                    'nombre': row[1],
                    'contrasena': row[2],
                    'cantidad_total_apostada': float(row[3]),
                    'fecha_ultima_apuesta': row[4],
                    'dinero': float(row[5])
                }
    return usuarios

def guardar_usuarios(usuarios):
    #Reescribe el archivo usuarios con el contenido actualizado presente en el diccionario usuarios
    with open('usuarios.csv', 'w', newline='', encoding='UTF-8') as archivo_csv:
        csv_writer = csv.writer(archivo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['correo', 'nombre', 'contrasena', 'cantidad_total_apostada', 'fecha_ultima_apuesta', 'dinero'])  # Escribir el encabezado
        
        for correo, datos in usuarios.items():
            csv_writer.writerow([
                correo,
                datos['nombre'],
                datos['contrasena'],
                datos['cantidad_total_apostada'],
                datos['fecha_ultima_apuesta'],
                datos['dinero']
            ])

def registrar_usuario(usuarios)-> str: #TODO validar mail no repetido
    #permite guardar un nuevo usuario en el diccionario de usuarios, siempre y cuando el main no exista en el mismo
    #devuelve 0 si el mail ya existe
    myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])

    correo = input("Ingrese correo electrónico: ")

    if(correo in usuarios):
        print("Ya existe un usuario registrado con ese correo")
        correo=0
    else:
        nombre = input("Ingrese su nombre de usuario:")
        contrasena = myctx.hash(input("Ingrese su contraseña: "))
        dinero = float(input("Ingrese el dinero disponible:"))
        usuarios[correo] = {
            'nombre': nombre,
            'contrasena': contrasena,
            'cantidad_total_apostada': 0, #apostada hasta el momento
            'fecha_ultima_apuesta': None, #de la ultima apuesta
            'dinero': dinero
        }
        print("Registro realizado")

    return correo 

def iniciar_sesion(usuarios:dict) -> str:
    #recibe el diccionario de usuarios y permite que un usuario se identifique, siempre que exista y ingrese su contraseña correctamente
    #devuelve 0 si
    myctx = CryptContext(schemes=["sha256_crypt", "md5_crypt"])
    myctx.default_scheme()
    correo = input("Ingrese su correo electrónico:")
    contrasena = input("Ingrese su contraseña: ")

    if correo in usuarios:
        if(myctx.verify(contrasena, usuarios[correo]['contrasena'])):
            print("Inicio de sesión realizado")
        else:
            print("Contraseña incorrecta")
            correo=0
    else:
        print("No hay ninguna cuenta con ese mail")
        correo=0

    return correo

def mostrar_menu():
    print("Ingrese el número correspondiente a la opción que desee:")
    print("0) Salir")
    print("1) Mostrar el plantel completo de un equipo ingresado")
    print("2) Mostrar la tabla de posiciones de la Liga profesional de una temporada")
    print("3) Información sobre el estadio y escudo de un equipo")
    print("4) Goles y los minutos en los que fueron realizados para un equipo")
    print("5) Cargar dinero en cuenta de usuario") 
    print("6) Usuario que más apostó") 
    print("7) Usuario que más gano")
    print("8) Apostar")
    
def ejecutar_accion(opcion:str, equipos:dict, fixtures: dict, jugadores:dict, id_usuario:str, usuarios:dict, transacciones:dict):
    if opcion == "1": 
        print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
        mostrar_equipos(equipos)
        id=0
        while(id==0):
            print("Ingrese nombre del equipo que desee ver el plantel")
            equipo_elegido=input()
            id= obtener_id_equipo(equipos, equipo_elegido)
        mostrar_plantel(id, jugadores)

    elif opcion == "2":
        print("Ingrese la temporada (el anio) de la cual desea ver la tabla de posiciones(junto a otras stats): ")
        temporada:int = input("Temporada: ")
        mostrar_tabla_posiciones(temporada)

    elif opcion == "3":
        print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
        mostrar_equipos(equipos)
        id=0
        while(id==0):
            print("Ingrese nombre del equipo que desee ver la información sobre el estadio y su escudo")
            equipo_elegido= input()
            id=obtener_id_equipo(equipos, equipo_elegido)
        mostrar_informacion_estadio_y_escudo(id, equipos)

    elif opcion == "4":
        pass

    elif opcion == "5":
        confirmacion = input("¿Desea cargar dinero a cuenta? (S/N)").lower()
        if confirmacion == "s":
            print("Ingrese monto a agregar")
            monto=ingresar_entero(1,99999)
            modificar_dinero_usuario(id_usuario, monto, "Sumar", usuarios)

    elif opcion == "6": 
        print ("Usuario que más apostó:")
        cantidad_max=0
        for usuario in usuarios:
            if usuario['cantidad_total_apostada']>cantidad_max:
                cantidad_max=usuario['cantidad_total_apostada']
                usuario_mas_aposto=usuario['nombre']
        print(f"El usuario que más dinero apostó hasta la fecha es ",usuario_mas_aposto)

    elif opcion == "7":
        print ("Usuario que más gano:")
        for usuario in transacciones:
            pass
    elif opcion == "8":
        print("Bienvenidx al sistema de apuestas")
        apostar(equipos, fixtures, id_usuario, usuarios, transacciones)

    else:
        print("Error, intente nuevamente (recuerde que debe ingresar un número)")

def apostar(equipos:dict, fixtures: dict, id_usuario:int, usuarios:dict, transacciones:dict):
    print("Equipos de la Liga Profesional correspondiente a la temporada 2023:")
    mostrar_equipos(equipos)
    print("Ingrese nombre de un equipo para ver un listado del fixture")
    equipo_elegido= input()
    id_equipo= obtener_id_equipo(equipos, equipo_elegido)
    informacion_partidos={}
    for partido in fixtures:
        if(partido["teams"]["home"]["id"]==id_equipo or partido["teams"]["away"]["id"]==id_equipo):
            id_partido=partido['fixture']['id']
            local = partido["teams"]["home"]["name"]
            visitante = partido["teams"]["away"]["name"]
            pago_local= partido['teams']['home']['cantidad_veces_pago']
            pago_visitante= partido['teams']['away']['cantidad_veces_pago']
            fecha,hora = partido["fixture"]["date"].split('T')
            informacion_partidos[fecha]=[local, visitante, pago_local, pago_visitante, id_partido]
            print()
            print(f"Para la fecha: ",fecha)
            print(f"Equipo local:", local)
            print(f"Equipo visitante:", visitante)
            
    print("Ingrese la fecha del partido para el que quiere apostar, YYYY-MM-DD")
    fecha= validar_fecha()

    equipo_win_or_draw= obtener_win_or_draw(informacion_partidos[fecha][4])

    if(equipo_win_or_draw == informacion_partidos[fecha][0]):
        informacion_partidos[fecha][2]=informacion_partidos[fecha][2]*10/100
    elif(equipo_win_or_draw == informacion_partidos[fecha][1]):
        informacion_partidos[fecha][3]=informacion_partidos[fecha][3]*10/100
    else:
        print("Se produjo un error al reconocer win_or_draw")

    print(f"Equipo local:", informacion_partidos[fecha][0], "paga: ",informacion_partidos[fecha][2],"veces de lo apostado")
    print(f"Equipo visitante:", informacion_partidos[fecha][1],"paga: ",informacion_partidos[fecha][3],"veces de lo apostado")

    print("Ingrese el monto a apostar")
    monto= input()
    dinero_suficiente= verificar_si_usuario_tiene_dinero_suficiente(id_usuario, monto)

    if (dinero_suficiente):
        print("Ahora le solicitaremos la fecha del día de hoy")
        fecha_actual=validar_fecha()
        print("Descontando dinero...")
        registrar_apuesta_en_usuario(id_usuario, monto, fecha_actual, usuarios)#actualiza fecha ultima apuesta y suma monto al total apostado
        modificar_dinero_usuario(id_usuario, monto, "Restar")

        print("1)Gana Local")
        print("2)Empate")
        print("3)Gana Visitante")

        respuesta=ingresar_entero(1,3)

        #la lógica del pago fue aprobada por un profesor
        if(respuesta==1):  
            monto+=(informacion_partidos[fecha][2]*monto)
        elif(respuesta==3):
            monto+=(informacion_partidos[fecha][3]*monto)
        else:#empate, ver que hacer TODO
            pass

        resultado_simulado=random.randint(1, 3)
        
        if(resultado_simulado==1):
            print("Gana Local")
        elif(resultado_simulado==2):
            print("Empate")
        else:
            print("Gana visitante")

        if(resultado_simulado==respuesta):
            #gana el usuario
            guardar_transaccion_en_diccionario(id_usuario, transacciones, fecha_actual, "Gana", monto)
            modificar_dinero_usuario(id_usuario, monto, "Sumar")
        else: #pierde
            print("Perdiste... mejor suerte la próxima")
        #informacion_partidos[fecha]=(local, visitante, pago_local, pago_visitante, id_partido)
    else:
        print("Lamento informarle que no tiene dinero suficiente para realizar esta apuesta")

def registrar_apuesta_en_usuario(id_usuario, monto, fecha, usuarios):
    
    usuarios[id_usuario]['cantidad_total_apostada']+=monto
    usuarios[id_usuario]['fecha_ultima_apuesta']+=monto


def obtener_win_or_draw(partido)-> str: #tengo que hacer una consulta si o si por partido, no puedo guardarme todas
    url = "https://v3.football.api-sports.io/predictions"
    params = {
        "fixture":partido
    }
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "780851d3b9e161c8b5dddd46f9e9da9a"
    }
    equipo_win_or_draw:str=""
    respuesta = requests.get(url, params=params, headers=headers)

    if respuesta.status_code == 200:
        data = respuesta.json()
        prediccion = data['response']
        equipo_win_or_draw = prediccion[0]['predictions']["winner"]["name"]
    else:
        print("Error en la solicitud:", respuesta.status_code)
    return equipo_win_or_draw

def obtener_transacciones()->dict:
    transacciones = {}
    archivo_transacciones = 'transacciones.csv'
    usuarios=[]
    if os.path.isfile(archivo_transacciones): # si el archivo existe
        with open(archivo_transacciones, 'r', encoding='UTF-8') as archivo_csv: # modo lectura
            csv_reader = csv.reader(archivo_csv, delimiter=',')
            next(csv_reader)  # Leer la primera línea (encabezado)
            for fila in csv_reader:
                id_usuario = fila[0]
                fecha = fila[1]
                tipo = fila[2]
                importe = float(fila[3])

                if id_usuario not in usuarios:
                    usuarios.append(id_usuario)
                    transacciones[id_usuario] = [[fecha, tipo, importe]]
                else:
                    transacciones[id_usuario].append([fecha, tipo, importe])

    return transacciones

def guardar_transaccion_en_diccionario(id_usuario:str, transacciones:dict, fecha_actual:str, tipo:str, monto:float):
    transaccion = [fecha_actual, tipo, monto]
    if id_usuario in transacciones:
        # usuario ya tiene transacciones
        transacciones[id_usuario].append(transaccion)
    else:
        # usuario no tiene transacciones
        transacciones[id_usuario] = [transaccion]

def guardar_transacciones(transacciones):
    print(transacciones)
    with open('transacciones.csv', 'w', newline='', encoding='UTF-8') as archivo_csv:
        csv_writer = csv.writer(archivo_csv, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
        csv_writer.writerow(['id_usuario', 'fecha', 'tipo', 'importe'])  # escribo el encabezado    
        for id_usuario, lista_transacciones in transacciones.items():
            for transaccion in lista_transacciones:
                csv_writer.writerow([
                    id_usuario,
                    transaccion[0], #fecha
                    transaccion[1], #tipo
                    transaccion[2] #importe
                ])

def modificar_dinero_usuario(id_usuario:str, monto:float, operación:str, usuarios:dict):
    
    if id_usuario in usuarios:
        dinero_en_cuenta = float(usuarios[id_usuario]['dinero'])
        if(operación=="Sumar"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta + float(monto)
        elif(operación=="Restar"):
            usuarios[id_usuario]["dinero"] = dinero_en_cuenta - float(monto)
        else:
            print("Error al reconocer operación")

    print (f"Ahora posee {usuarios[id_usuario]['dinero']} disponible en su cuenta. ")


def verificar_si_usuario_tiene_dinero_suficiente(id_usuario, monto)->bool:
    archivo_usuarios = 'usuarios.csv'
    usuarios = {}

    if os.path.isfile(archivo_usuarios):
        with open(archivo_usuarios, 'r', encoding='UTF-8') as archivo_csv:
            csv_reader = csv.reader(archivo_csv, delimiter=',')
            next(csv_reader)
            for row in csv_reader:
                correo = row[0]
                usuarios[correo] = {
                    'dinero': float(row[5])
                }
    dinero_suficiente= False
    if id_usuario in usuarios:
        dinero = float(usuarios[id_usuario]['dinero'])
        if dinero >= float(monto):
            dinero_suficiente= True
    return dinero_suficiente

def obtener_cantidad_de_veces()->int:
    cantidad_veces=random.randint(1, 4)
    return cantidad_veces

def mostrar_plantel(id_equipo:int, jugadores:dict)->None:
    for jugador in jugadores:
        if(jugador['statistics'][0]['team']['id']==id_equipo):
            print(jugador['player']['name'])

def obtener_equipos()->dict:
    url = "https://v3.football.api-sports.io/teams"
    params = {
        "league": "128",
        "country": "Argentina",
        "season": 2023
    }
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "780851d3b9e161c8b5dddd46f9e9da9a"
    }
    
    # solicito los equipos de la liga argentina
    respuesta = requests.get(url, params=params, headers=headers)
    equipos={}
    # verifico estado de la solicitud
    if respuesta.status_code == 200: #si fue exitosa
        data = respuesta.json()
        equipos = data['response']        
    else:
        print("Error en la solicitud:", respuesta.status_code)
    return equipos

def mostrar_informacion_estadio_y_escudo(id_equipo, equipos):
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

    enlace_imagen = equipo_elegido['logo']
    response = requests.get(enlace_imagen)
    # guardo la imagen temporalmente
    with tempfile.NamedTemporaryFile(delete=False) as imagen_temporal:
        imagen_temporal.write(response.content)
        nombre_imagen_temporal = imagen_temporal.name
    # Cargar la imagen desde el archivo temporal
    imagen = mpimg.imread(nombre_imagen_temporal)
    # Mostrar la imagen
    plt.imshow(imagen)
    plt.show()
    os.remove(nombre_imagen_temporal)

def mostrar_tabla_posiciones(temporada)->dict: #temporada es año
    url = "https://v3.football.api-sports.io/standings"
    params = {
        "league": "128",
        "season": temporada
    }
    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "780851d3b9e161c8b5dddd46f9e9da9a"
    }
    respuesta = requests.get(url, params=params, headers=headers)
    posiciones={}
    if respuesta.status_code == 200: #si fue exitosa
        data = respuesta.json()
        posiciones = data['response']
        print("Posicion---Equipo---Pts---P.J---P.G---P.E---P.P")
        if(len(posiciones)>0):
            for equipo in range(len(posiciones[0]['league']['standings'][0])):
                print(posiciones[0]['league']['standings'][0][equipo]['rank'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['team']['name'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['points'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['all']['played'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['all']['win'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['all']['draw'],"-"*3,posiciones[0]['league']['standings'][0][equipo]['all']['lose'])
    else:
        print("Error en la solicitud:", respuesta.status_code)


def obtener_jugadores()->dict:
    url = "https://v3.football.api-sports.io/players"
    params = {
        "league": "128",
        "season": 2023
    }

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "780851d3b9e161c8b5dddd46f9e9da9a"
    }
    
    # solicito equipo indicado por parametro
    respuesta = requests.get(url, params=params, headers=headers)
    jugadores={}
    # verifico estado de la solicitud
    if respuesta.status_code == 200: #si fue exitosa
        data = respuesta.json()
        jugadores = data['response']
    else:
        print("Error en la solicitud:", respuesta.status_code)
    return jugadores


def obtener_fixtures()->dict:
    url = "https://v3.football.api-sports.io/fixtures"
    params = {
        "league": "128",
        "season": 2023
    }

    headers = {
        'x-rapidapi-host': "v3.football.api-sports.io",
        'x-rapidapi-key': "780851d3b9e161c8b5dddd46f9e9da9a"
    }
    
    # solicito equipo indicado por parametro
    respuesta = requests.get(url, params=params, headers=headers)
    # verifico estado de la solicitud
    fixture={}
    if respuesta.status_code == 200: #si fue exitosa
        data = respuesta.json()
        fixture = data['response']
        for partido in fixture:
            partido['teams']['home']['cantidad_veces_pago'] = obtener_cantidad_de_veces()
            partido['teams']['away']['cantidad_veces_pago'] = obtener_cantidad_de_veces()
    else:
        print("Error en la solicitud:", respuesta.status_code)
    return fixture

def validar_fecha()->int:
    fecha_invalida=True
    fecha=0
    while(fecha_invalida):
        fecha_invalida=False
        print("Ingrese fecha")
        fecha=input()
        partes = fecha.split('-')

        if ((len(partes) != 3)) or ((len(partes[0]) != 4) or (len(partes[1]) != 2) or (len(partes[2]) != 2)):
            fecha_invalida=True

        if ((not partes[0].isnumeric()) or (not partes[1].isnumeric()) or (not partes[2].isnumeric())):
            fecha_invalida=True
        else:
            anio = int(partes[0])
            mes = int(partes[1])
            dia = int(partes[2])
            if ((anio < 1) or (mes < 1) or (mes > 12) or (dia < 1) or (dia > 31)):
                fecha_invalida=True

    return fecha

def mostrar_equipos(equipos):
    for equipo in equipos:
        print(equipo['team']['name'])

def obtener_id_equipo(equipos, equipo_elegido)->str:
    #devuelve 0 si no se encuentra
    id=0
    for equipo in equipos:
        if(equipo_elegido) == (equipo['team']['name']):
            id=equipo['team']['id']
    return id

def main():   
    print("Bienvenidx al portal de apuestas Jugarsela")
    usuarios:dict=obtener_usuarios()
    transacciones:dict=obtener_transacciones()
    fixtures:dict= obtener_fixtures()
    equipos:dict= obtener_equipos()
    jugadores:dict=obtener_jugadores()
    
    finalizar = False

    id_usuario:str= 0
    while (id_usuario==0 and not finalizar): #mientras que no se identifique y no decida salir
        print("1)Iniciar sesión")
        print("2)Registrarse")
        print("3)Salir")
        respuesta:int=int(ingresar_entero(1,3))
        if(respuesta == 1):
            id_usuario = iniciar_sesion(usuarios)
        elif(respuesta == 2):
            id_usuario= registrar_usuario(usuarios)
        elif(respuesta == 3):
            finalizar= True
    
    while not finalizar:
        mostrar_menu()
        opcion = input()
        if opcion!= "0":
            ejecutar_accion(opcion, equipos, fixtures, jugadores ,id_usuario, usuarios, transacciones)
        else:
            finalizar = True
            guardar_usuarios(usuarios)
            guardar_transacciones(transacciones)
    
    print("Hasta pronto")

main()