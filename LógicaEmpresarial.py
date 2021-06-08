"""Contiene la lógica transaccional y de manejo de datos del programa, lo que se definiría como la "lógica empresarial", "inteligencia de negocios".
040621 con respecto a la primera versión:140321
"""
from ast import In
from datetime import datetime
from turtle import undo
import psycopg2
from psycopg2 import sql #Importamos el módulo para composición de cadenas sql, psycopg2.sql, para poder hacer sentencias o proposiciones sql dinámicas, para no tener que hacer las peligrosas concatenaciones con % o +, con lo cual se pueden hacer ataques a la base de datos por medio de inyecciones sql.
from tkinter import messagebox

def ResultadoConsulta(argconnect2, argSQL): 
    "Función que retorna la informacion, resultado de la consulta self.argSQL, en forma de lista de listas del argSQL almacenada en un cursor tipo fetchall, para las operaciones de consulta al navegar por los registros."
    listaDeListas = [] 
    try:
        #Hacemos el cursor con la columna y su respectiva tabla:
        cursorVar = argconnect2.cursor()
        cursorVar.execute(argSQL)  

        #Convertimos las tuplas en listas, para que los resultados sean expresados en lista de listas, y así sirvan para los tksheet de los tickest:
        listaDeTuplascursorSQL = cursorVar.fetchall()
        if listaDeTuplascursorSQL != []:  #Hay por lo menos una tupla en la lista:
            for tupla in listaDeTuplascursorSQL:  
                listaDeListas.append(list(tupla)) #El cast list convierte una tupla en lista.
        resultado = listaDeListas
        #Finalmente cerramos el cursor:
        cursorVar.close()
        return resultado

    except (Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror(message=error, title='Error')
        argconnect2.rollback()

def Actualización_Inserción(argconnect2, listaDeListas, tipoDeOperación, tipoDeVentana, frame):
    """Función que consta de commit para concretar actualizaciones o inserciones de registros en función del tipo de operación y de ventana proporcionados. Note que no tiene return (sólo en el except, para fines de terminación en casos de excepciones)."""
    try:
        varCursor = argconnect2.cursor() 
        
        for lista in listaDeListas:
            if tipoDeVentana == "principal":
                #En este nivel filtramos el tipo de sentencia SQL según el caso:
                if tipoDeOperación == "actualizar":
                    if frame == "mainframe1": varCursor.execute("update consignación set id_cliente = %s, fecha = %s, entregó = %s where no_consignación = %s", (lista[0], lista[1], lista[2], lista[3]))
                    #La lógica de los tksheet en los mainframe2, es que se actualizarán sólo los montos de los ref correspondientes: si modifico el ref, y ese ref existe en otra consignación, se modificará dicho monto de ese ref en esa otra consignación. Para solucionar esto, debo deshabilitar la columna ref de la tabla tickets banco1 o id_cartón en la tabla tickets_cartón_emitidos:
                    if frame == "mainframe2TicketsBanco1": varCursor.execute("update ticket_banco1 set monto = %s where ref = %s", (lista[1], lista[0]))
                    if frame == "mainframe2TicketsCartón": varCursor.execute("update ticket_cartón_recibidos set monto = %s where id_cartón = %s", (lista[1], lista[0]))
                else:
                    #En el caso de que tipo de operación no sea actualizar, si no insertar, pero en la ventana tipo principal. El primer mainframe determina el nuevo no_consignación o id_división, por lo cual hay que obtenerlo para poder tenerlo disponible en los subsiguientes ingresos en ticketbanco1 y cartón. Recuerde que esas columnas son autonuméricas, y no llevan una secuencia fija de paso 1:
                    if frame == "mainframe1": 
                        varCursor.execute("INSERT INTO consignación(id_cliente, fecha, entregó) VALUES(%s, %s, %s)", (lista[0], lista[1], lista[2])) 
                    #La lógica de los tksheet en los mainframe2, es que se actualizarán sólo los montos de los ref correspondientes: si modifico el ref, y ese ref existe, se modificará en el registro dónde esté en consignación o división de tickets. Por eso se debe inhabilitar la columna de ref o idcartón en los tksheets:
                    if frame == "mainframe2TicketsBanco1": varCursor.execute("INSERT INTO ticket_banco1(ref, no_consignación, monto) VALUES(%s, %s, %s)", (lista[0], Último(argconnect2, tipoDeVentana)[-1][0], lista[1]))
                    #Recuerde [-1][0] hace referencia al primer elemento empezando desde el último en la lista Último, y además al primer (y único) elemento en esa tupla.
                    if frame == "mainframe2TicketsCartón": 
                        #Si se van a analizar tuplas en el código contratista, se debe pasar la tupla ya hecha (lista[0],): en el código servidor no se pueden armar tuplas:
                        if DLookUp(argconnect2, "monto", "tickets_cartón_emitidos", "id_cartón", lista[0]) is not None:
                            #note que DLookUp retorna una tupla monomia, por ejemplo (Decimal('2800.00'),) y no utilizamos índice [0] para tomar su valor contenido, 2800, en execute. Supongo que es porque es una tupla monomia, o que indefectiblemente %s posicional tomará el primer valor de una tupla polinómica que se pase:
                            varCursor.execute("INSERT INTO ticket_cartón_recibidos(id_cartón, no_consignación, monto) VALUES(%s, %s, %s)", (lista[0], Último(argconnect2, tipoDeVentana)[-1][0], DLookUp(argconnect2, "monto", "tickets_cartón_emitidos", "id_cartón", lista[0])))
                        else:
                            messagebox.showwarning(message = "El cartón " + lista[0] + " no existe.")
                              
            #En el caso de que tipoVentana sea "secundaria":
            else:
                if tipoDeOperación == "actualizar":
                    if frame == "mainframe1": varCursor.execute("update divisiones_hechas set fecha = %s, punto = %s,  ref_secuencia = %s, monto = %s, id_cliente = %s where id_división = %s", (lista[0], lista[1], lista[2], lista[3], lista[4], lista[5]))
                    if frame == "mainframe2TicketsCartón": varCursor.execute("update tickets_cartón_emitidos set monto = %s where id_cartón = %s", (lista[1], lista[0]))
                else:
                    #En el caso de que tipo de operación en el tipoVentana secundaria, no sea actualizar, si no insertar. El primer mainframe determina el nuevo no_consignación o id_división, por lo cual hay que obtenerlo para los subsiguientes ingresos en ticketbanco1 y cartón. Recuerde que esas columnas son autonuméricas, y no llevan una secuencia fija de paso 1:
                    if frame == "mainframe1": varCursor.execute("INSERT INTO divisiones_hechas(fecha, punto, ref_secuencia, monto, id_cliente) VALUES(%s, %s, %s, %s, %s)", (lista[0], lista[1], lista[2], lista[3], lista[4])) 
                    if frame == "mainframe2TicketsCartón": varCursor.execute("INSERT INTO tickets_cartón_emitidos(id_cartón, id_división, monto) VALUES(%s, %s, %s)", (lista[0], Último(argconnect2, tipoDeVentana)[-1][0], lista[1]))
        
        argconnect2.commit()  #Hacemos la respectiva concreción de la operación y cierre del cursor.
        varCursor.close()
        
    except(Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror(message=error, title='Error') 
        argconnect2.rollback() #El rollback en consignación, produce saltos en el campo no_consignación, que es normal en el tipo serial (automático o autorango), por lo de seguridad en concurrencias de múltiples conexiones. Si es determinante
        #una progresión de números de paso 1, no podrá usar serial: tendrá que meterlas manualmente, o hacer un código a parte para garantizar el paso 1 de forma automática.
        return  #Nos saca a este nivel del procedimiento.  

def conversorListaSencilla(listaDelistas):
    "Retorna una lista con los valores simples únicos contenidos en las listas de listas de un sólo elemento que retorna ResultadoConsulta."
    lista = []
    for elemento in listaDelistas: lista.append(elemento[0])
    return lista

def Último(argconex, tipoVentana):
    try:
        cursorVar = argconex.cursor()
        if tipoVentana == "principal":
            cursorVar.execute("select no_consignación from consignación order by no_consignación asc") 
        else:
            cursorVar.execute("select id_división from divisiones_hechas order by id_división asc") 
    
        lista = cursorVar.fetchall()
        cursorVar.close()
        return lista  #Retorna una lista de tuplas de un sólo elemento que se ve así: [(1,), (2,),...,(n,)]
    except (Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror(message=error, title='Error') 
        argconex.rollback()
        return

def Eliminación(argconnect2, tipoVentana, registro):
    try:
        cursorEliminación = argconnect2.cursor() 
        if tipoVentana == "principal":
            #Como la configuracion de la base de datos está en "actualización y eliminación en cascada", se eliminarán o actualizarán también los registros foráneos en las tablas secundarias.
            #Recuerde que para usar composición de cadena sql de psycopg2, se debe usar tuplas (objeto indizado), y si estas son de un sólo elemento, indefectiblemente hay que acompañar con la coma para indicarle a python que se trata de una tupla:
            cursorEliminación.execute("delete from consignación where no_consignación = %s", (registro,))
        else:
            cursorEliminación.execute("delete from divisiones_hechas where id_división = %s", (registro,))

        argconnect2.commit()  #Hacemos la respectiva concreción de la operación y cierre del cursor. 
        cursorEliminación.close()

    except (Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror(message=error, title='Error') 
        argconnect2.rollback()
        return  

def DLookUp(argConex, imagen, enLaTabla, dominio, valorEspecíficoEnDominio):
    """Retorna un único valor o varios según se use fetchone o fetchall, que se encuentra en la columna imagen (contradominio), la columna monto 
    si hablamos de la tabla tickets_cartón_emitidos, por ejemplo, como imagen del valor independiente específico, valorEspecíficoEnDominio, que 
    es buscado en la columna dominio (conjunto de la variables independientes) de la tabla enLaTabla (cartones_emitidos en nuestro ejemplo), que sería la columna id_cartón. Se expresaría
    de la forma: retorno = f(valorEspecíficoEnDominio). Más específicamente: retorno = f(imagen,enLaTabla,dominio,valorEspecíficoEnDominio) """
    try:
        cursorBusqueda = argConex.cursor() 
        cursorBusqueda.execute(sql.SQL("select {} from {} where {} = %s").format(sql.SQL(imagen), sql.SQL(enLaTabla), sql.SQL(dominio)), (valorEspecíficoEnDominio,))
        #Atención: en una composición de cadena sql, format() tratará solamente las composiciones sql.SQL(), de modo que ellas deben estar dentro de sus paréntesis. Fijese que valorEspecíficoEnDominio es un "literal" en cuanto a 
        #composición de cadenas sql, es por ello que está fuera del format, y debe ponerse en forma de tupla monomia para este case de un sólo valor.
        #Ojo: un select que no encuentra nada y mete su resultado en un fetchone, no lo retorna dentro de una tupla de la forma (None,), como se esperaría, 
        # sino que retorna un None a secas. De tal manera que la expresión cursorBusqueda.fetchone()[0] en caso que no se encuentre ningún valor, 
        # arrojará indefectiblemente el error: 'noneType' object is not subscriptable, puesto que no se puede hacer tal cosa como None[0] (buscar indice en un objeto None).
        valor = cursorBusqueda.fetchone()
        return valor
        
    except (Exception, psycopg2.DatabaseError) as error:
        messagebox.showerror(message=error, title='Error') 
        argConex.rollback()
        return  
