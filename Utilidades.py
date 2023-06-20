import random

def ingresar_entero(min: int, max: int)->int:
    #Funcion que recibe un numero mínimo y uno máximo y permite al usuario ingresar valores hasta que uno sea entero y se encuentre en el rango númerico indicado por esos números
    #Devuelve un entero, ingresado por el usuario
    numero:str=input()
    while (not numero.isdigit() or int(numero)>max or int(numero)<min):
        #Si la primera condici/on se cumple, no lee las que siguen y por eso ya puedo convertirlo a int
        print(f"ERROR. Intente de nuevo, recuerde que debe ser un numero entero entre {min} y {max}")
        numero=input()
    return int(numero)

def ingresar_float(min: float, max: float) ->float:
    #Funcion que recibe un numero float mínimo y uno máximo y permite al usuario ingresar valores hasta que uno sea float y se encuentre en el rango númerico indicado por esos números
    #Devuelve un float, ingresado por el usuario
    numero:str=""
    invalido=True
    while(invalido):
        try:
            numero=float(input())
            if(float(numero)>max or float(numero)<min):
                invalido=True
                print("Intente nuevamente. Recuerde que el número debe encontrarse entre ",min, " y ",max)
            else:
                invalido=False
        except:
            print("Intente nuevamente. Recuerde ingresar un número")
            numero=""
    return float(numero)
   
def ingresar_email()->str:
    #No recibe nada por parámetro
    #Permite ingresar un mail hasta que tenga una @ y un punto y lo devuelve
    email_valido=False
    while not email_valido:
        print("Ingrese su email")
        email=input()
        if (("@" in email) and ("." in email)):
            separado_por_arroba = email.split("@")
            if (len(separado_por_arroba) == 2):
                separado_por_punto = separado_por_arroba[1].split(".")
                if len(separado_por_arroba) >= 2:
                    email_valido= True
        else:
            print("Parece que lo que ingresaste no es un email...")
    return email

def validar_fecha()->int:
    #No recibe nada por parametro
    #Devuelve una fecha validada, formato YYYY-MM-DD
    fecha_invalida=True
    fecha=0
    while(fecha_invalida):
        fecha_invalida=False
        print("Ingrese una fecha válida")
        fecha=input()
        print("-"*80)
        partes = fecha.split('-')

        if ((len(partes) != 3)) or ((len(partes[0]) != 4) or (len(partes[1]) != 2) or (len(partes[2]) != 2)):
            fecha_invalida=True
        else:
            if ((not partes[0].isnumeric()) or (not partes[1].isnumeric()) or (not partes[2].isnumeric())):
                fecha_invalida=True
            else:
                anio = int(partes[0])
                mes = int(partes[1])
                dia = int(partes[2])
                if ((anio < 1) or (mes < 1) or (mes > 12) or (dia < 1) or (dia > 31)):
                    fecha_invalida=True
    return fecha

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