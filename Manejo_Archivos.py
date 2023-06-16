import os
import csv

def obtener_usuarios()-> dict:
    #No recibe nada por parámetro
    #Se encarga de guardar en un diccionario la información del archivo de usuarios
    usuarios:dict = {}
    archivo_usuarios:str = 'usuarios.csv'
    try:
        if os.path.isfile(archivo_usuarios): # si el archivo existe
            with open(archivo_usuarios, 'r', encoding='UTF-8') as archivo_csv: # modo lectura
                csv_reader = csv.reader(archivo_csv, delimiter=',')
                next(csv_reader)
                for row in csv_reader:
                    correo = row[0]
                    usuarios[correo] = {
                        'nombre': row[1],
                        'contrasena': row[2],
                        'cantidad_total_apostada': float(row[3]),
                        'fecha_ultima_apuesta': row[4],
                        'dinero': float(row[5])
                    }
        else:
            with open(archivo_usuarios, 'w', encoding='UTF-8', newline='') as archivo_csv:
                encabezado = ["Correo", "Nombre", "Contraseña", "Cantidad Apostada", "Fecha Última Apuesta", "Dinero"]
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
                if id_usuario not in usuarios:
                    usuarios.append(id_usuario)
                    transacciones[id_usuario] = [[fecha, tipo, importe]]
                else:
                    transacciones[id_usuario].append([fecha, tipo, importe])
    else:
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
        csv_writer.writerow(['id_usuario', 'fecha', 'tipo', 'importe'])  # escribo el encabezado    
        for id_usuario, lista_transacciones in transacciones.items():
            for transaccion in lista_transacciones:
                csv_writer.writerow([
                    id_usuario,
                    transaccion[0], #fecha
                    transaccion[1], #tipo
                    transaccion[2] #importe
                ])
