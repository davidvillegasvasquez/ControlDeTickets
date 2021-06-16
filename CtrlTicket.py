"""Interfaz gráfica para la base de datos controltickets. 
        Versión:040621 con respecto a la primera versión:140321.
260521E-1: fue la primera versión encapsulada básica totalmente funcional minimamente.
020621: presenta por primera vez una función dlookup totalmente completa, no parcial."""

import psycopg2
from datetime import datetime
from tkinter import *
from tkinter import ttk
from tksheet import *
from tkinter import messagebox
from LógicaEmpresarial import * 
conexión = None

try:
    raíz = Tk()
    conexión = psycopg2.connect(
        host="localhost", database="controltickets", user="david", password="1234")

    class GeometríaBase:
        "Haremos la clase plantilla, con los atributos comunes a las instancias."
        def __init__(self, argroot, argconnect, argtipoVentana):
            # Primero, definimos los atributos comunes en todas las instancias que se produzcan con esta clase GeometríaBase (que será el común en todas las ventanas que se instancien con esta clase):
            # Definición de variables comunes de control tkinter enlazadas a sus respecivos widgets:
            # Me permite visivilizar la conexión argconnect en todos los miembros de la clase (atributos-métodos y otros).
            self.conexiónParaTodaLaClase = argconnect
            # Enlazada a self.txtBoxFecha (textvariable = self.fecha).
            self.fecha = StringVar()
            # Variable entera que guarda la posición actual en la lista TodosLosNoConsig igual al no_consig. Se puede obviar y usar directamente los métodos .set y .get de la variable de control, pero para evitar esto y hacer el código más eficiente, usamos esta variable-miembro de clase.
            self.posición = 0
            # Variable de control tkinter para el valor del registro de acceso directo.
            self.Ir_a = IntVar(value=1)
            # Variable de control para los subtotales de los tickets Cartón, que es común para las ventanas que se usarán.
            self.SubTotalTicketsCartón = DoubleVar()
            # Enlazada a self.txtBoxIdCliente (textvariable = self.idCliente)
            self.idCliente = StringVar()
            # Su widget estará invisibilizado hasta que se llame a una actualización o inserción de un nuevo registro.
            self.idClienteComboBox = StringVar()
            #tipoOperación guardará la constante simbólica en forma de cadena del tipo de operación que se invocó según el botón de operación pulsado:
            self.tipoDeOperación = None
            self.tipoVentana = argtipoVentana
            self.ventanaParaTodaLaClase = argroot

            # Definición de los widgets comunes:
            # Definimos los cuatro cuerpos principales comunes que conforman la ventana:
            # Creamos el frame común "self.mainframe1" para colocar los widgets con los datos de los widgets particulares de tipoVentana:
            self.mainframe1 = ttk.Frame(self.ventanaParaTodaLaClase)
            # En la columna y fila 0 de argroot.
            self.mainframe1.grid(column=0, row=1, sticky=(N, W, E, S))

            # Creamos el widget común tipo frame identificado como self.mainframe2 que estará en la mitad vertical de la interfaz y servirá para meter las hojas tksheet para visulizar los tickets:
            self.mainframe2 = ttk.Frame(self.ventanaParaTodaLaClase)
            # En la columna 0 y fila 1 de argroot (mitad vertical).
            self.mainframe2.grid(column=0, row=2)

            # El frame común inferior, el que colocamos debajo self.mainframe2, para colocar los botones de navegación:
            # Fijamos la altura en 20 pixeles.
            self.mainframe3 = ttk.Frame(self.ventanaParaTodaLaClase, height=20)
            self.mainframe3.grid(column=0, row=3, sticky=(N, W, E, S))

            # Definimos un cuarto cuerpo o subframe llamada self.mainframe4, y lo metemos dentro de self.mainframe2, al lado de los tk sheet que estarán metidos dentro de un cuaderno (consignación) o canvas (división de tickets), para meter los widgets de los montos parciales de los tickets con su uso de la función agregada sum:
            self.mainframe4 = ttk.Frame(self.mainframe2)
            self.mainframe4.grid(column=1, row=0)

            # Creamos un subframe a parte para los botones de operaciones (actualizar, confirmar, eliminar), self.mainframe5. No pueden ir en mainframe3 porque me deforma los botones que van a encima de ellos (nuevo, confirmar, abortar in), porque compartirían columnas:
            # 20 pixeles es la altura que estamos usando para las filas.
            self.mainframe5 = ttk.Frame(self.ventanaParaTodaLaClase, height=20)
            self.mainframe5.grid(row=4, sticky=NSEW, column=0)
            
            # Tenemos dos widgets comunes para mainframe1 para los casos de consignación y división de tickets: fecha e idCliente. De modo que los colocamos. La fecha la pondremos en la primera fila, segunda columna, e idcliente lo pondremos en la segunda fila, primera columna:
            # Widgets para el campo o columna Fecha:
            ttk.Label(self.mainframe1, text="FECHA").grid(
                column=3, row=1, sticky=NSEW)
            self.txtBoxFecha = ttk.Entry(
                self.mainframe1, width=9, textvariable=self.fecha)
            self.txtBoxFecha.grid(column=4, row=1, sticky=NSEW)
            self.txtBoxFecha['state'] = "readonly"

            # Widgets para el campo o columna IdCLIENTE:
            ttk.Label(self.mainframe1, text="IdCLIENTE").grid(
                column=1, row=2, sticky=NSEW)
            self.txtBoxIdCliente = ttk.Entry(
                self.mainframe1, width=6, textvariable=self.idCliente)
            self.txtBoxIdCliente.grid(column=2, row=2, sticky=NSEW)
            self.txtBoxIdCliente['state'] = 'readonly'

            # El widget común combobox que se visualizará eventualmente para el campo o columna IdCLIENTE cuando se vaya a actualizar o a ingresar nuevos registros:
            # textvariable se actualizará automáticamente con el valor seleccionado en el combobox (genera un evento virtual <<ComboboxSelected>>, cada vez que se selecciona un valor de su lista de valores value, o se introduce un texto en el caso de que se use como combinación entry y listbox.
            self.comboBoxIdCliente = ttk.Combobox(
                self.mainframe1, width=6, textvariable=self.idClienteComboBox)
            self.comboBoxIdCliente.grid(column=2, row=2, sticky=NSEW)
            self.comboBoxIdCliente['state'] = 'readonly'
            self.comboBoxIdCliente.grid_remove()  # Le aplicamos grid_remove: método que lo invisibiliza (el widget existe, está todo el tiempo en mainframe1 pero oculto) y que con grid(), lo volvemos a visibilizar con todos los valores originales en sus atributos. Su estado normal será estar invisible, porque para navegar por los registros, usaremos txtBoxIdCliente para visualizar idCliente.

            # Todos los botones son comunes a los tipos de ventana que se instanciaran, así que ponemos los botones en sus mainframe correspondientes, self.mainframe3 y self.mainframe5, en esta clase GeometríaBase:
            # Colocamos los botones de navegación sobre las consignaciones dentro de self.mainframe3. Como podemos repasar, en los parámetros con nombre, no importa su posición.
            # Usaremos funciones anónimas (lambda) para poder pasar el parámetro "tipoAcción" al método referido, porque usaremos un sólo método para todos los botones de navegación, en plan de racionalizar el código.
            # Los crearemos como atributos de la clase (self.) porque serán manipulados desde atributos-métodos de esta misma clase:
            self.botónPrimer = ttk.Button(
                self.mainframe3, command=lambda: self.BotónPulsado("primero"), text="<<", width=3)
            self.botónPrimer.grid(column=0, row=1, sticky=NSEW)
            self.botónRetro = ttk.Button(
                self.mainframe3, text="<", width=2, command=lambda: self.BotónPulsado("retroceso"))
            self.botónRetro.grid(column=1, row=1, sticky=NSEW)
            self.botónAvance = ttk.Button(
                self.mainframe3, width=2, command=lambda: self.BotónPulsado("avance"), text=">")
            self.botónAvance.grid(column=2, row=1, sticky=NSEW)
            self.botónUltimo = ttk.Button(
                self.mainframe3, text=">>", command=lambda: self.BotónPulsado("último"), width=3)
            self.botónUltimo.grid(column=3, row=1, sticky=NSEW)
            self.botónIrA = ttk.Button(self.mainframe3, text="Ir a:",
                                       command=lambda: self.BotónPulsado("ir_a"), width=3)
            self.botónIrA.grid(column=4, row=1, sticky=NSEW)

            # Como este cuadro de texto no se manipula, no se declara como miembro-atributo de la clase (self.):
            ttk.Entry(self.mainframe3, width=3,
                      textvariable=self.Ir_a).grid(column=5, row=1)

            # Creamos los botones de acción de insertar nuevos registros, modificar y eliminar. Como estos botones
            # invocan métodos específicos de ingreso o deshabilitaciones, no usan funciones anónimas lambda, si no que refieren a procedimientos normales:
            self.botónNuevoRegis = ttk.Button(
                self.mainframe3, text="Nuevo", command=lambda: self.BotónPulsado("nuevo"), width=5)
            self.botónNuevoRegis.grid(column=6, row=1, sticky=NSEW)
            #Recuerde que la invocación del método convencional para command no lleva paréntesis:
            self.botónIngresar = ttk.Button(
                self.mainframe3, text="Confirm", command=self.Insertar, width=7, state=DISABLED) 
            self.botónIngresar.grid(column=7, row=1, sticky=NSEW)
            
            # Metemos los botones de actualización y eliminación en mainframe5:
            self.botónUpdate = ttk.Button(
                self.mainframe5, text="Actualizar", command=lambda: self.BotónPulsado("actualización"), width=9)
            self.botónUpdate.grid(column=1, row=1, sticky=NSEW)
            self.botónEliminar = ttk.Button(
                self.mainframe5, text='Eliminar', command=self.Eliminar, width=7)
            self.botónEliminar.grid(column=3, row=1, sticky=NSEW)
            # Su estado normal es deshabilitado:
            self.botónConfirmUpDate = ttk.Button(
                self.mainframe5, text='ConfirmUpDate', command=self.Actualizar, width=14, state=DISABLED) 
            self.botónConfirmUpDate.grid(column=2, row=1, sticky=NSEW)

            # Ahora, filtramos según tipo ventana con que instanciamos a GeometríaBase, para definir los widgets y las variables de control específicas, no comunes, del tipoVentana:
            if self.tipoVentana == "principal":
                # Variables de control específicas para tipo de ventana consignación:
                self.ventanaParaTodaLaClase.title("CONSIGNACIÓN")
                # Hacemos una lista con todos los valores no_consignación de la tabla consignación. Retornará una lista de listas de un solo elemento de
                # la forma [[1], [2], ...[último no_consig]] que debe convertirse a lista sencilla [1, 2, ...último no_consig] con la función ConversorListaSencilla:
                self.todosLosNo_Consigna = conversorListaSencilla(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select no_consignación from consignación order by no_consignación asc"))
                
                # Enlazada a self.txtBoxNoCONSIG (textvariable = self.no_consig). Inicializamos con el registro de la primera posición:
                self.no_consig = IntVar()
                # Enlazada a self.txtBoxEntregó (textvariable = self.entregó):
                self.entregó = StringVar()
                self.SubTotalTicketsBanco1 = DoubleVar()
                self.TotalTickets = DoubleVar()
                self.TotalTicketsPorcent = DoubleVar()
                
        # Segunda Parte: creación de los widgets y su colocación dentro de la interfaz:
                # Creamos el widget de barra de menú en la interfaz que se situará por defecto en la parte superior, independientemente de los frame que se introduzcan en la raíz tksheet originaria:
                self.barraMenú = Menu(self.ventanaParaTodaLaClase)
                # Con la opción de configuración menu del widget dónde irá el menú (que la interfaz raíz), visibilizamos el menú: es remotamente equivalente al grid.
                # La propiedad menu del widget, en este caso la interfaz raíz, tendrá como valor el menú que instanciamos sobre el, y que apuntamos con el identificador barraMenú.
                self.ventanaParaTodaLaClase['menu'] = self.barraMenú

                # Agregamos los menú a la barra de menú que creamos con el identificador barraMenú:
                # Para aspecto moderno y no desacoplable de los menú, antes de crear cualquiera de ellos, colocamos esta proposición:
                self.ventanaParaTodaLaClase.option_add('*tearOff', FALSE)
                # Creamos el primer menú contenido en barraMenú, apuntado por el identificador operarTablas:
                self.operarTablas = Menu(self.barraMenú)
                # Creamos otro menú que ya veremos que le agregamos. Puede ser versión, ayuda, acerca de, etc.
                self.otrasOperaciones = Menu(self.barraMenú)
                # Agregamos los menú creado en la barra de menú barraMenú.
                self.barraMenú.add_cascade(
                    label="TABLA", menu=self.operarTablas)
                self.barraMenú.add_cascade(
                    label="OTRAS", menu=self.otrasOperaciones)

                # Agregamos los comandos a los menús:
                # Tiene que ser una función-atributo-método convencional porque implica dos proposiciones.
                self.operarTablas.add_command(
                    label="Divisiones Hechas", command=self.EmergenteDivisionesHechas)
                # lambda: GeometríaVentanaTicketCarGenerados(argroot, self.conexiónParaTodaLaClase))
                self.operarTablas.add_command(
                    label="Tickets Cartón Generados", command="")
                self.otrasOperaciones.add_command(
                    command="", label="Comando x")
                self.otrasOperaciones.add_command(label="Comando z")

                # Widgets para el campo o columna Consignación de la base de datos controltickets:
                ttk.Label(self.mainframe1, text="NoCONSGINACIÓN").grid(
                    column=1, row=1, sticky=NSEW)
                # Lo creamos deshabilitado. Como está deshabilitado, no se podrá apreciar el estilo.
                self.txtBoxNoCONSIG = ttk.Entry(
                    self.mainframe1, width=3, textvariable=self.no_consig, state=DISABLED, style="estiloE1.TEntry")
                self.txtBoxNoCONSIG.grid(column=2, row=1, sticky=NSEW)
                # self.txtBoxNoCONSIG['state']="enabled"  #Y con esta proposición la habilitamos. El atributo state de esta clase tiene una lista de tres posibles valores: enabled, disabled y readonly. Fijese que podemos creal el widget con su condición inicial, o asignarla luego, como aquí.

                # Widgets para el campo o columna Entregó:
                ttk.Label(self.mainframe1, text="ENTREGÓ").grid(
                    column=3, row=2, sticky=NSEW)
                self.txtBoxEntregó = ttk.Entry(
                    self.mainframe1, width=9, textvariable=self.entregó)
                self.txtBoxEntregó.grid(column=4, row=2, sticky=NSEW)
                self.txtBoxEntregó['state'] = 'readonly'

                # Y metemos el cuaderno (sin pestañas aún) dentro de self.mainframe2. Como lo referiremos en otros métodos de la clase, debe ser un miembro de la clase, así que lo declaramos con el calificativo self:
                # Como mainframe2 es de tamaño automático, ajustable a los widgets que se le metan, se pondrá de alto a la altura que se le dió al cuaderno (130):
                self.cuaderno = ttk.Notebook(
                    self.mainframe2, height=130, width=200)
                self.cuaderno.grid(column=0, row=0)

                # Creamos, instanciamos los objetos hojas de la clase tksheet, que metemos dentro del cuaderno. Como las hojas son objetos gráficos si van a cambiar, modificadas desde métodos miembros de la clase, se declaran como miembros de la clase (.self):
                self.hojaTicketBanco1 = Sheet(
                    self.cuaderno, column_width=70, align="center", header_align="center")
                self.hojaTicketCartón = Sheet(
                    self.cuaderno, column_width=70, align="center", header_align="center")

                # Y así le modificamos el nombre a los encabezados, con el atributo headers de la clase Sheet:
                # Fíjese que el parámetro imprescindible es la tupla de los nuevos nombres de los encabezados. El nombre de parámetro es opcional en esta caso.
                self.hojaTicketBanco1.headers(newheaders=("REF", "MONTO"))
                # El uso del nombre del parámetro (newheaders) es prescindible. Fijese que esta vez metimos una lista. Es indiferente usar listas o tuplas para ello, siempre y cuando sea un iterable.
                self.hojaTicketCartón.headers(["IdCARTÓN", "MONTO"])

                # Posicionamos las hojas dentro de cuaderno. Si no específicamos nada, las pondrá una al lado de otra en el orden que fueron creadas:
                self.hojaTicketBanco1.grid()
                self.hojaTicketCartón.grid()

                # A vaina loca, metí las hojas de cuaderno al mismo tiempo que las creo agregándolas:
                # Por último metemos las hojas (pestañas) del cuaderno y las apuntamos con identificadores porque las referiremos desde otras partes de programa más tarde:
                self.cuaderno.add(self.hojaTicketBanco1, text='TicketBanco1')
                self.cuaderno.add(self.hojaTicketCartón, text='TicketCartón')

                # Ahora metemos los widgets de los montos parciales por tipo de tickes, y total a transferir por porcentaje (no todos se le cobra el mismo porcentaje) dentro de self.mainframe4:
                # Para los tickets de Banco1:
                ttk.Label(self.mainframe4, text="SubTotalTicketBanco1:").grid(
                    column=1, row=1, sticky=NSEW)
                self.txtBoxTicketBanco1 = ttk.Entry(
                    self.mainframe4, width=10, textvariable=self.SubTotalTicketsBanco1)
                self.txtBoxTicketBanco1.grid(column=1, row=2)
                self.txtBoxTicketBanco1['state'] = "readonly"

                # Para los tickets cartón:
                ttk.Label(self.mainframe4, text="SubTotalTicketCartón:").grid(
                    column=1, row=3, sticky=NSEW)
                self.txtBoxTicketCartón = ttk.Entry(
                    self.mainframe4, width=10, textvariable=self.SubTotalTicketsCartón)
                self.txtBoxTicketCartón.grid(column=1, row=4)
                self.txtBoxTicketCartón['state'] = "readonly"

                # Para el subtotal de todos los tickets:
                ttk.Label(self.mainframe4, text="SubTotalTickets:").grid(
                    column=1, row=5, sticky=NSEW)
                self.txtBoxTotalTicket = ttk.Entry(
                    self.mainframe4, width=10, textvariable=self.TotalTickets)
                self.txtBoxTotalTicket.grid(column=1, row=6)
                self.txtBoxTotalTicket['state'] = "readonly"

                # Para el subtotal de todos los tickets menos el porcentaje:
                ttk.Label(self.mainframe4,
                          text="SubTotalTickets - x%:").grid(column=1, row=7, sticky=NSEW)
                self.txtBoxTicketCartón = ttk.Entry(
                    self.mainframe4, width=10, textvariable="")
                self.txtBoxTicketCartón.grid(column=1, row=8)
                self.txtBoxTicketCartón['state'] = "readonly"

                # Finalmente, le damos los valores contenidos a los widgets, pulsando el botón primer registro:
            if self.tipoVentana == "secundaria":
                # Variables de control específicas para la ventana secundaria, divisiones hechas:
                self.ventanaParaTodaLaClase.title("DIVISIONES HECHAS")
                #Tenemos que obtener la lista de forma ascendente (asc), porque además de usarla para ver cantidad de registros, la necesitamos para obtener el último registro ingresado:
                self.todosLosIdDivisión = conversorListaSencilla(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select id_división from divisiones_hechas order by id_división asc"))
                self.idDivisión = IntVar(value=1)
                self.punto = StringVar()  # Enlazada a self.txtBoxEntregó (textvariable = self.entregó)
                self.puntoComboBox = StringVar()
                self.SubTotalTicketsRecibidos = DoubleVar()
                self.ref_sec = IntVar()
                self.monto = DoubleVar()

                # Definimos sus widgets:
                ttk.Label(self.mainframe1, text="IdDIVISIÓN").grid(
                    column=1, row=1, sticky=NSEW)
                self.txtBoxIdDivisión = ttk.Entry(
                    self.mainframe1, width=3, textvariable=self.idDivisión, state=DISABLED, style="estiloE1.TEntry")
                self.txtBoxIdDivisión.grid(column=2, row=1, sticky=NSEW)

                # Widgets para el campo o columna punto:
                ttk.Label(self.mainframe1, text="PUNTO").grid(
                    column=3, row=2, sticky=NSEW)
                self.txtBoxPunto = ttk.Entry(
                    self.mainframe1, width=9, textvariable=self.punto)
                self.txtBoxPunto.grid(column=4, row=2, sticky=NSEW)
                self.txtBoxPunto['state'] = 'readonly'

                # Widget tipo combobox para el campo punto que aparecerá temporalmente en los procesos de actualización e inserción de nuevos registros en la tabla :
                self.comboBoxPunto = ttk.Combobox(
                    self.mainframe1, width=6, textvariable=self.puntoComboBox)
                self.comboBoxPunto.grid(column=4, row=2, sticky=NSEW)
                self.comboBoxPunto['state'] = 'readonly'
                self.comboBoxPunto.grid_remove()

                # Widgets para el campo o columna ref_sec:
                ttk.Label(self.mainframe1, text="REF/SEC").grid(
                    column=1, row=3, sticky=NSEW)
                self.txtBoxRef_Sec = ttk.Entry(
                    self.mainframe1, width=9, textvariable=self.ref_sec)
                self.txtBoxRef_Sec.grid(column=2, row=3, sticky=NSEW)
                self.txtBoxRef_Sec['state'] = 'readonly'

                # Widgets para el campo o columna monto:
                ttk.Label(self.mainframe1, text="MONTO").grid(
                    column=3, row=3, sticky=NSEW)
                self.txtBoxMonto = ttk.Entry(
                    self.mainframe1, width=9, textvariable=self.monto)
                self.txtBoxMonto.grid(column=4, row=3, sticky=NSEW)
                self.txtBoxMonto['state'] = 'readonly'

                # Atención: Si no meto la hoja dimensionada (height= 200, width = 200),
                # se meterá en el mainframe2, y "estirará" a este con el mayor tamaño prefijado por tksheet. En el caso de consignación no pasa,
                # porque el cuaderno se le dió un tamaño determinado. Recuerde que mainframe2, como cualquier ttk.Frame, se ajusta automáticamente a los widgets que se le metan, al menos que su propiedad grid_propagate esté apagada (False).
                self.hojaTicketCartón = Sheet(
                    self.mainframe2, column_width=70, align="center", header_align="center", height=130, width=200)
                #Note que hay dos tipos de self.hojaTiketsCartón: la de "principal" (consignación), que corresponde a la tabla tickets_cartón_recibidos, y este, a la tabla tickets_cartón_emitidos.
                self.hojaTicketCartón.headers(["IdCARTÓN", "MONTO"])
                self.hojaTicketCartón.grid(column=0, row=0)

                ttk.Label(self.mainframe4, text="SubTotalTicketCartón:").grid(
                    column=0, row=0, sticky=N)
                self.txtBoxTicketCartón = ttk.Entry(
                    self.mainframe4, width=10, textvariable=self.SubTotalTicketsCartón)
                self.txtBoxTicketCartón.grid(column=0, row=1, sticky=N)
                self.txtBoxTicketCartón['state'] = "readonly"

                ttk.Label(self.mainframe4,
                          text="SubTotalTickets - x%:").grid(column=0, row=2, sticky=N)
                self.txtBoxTicketCartón = ttk.Entry(
                    self.mainframe4, width=10, textvariable="")
                self.txtBoxTicketCartón.grid(column=0, row=3)
                self.txtBoxTicketCartón['state'] = "readonly"

    # Cuarta y última parte: definimos los métodos que invocan los botones (tanto los de navegación, como los operativos). En los de navegación adoptamos el enfoque de
    # funciones lambdas en los argumentos command=, que permiten el uso de parámetros, y así poder usar un sólo método para todos los botones de navegación y no repetir n-botones el mísmo código n-veces para actualizar los widgets de datos ttl.Entry de mainframe1 y los tksheet en el cuaderno de pestañas:
    # Para los botones de operación (inserción y actualización), si utilizamos el llamado a procedimientos convencionales python:

        def BotónPulsado(self, *args):
            # print("Imprimir: ", args)  #Fijese como se reciben los valores enviados desde las funciones lambdas
            # en los command. Lo que manda es una tupla de valores, en este caso los botones mandan una tupla de un sólo elemento.
            # De modo que args es una tupla de un sólo elemento, (x, ), por ello para acceder a dicho valor, hay que referenciar con [0].
            # Como python no tiene swicht-case, usamos una seguidilla de if para ver en que posición vamos a poner self.posición, para la consecuente creación de los cursores con las respectivas sentencia sql según la columna no_consignación de la tabla consignación, en función de self.posición:
            # Primero que todo, determinamos todos los valores de la clave principal que recorrerá self.posición, según el tipoVentana:
            if self.tipoVentana == "principal":
                todosLosValores = self.todosLosNo_Consigna
            else:
                todosLosValores = self.todosLosIdDivisión

            # Y ahora aplicamos el condicional que corresponda sobre el tipo de ventana que se determinó arriba, que se está usando aquí:
            if args[0] == "primero":
                # Colocamos self.posición en la primera:
                self.posición = 0

            if args[0] == "retroceso":
                # Condición validadora de que no estamos en la primera posición (self.posición=0).
                if self.posición > 0:
                    # Decrementamos la variable posición para retroceder al registro anterior.
                    self.posición = self.posición-1
                else:
                    pass

            if args[0] == "avance":
                if (self.posición) < len(todosLosValores) - 1:
                    # Incrementamos la variable posición para avanzar al siguiente registro en la tabla.
                    self.posición = self.posición+1
                else:
                    pass

            if args[0] == "último":
                self.posición = len(todosLosValores) - 1

            if args[0] == "ir_a":
                # Colocamos self.posición al registro que queremos acceder directamente:
                if self.Ir_a.get() in todosLosValores:
                    self.posición = todosLosValores.index(self.Ir_a.get())
                else:
                    messagebox.showerror(
                        message="Ese registro no existe.", title='Error')

            # Una vez determinada la posición con los if anteriores, invocamos la función ResultadoConsulta según el tipo de ventana que lo invoca, resultado de la evaluación de los if de arriba, que emulan un swicht-case,
            # Para rellenar los widgets con su información respectiva según el registro en que lo sitúe self.posición:
            if self.tipoVentana == "principal":
                resultConsig = ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select no_consignación, fecha, entregó, id_cliente from consignación where no_consignación = %s" % self.todosLosNo_Consigna[self.posición])[0]  # Tomára el primer registro (la primera lista) de la lista de listas.
                # Le asignamos los valores a las variables de control tkinter del formulario principal de self.mainframe1, según los valores posicionales de la lista ResultadoConsulta:
                self.no_consig.set(resultConsig[0])
                self.fecha.set(resultConsig[1])
                self.entregó.set(resultConsig[2])
                self.idCliente.set(resultConsig[3])
                
                # Recuerde que el método ResultadoConsulta() retorna una lista de listas, que puede ser de una sola lista (consignación), o varias (tickets para los tksheet).
                self.hojaTicketBanco1.set_sheet_data(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select ref, monto from ticket_banco1 where no_consignación = %s" % self.todosLosNo_Consigna[self.posición]))
                self.hojaTicketCartón.set_sheet_data(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select id_cartón, monto from ticket_cartón_recibidos where no_consignación = %s" % self.todosLosNo_Consigna[self.posición]))

                # Procedemos a llenar los subtotales de los tickets. Utilizamos aquí la función agregada sum en la sentencia sql:
                # Recuerde que ResultadoConsulta retorna una lista de listas. [0][0] es el primer y único elemento de la primera y única lista en la lista de listas:
                resulConsulTiketsBanco1 = ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select sum(monto) as total from ticket_banco1 where no_consignación = %s" % self.todosLosNo_Consigna[self.posición])[0][0]
                resulConsulTiketsCartón = ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select sum(monto) as total from ticket_cartón_recibidos where no_consignación = %s" % self.todosLosNo_Consigna[self.posición])[0][0]

                # Posiblemente alguna consignación no tenga ni un ticket de alguno de los tipos de ticket en específico arrojando un None por su ResultadoConsulta. Para evitar el None hay que evaluar primero el resultado y luego asignarlo:
                if resulConsulTiketsBanco1 is None:
                    resulConsulTiketsBanco1 = 0
                if resulConsulTiketsCartón is None:
                    resulConsulTiketsCartón = 0
                self.SubTotalTicketsBanco1.set(resulConsulTiketsBanco1)
                self.SubTotalTicketsCartón.set(resulConsulTiketsCartón)

                # Fijese el tratamiento de las variables de control tkinter para obtener el total de ellos.
                self.TotalTickets.set(
                    self.SubTotalTicketsBanco1.get() + self.SubTotalTicketsCartón.get())

            if self.tipoVentana == "secundaria":
                # Consultamos los datos para los widgets de mainframe1:
                resultDivisionesInicio = ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select id_división, fecha, punto, ref_secuencia, monto, id_cliente from divisiones_hechas where id_división = %s" % self.todosLosIdDivisión[self.posición])[0]
                self.idDivisión.set(resultDivisionesInicio[0])
                self.fecha.set(resultDivisionesInicio[1])
                self.punto.set(resultDivisionesInicio[2])
                self.ref_sec.set(resultDivisionesInicio[3])
                self.monto.set(resultDivisionesInicio[4])
                self.idCliente.set(resultDivisionesInicio[5])

                # Recuerde que ResultadoConsulta retorna una lista de listas, lo que acepta un tksheet.
                self.hojaTicketCartón.set_sheet_data(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select id_cartón, monto from tickets_cartón_emitidos where id_división = %s" % self.idDivisión.get()))

                # Y para el subtotal de los tickets cartones en que se dividió el ticket en iddivisión:
                self.SubTotalTicketsCartón.set(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select sum(monto) as total from tickets_cartón_emitidos where id_división = %s" % self.idDivisión.get())[0][0])

        # Para los botones de operación (inserción y actualización). Recuerde que para preparar los widget para insertar o actualizar, puede ser dentro de los lambda de este método, BotónPulsado:
            if args[0] == "nuevo":
                #Primero establecemos que estamos tratando con una operación de inserción de nuevo registro:
                self.tipoDeOperación = "insertar"
                #Inicializamos los widgets según el tipo de ventana limpiando sus variables de control:
                if self.tipoVentana == "principal":
                    #Note que para borrar el texto en no_consig (analogamente para id división), lo tenemos que setear en 0, puesto que es de tipo entero y se pasa indefectiblemente como argumento a la función Actualizar_Insertar:
                    self.no_consig.set(0)
                    self.entregó.set("")
                    self.hojaTicketBanco1.set_sheet_data(data=[[]])
                    self.hojaTicketCartón.set_sheet_data(data=[[]])
                    # Seteamos los valores de los widget en mainframe4 a cero según el tipoVentana:
                    self.SubTotalTicketsBanco1.set(0)
                    self.SubTotalTicketsCartón.set(0)
                    self.TotalTickets.set(0)
                else:
                    self.idDivisión.set(0)
                    self.ref_sec.set("")
                    self.monto.set(value=0)
                    self.hojaTicketCartón.set_sheet_data(data=[[]])
                    self.SubTotalTicketsCartón.set(0)
                
                self.HabilitarWidgets()
                #Habilitamos el botón de confirmar inserción:
                self.botónIngresar['state'] = 'enabled'
                #Fecha es común al tipo de ventana, así que va fuera del if. Para inserción hacemos un tratamiento específico para fecha. Fijese como meto la fecha actual en formato date de forma automática, y self.fecha que es la variable de control tkinter de la clase StringVar, la toma directamente.
                self.fecha.set(datetime.now().strftime("%Y-%m-%d"))
                self.txtBoxFecha['state'] = 'readonly'
                
            if args[0] == "actualización": 
                self.tipoDeOperación = "actualizar"
                self.HabilitarWidgets()
                self.botónConfirmUpDate['state'] = 'enabled'

        #Definimos lo métodos de actualización e inserción:
        def Actualizar(self, *args):
            "Duré una semana atascado aquí para darme cuenta que tenía que hacer esta definición de método a parte, puesto que estaba usando este método como implementación lambda dentro del método BotónPulsado, y claro, me volvía a poner en la variable de control self.entregó, el valor original que está en la base de datos, puesto que cada vez que se invoca, resulConsigna allá arriba se vuelve a llenar con los valores que están establecidos en la base de datos, y los nuevo en los txtBoxEntregó y txtBoxFecha son volados por estos."
            #self.tipoDeOperación = "actualizar"
            self.Operación()
            self.DeshabilitarWidgets()
            
        def Insertar(self, *args):
            #self.tipoDeOperación = "insertar"
            self.Operación()
            self.DeshabilitarWidgets()
            #Tenemos que actualizar todosLosNoConsigna o todosLosNoIdDivisión según sea el caso:
            if self.tipoVentana == "principal":
                self.todosLosNo_Consigna = conversorListaSencilla(ResultadoConsulta(self.conexiónParaTodaLaClase, "select no_consignación from consignación order by no_consignación asc"))
            else:
                self.todosLosIdDivisión = conversorListaSencilla(ResultadoConsulta(self.conexiónParaTodaLaClase, "select id_división from divisiones_hechas order by id_división asc"))
            #Nos pondrá en el último registro que será el recién ingresado, o el anterior último si no se da la inserción:
            self.BotónPulsado("último")

        def Eliminar(self, *args):
            respuesta = messagebox.askyesno(
                message="Está a punto de eliminar este registro. Si le da a sí, lo borrará irreversiblemente.", title="Borrar Registro")
            if respuesta:
                if self.tipoVentana == "principal":
                    Eliminación(self.conexiónParaTodaLaClase, self.tipoVentana,self.no_consig.get())
                else:
                    Eliminación(self.conexiónParaTodaLaClase, self.tipoVentana,self.idDivisión.get())

            if self.tipoVentana == "principal":
                self.todosLosNo_Consigna = conversorListaSencilla(ResultadoConsulta(self.conexiónParaTodaLaClase, "select no_consignación from consignación order by no_consignación asc"))
            else:
                self.todosLosIdDivisión = conversorListaSencilla(ResultadoConsulta(self.conexiónParaTodaLaClase, "select id_división from divisiones_hechas order by id_división asc"))

            self.BotónPulsado("último")

        def HabilitarWidgets(self, *args):
            "Trabaja conjuntamente con Operación, y posteriormente a este, DeshabilitarWidgets, y es el método que habilita todos los widgets pertinentes para la operación sobre ellos, sea actualización, inserción o eliminación de registros."
            # Deshabilitamos todos los botones de navegación, todos los widgets de mainframe3 o mainframe5 según sea insertar o actualizar:
            for widget in self.mainframe3.winfo_children(): widget['state'] = DISABLED
            for widget in self.mainframe5.winfo_children(): widget['state'] = DISABLED

            if self.tipoDeOperación == "insertar": self.botónNuevoRegis['state'] = DISABLED   
            if self.tipoDeOperación == "actualizar": self.botónUpdate['state'] = DISABLED

            # Habilitamos los widgets comunes. Invisibilizamos self.txtBoxIdCliente y visibilizamos comboBoxIdCliente mientras actualizamos:
            self.txtBoxIdCliente.grid_remove()
            self.txtBoxFecha['state'] = 'enabled'

            # Metemos la lista de idClientes que existen actualmente en al tabla cliente:
            self.comboBoxIdCliente['values'] = conversorListaSencilla(ResultadoConsulta(
                self.conexiónParaTodaLaClase, "select id_cliente from cliente"))
            self.comboBoxIdCliente.grid()
            
            if self.tipoVentana == "principal":
                # Habilitamos los widgets en mainframe1 para este caso:
                self.txtBoxEntregó['state'] = 'enabled'
                # Habilitamos los tksheet:
                self.hojaTicketBanco1.enable_bindings(bindings="all")
                self.hojaTicketCartón.enable_bindings(bindings="all")
                if self.tipoDeOperación == "actualizar":
                    #Con readonly_columns es que se bloquean las columnas. Puede ser un grupo de columnas (lista), referenciadas a partir de 0 para la primera:
                    self.hojaTicketBanco1.readonly_columns(columns = [0], readonly = True, redraw = False)
                    self.hojaTicketCartón.readonly_columns(columns = [0], readonly = True, redraw = False)
                
            if self.tipoVentana == "secundaria":
                # Removemos txtBoxPunto y lo sustituimos temporalmente por comboBoxPunto. Recuerde que ya hicimos lo propio con el combobox común, comboBoxIdCliente, al principio del método:
                self.txtBoxPunto.grid_remove()

                # Metemos la lista de puntos que existen actualmente cuentas:
                self.comboBoxPunto['values'] = conversorListaSencilla(ResultadoConsulta(
                    self.conexiónParaTodaLaClase, "select banco from cuentas"))
                self.comboBoxPunto.grid()

                # Habilitamos los widgets pertinentes de mainframe1:
                self.txtBoxRef_Sec['state'] = 'enabled'
                self.txtBoxMonto['state'] = 'enabled'
                self.hojaTicketCartón.enable_bindings(bindings="all")
                if self.tipoDeOperación == "actualizar": self.hojaTicketCartón.readonly_columns(columns = [0], readonly = True, redraw = False)

        def DeshabilitarWidgets(self, *args):
            "Este es el método para deshabilitar los widgets que se habián habilitado para hacer la operación según el tipo de operaciones y ventana. En pocas palabras, es la función inversa de HabilitarWidgets."
            # Deshabilitamos los widgets en mainframe1, independientemente del resultado de la actualización (procedente, no, cancel o excepción):
            for widget in self.mainframe1.winfo_children(): widget['state'] = 'readonly'
        
            # Rehabilitamos los botones en mainframe3 y mainframe5:
            for widget in self.mainframe3.winfo_children(): widget['state'] = 'enabled'
            for widget in self.mainframe5.winfo_children(): widget['state'] = 'enabled'

            #Haciendo la operación inversa de HabilitarWidgets, remuevo el comboBox común, comboBoxIdCliente, y revisibilizo a txtBoxIdCliente:
            self.comboBoxIdCliente.grid_remove()
            #Para refrescar txtBoxIdCliente, debo actualizar su variable de control, de lo contrario mostrará la que le había asignado antes BotónPulsado (recuerde que ese widget no se toco porque se había removido para darle paso al txtComboboxIdCliente). Igualmente para punto:
            self.idCliente.set(self.idClienteComboBox.get())
            self.txtBoxIdCliente.grid()

            #Para el nó común, si la ventana es de tipo secundaria:
            if self.tipoVentana == "secundaria":
                self.comboBoxPunto.grid_remove()
                self.punto.set(self.puntoComboBox.get())
                self.txtBoxPunto.grid()
            
            #Ahora deshabilitamos los widgets específicos según el tipo de ventana:
            if self.tipoVentana == "principal":
                # Deshabilitamos todos enlaces en los tksheets.
                self.hojaTicketBanco1.disable_bindings()
                self.hojaTicketCartón.disable_bindings()
                #Si se hizo una actulización, hay que volver a habilitar las columnas de tickets banco1 y cartón recibidos (readonly = True):
                if self.tipoDeOperación == "actualizar":
                    #Con readonly_columns es que se bloquean las columnas. Puede ser un grupo de columnas (lista), referenciadas a partir de 0 para la primera:
                    self.hojaTicketBanco1.readonly_columns(columns = [0], readonly = False, redraw = False)
                    self.hojaTicketCartón.readonly_columns(columns = [0], readonly = False, redraw = False)
            if self.tipoVentana == "secundaria": 
                self.hojaTicketCartón.disable_bindings()
                if self.tipoDeOperación == "actualizar":
                    self.hojaTicketCartón.readonly_columns(columns = [0], readonly = False, redraw = False)

            #Por último, deshabilitamos los botones de ejecución de operación, independientemente de cual fue el tipo de operación:
            self.botónIngresar['state'] = DISABLED
            self.botónConfirmUpDate['state'] = DISABLED
    
        def Operación(self, *args):
            "Este método fundamentalmente filtra el tipo de operación, mandando los parámetros pertinentes para ejecutar la operación sql demandada."
            respuesta = messagebox.askyesnocancel("Desea ejecutar la operación?", " Verifique la Entrada")
            if respuesta is not None:
                if respuesta:
                    #Primero, se debe elaborar las listaDelistas que se enviarán segun el caso. Son dos Actualización_Inserción: la de mainframe1, y la de los tksheet en mainframe2 (get_sheet_data):
                    if self.tipoVentana == "principal":
                        Actualización_Inserción(self.conexiónParaTodaLaClase, [[self.idClienteComboBox.get(), self.fecha.get(), self.entregó.get(), self.no_consig.get()]], self.tipoDeOperación, self.tipoVentana, "mainframe1")
                        #Tenemos que validar que hallan datos en las hojas para poder actualizar-insertar en los tksheets de los tickets. Por ahora esta sirve parcialmente, mientras no se escriba y borre en una hoja determinada:
                        if self.hojaTicketBanco1.get_sheet_data()[0] != []:
                            Actualización_Inserción(self.conexiónParaTodaLaClase, self.hojaTicketBanco1.get_sheet_data(), self.tipoDeOperación, self.tipoVentana, "mainframe2TicketsBanco1")
                        if self.hojaTicketCartón.get_sheet_data()[0] != []:
                            Actualización_Inserción(self.conexiónParaTodaLaClase, self.hojaTicketCartón.get_sheet_data(), self.tipoDeOperación, self.tipoVentana, "mainframe2TicketsCartón")
                    else:
                        Actualización_Inserción(self.conexiónParaTodaLaClase, [[self.fecha.get(), self.puntoComboBox.get(), self.ref_sec.get(), self.monto.get(), self.idClienteComboBox.get(), self.idDivisión.get()]], self.tipoDeOperación, self.tipoVentana, "mainframe1")
                        #Como sabemos en el caso de "secundaria", self.hojaTicketCartón será la de divisiones hechas (comparte el mísmo nombre que la de tickets recibidos):
                        if self.hojaTicketCartón.get_sheet_data()[0] != []:
                            Actualización_Inserción(self.conexiónParaTodaLaClase, self.hojaTicketCartón.get_sheet_data(), self.tipoDeOperación, self.tipoVentana, "mainframe2TicketsCartón")

        def EmergenteDivisionesHechas(self, *args):
            # Debo crear el widget toplevel en bruto (cliente) y pasarlo como argumento a la instanciación de la clase GeometríaBase, para que esa instanciación de geometría le de forma al widget de tipo Toplevel pasado. Esa clase es un contratista que hace el trabajo de "peluquear" al widget Toplevel que pasé en bruto.
            self.top = Toplevel(self.ventanaParaTodaLaClase)
            self.top.grab_set()  # El atributo método grab_set, monopoliza todos los eventos en el widget dónde se aplica, convirtiendolo de facto en modal. Esta forma es más concreta para convertir en modal un widget. Lo otro bueno de grab_set() es que al destruir el widget dónde lo apliqué para convertirlo en modal, el resto de las otras ventanas que estén abiertas quedan habilitadas automáticamente,
            # sin tener que crear código adicional para ello. Ojo: si aplico el atributo-método grab_set después de instanciar GeometríaBase para producir nuevaVentana, los widget contenidos en dicha ventana que usan a top como base no se configurarán en grab_set (grab: agarrarse para el sólo toda la atención, inhabilitando todo los demás widget que hayan), dejando que se puedan usar los widget en la ventana principal.
            # Y he aquí la magia de la autoinstanciación o instanciación recursiva:
            # Si no apunto-referencio la nueva instancia de widget de la clase GeometríaBase, no se visibilizará. Es por ello que el vscode no me lo subraya como "variable no utilizada", independientemente de que no invoque su atributo-metodo BotónPulsado allá abajo.
            self.nuevaVentana = GeometríaBase(
                self.top, self.conexiónParaTodaLaClase, "secundaria")
            # Y claro, la nueva instancia la inicializamos en la primera posición:
            self.nuevaVentana.BotónPulsado("primero")

    # Finalmente creamos una primera y definitiva o última instancia "de arranque" y que durará toda la vida de la ejecución del programa, instanciando la clase GeometríaBase para comenzar:
    ventana = GeometríaBase(raíz, conexión, "principal")
    # A esa primera instancia, le invocamos su método BotónPulsado en primera posición para obtener los datos de las variables de control en los widgets, del primer registro en la tabla consignación ("principal"):
    ventana.BotónPulsado("primero")
    raíz.mainloop()

except (Exception, psycopg2.DatabaseError) as error:
    # Note como se le agrega texto al mensage del messagebox.
    messagebox.showerror(message=str(
        error)+"Problemas en la conexión, el programa se cerrará.", title='Error')

# Si se logró conectar, cerrar la conexión antes de terminar el programa:
if conexión is not None:
    conexión.close()
print("Conexión cerrada...chau.")
# 110521: 687 líneas. Será que logro llevarlas a la mitad? R:Eso no será posible, porque estoy condensando todo el código en una sóla clase, lo cual la hará más grande, pero el código global entre todos los módulos será mucho menor a la mitad.
