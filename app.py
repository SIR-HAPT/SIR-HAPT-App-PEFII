'''
SIR-HAPT - Aplicación para la gestión terapéutica
Autora: Alma Cristina Villanueva Guzmán
PEF - Ingeniería Biomédica
'''
# Instalar librerias
import os
import sys
from datetime import datetime

# KV
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.core.window import Window

# Para graficar
import matplotlib
matplotlib.use("Agg")  # Backend no interactivo, evita conflictos con Kivy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (registra el proyector 3D)
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import numpy as np
 
# Firebase Auth y Firestore
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

# Obtiene la ruta absoluta tanto en desarrollo como en ejecutable
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # Cuando corre como .exe
    except Exception:
        base_path = os.path.abspath(".")  # Cuando corre como script

    return os.path.join(base_path, relative_path)

# Ruta dinámica al JSON
# Para usuarios de prueba voluntarios sanos
px_cred_path = resource_path("sir-hapt-firebase-adminsdk-fbsvc-baadfe4250.json")
# Para pruebas en ADACEA, pacientes
users_cred_path = resource_path("serviceAccountKey_mrgame-pefii-v2-firebase-adminsdk.json")


# Inicializar credenciales
cred = credentials.Certificate(users_cred_path) # Seleccionar la credencial de la nube que se quiere visualizar
firebase_admin.initialize_app(cred)

db = firestore.client()

# Configuración Firebase Auth (Pyrebase) 
firebaseConfig = {
    "apiKey": "AIzaSyDdi_cAzbF_baiat6cKyakbzgiosFLX5a0",
    "authDomain": "sir-hapt.firebaseapp.com",
    "projectId": "sir-hapt",
    "storageBucket": "sir-hapt.firebasestorage.app",
    "messagingSenderId": "851859226117",
    "appId": "1:851859226117:web:a003792b111bfdd617266c",
    "databaseURL": ""
}
firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# =================================================================
# ======= INICIO DE SESION ========================================
# =================================================================
class LogIn(MDScreen):

    # Inicia sesión con Firebase
    def login(self):
        email = self.ids.user.text.strip() 
        password = self.ids.password.text   

        if not email or not password:
            self.show_message("Por favor, complete todos los campos")
            return

        try:
            auth.sign_in_with_email_and_password(email, password)
            app = MDApp.get_running_app()
            app.user_email = email
            print(f"Email guardado en app: {email}") 

            # Mensaje en verde de inicio correcto
            self.show_message("Inicio de sesión realizado correctamente", color=self.theme_cls.primary_color) 
            print(f"Usuario autenticado: {email}")
            
            # Cambiar a pantalla Dashboard
            Clock.schedule_once(lambda dt: self.go_to_dashboard(), 2)
            
        except Exception as e:
            error_message = self.firebase_error(str(e))
            self.show_message(f"{error_message}")
            print(f"Error de login: {e}")

    def register_user(self):
        # Registra nuevo usuario en Firebase
        email = self.ids.user.text.strip()
        password = self.ids.password.text

        if not email or not password: # Validacion de campos
            self.show_message("Por favor, complete todos los campos")
            return
        
        if len(password) < 6:
            self.show_message("La contraseña debe tener al menos 6 caracteres")
            return

        try:
            auth.create_user_with_email_and_password(email, password)
            # Almacenar ID en firestore
            IDTerapeuta = self.ids.user.text.split("@")[0]

            # Datos a almacenar
            data_terapeuta = {
                "nombre": "Ingresar nombre",
                "correo": email,
                "pacientes_asignados": []  # lista vacía inicial
            }
            db.collection("Terapeutas").document(IDTerapeuta).set(data_terapeuta)

            self.show_message(
                "Usuario registrado exitosamente, inicie sesión", 
                color=self.theme_cls.primary_color
            )
            print(f"Usuario registrado: {email}")
            
        except Exception as e:
            error_message = self.firebase_error(str(e))
            self.show_message(f"{error_message}")
            print(f"Error de registro: {e}")
    
    def forgot_password(self):
        email = self.ids.user.text.strip()

        if not email:
            self.show_message("Ingresa un correo electrónico.")
            return

        try:
            auth.send_password_reset_email(email)
            self.show_message("Se envió un correo para restablecer contraseña")
            
        except Exception as e:
            print("Error:", e)
            self.show_message("No se pudo enviar el correo. Verifica el email.")

    def firebase_error(self, error_str):
        # Convertir errores de Firebase en mensajes cortos
        error_map = {
            "INVALID_EMAIL": "Correo electrónico inválido",
            "EMAIL_NOT_FOUND": "Usuario no encontrado",
            "INVALID_PASSWORD": "Contraseña incorrecta",
            "USER_DISABLED": "Usuario deshabilitado",
            "EMAIL_EXISTS": "El correo ya está registrado",
            "WEAK_PASSWORD": "Contraseña muy débil (mínimo 6 caracteres)",
            "INVALID_LOGIN_CREDENTIALS": "Credenciales inválidas",
        }
        
        for key, message in error_map.items():
            if key in error_str:
                return message
        
        return "Error de conexión. Intente nuevamente"
    
    def show_message(self, message, color= None):
        # Muestra mensaje en warning_label
        if color is None:
            color = self.theme_cls.text_color

        warning_label = self.ids.warning_label
        warning_label.text = message
        warning_label.theme_text_color = "Custom"
        warning_label.text_color = color
        
        Clock.schedule_once(lambda dt: self.clear_message(), 5)
    
    def clear_message(self):
        # Limpia el mensaje de advertencia
        self.ids.warning_label.text = ""

    # Moverse al dashboard
    def go_to_dashboard(self): 
        self.manager.current = "dashboard"
    
    # Para ver o no la contraseña (ojito)
    def toggle_password_visibility(self):
        textfield = self.ids.password
        boton_ojo = self.ids.eye_btn
        #  invertir visibilidad 
        textfield.password = not textfield.password
        # invertir el icono según el estado
        boton_ojo.icon = "eye" if not textfield.password else "eye-off"

# =================================================================
# ======= DASHBOARD CON NAVIGATION RAIL ===========================
# =================================================================
class Dashboard(MDScreen):

    # Forzar cargar datos en Home
    def on_enter(self):
        internal_manager = self.ids.screen_manager2
        home_screen = internal_manager.get_screen('home')
        home_screen.cargar_info_terapeuta()
        
    #  Borrar los datos de IDTerapeuta local y regresar a Login 
    def logout(self):
        try:
            app = MDApp.get_running_app()

            # Limpiar estado a nivel de aplicacion
            app.user_email = None
            app.user_uid = None
            app.paciente_actual = None

            # Resetear el screen manager interno para que muestre la pantalla principal
            try:
                self.ids.screen_manager2.current = "home"
            except Exception as e:
                print(f"No se pudo resetear screen_manager2: {e}")

            # Limpiar los campos del LogIn 
            try:
                login_screen = self.manager.get_screen("login")
                if "user" in login_screen.ids:
                    login_screen.ids.user.text = ""
                if "password" in login_screen.ids:
                    login_screen.ids.password.text = ""
                if "warning_label" in login_screen.ids:
                    login_screen.ids.warning_label.text = ""
            except Exception as e:
                print(f"No se pudieron limpiar campos del login: {e}")

            # Volver al login
            self.manager.transition.direction = "right"
            self.manager.current = "login"

        except Exception as e:
            print(f"Error en logout: {e}")
            import traceback
            traceback.print_exc()

# =================================================================
# ======= PANTALLA DE HOME ========================================
# =================================================================
class Home(MDScreen):

    def on_enter(self): # esperar tantito porque si no se traba
        Clock.schedule_once(self.cargar_datos_inicio, 0.1)               
        
    def cargar_datos_inicio(self, dt):
        print("Iniciando carga de datos diferida...")
        self.cargar_info_terapeuta()
        self.iniciar_reloj()
        print(f"IDs disponibles: {list(self.ids.keys())}")

    #  Obtener la información del terapeuta 
    def cargar_info_terapeuta(self):
        try:
            app = MDApp.get_running_app()
            email = getattr(app, "user_email", None)

            if not email:
                print("Aun no hay email...")
                return

            IDTerapeuta = email.split("@")[0]
            
            # Actualización directa
            self.ids.terapeuta_nombre.text = str(IDTerapeuta)
            self.ids.terapeuta_email.text = f"Correo: {email}"
            #print(f"Info actualizada manualmente: {IDTerapeuta}")

        except Exception as e:
            print(f"Error actualizando info: {e}")

    #  Reloj y hora 
    def iniciar_reloj(self):
        def actualizar_tiempo(dt):
            try:
                ahora = datetime.now()
                
                if 'fecha_label' in self.ids:
                    self.ids.fecha_label.text = ahora.strftime("%d %B %Y")
                
                if 'hora_label' in self.ids:
                    self.ids.hora_label.text = ahora.strftime("%H:%M:%S")
                    
            except Exception as e:
                print(f"Error actualizando tiempo: {e}")
        
        Clock.schedule_interval(actualizar_tiempo, 0.5)
        actualizar_tiempo(0)

    def ir_a_pacientes(self):
        self.manager.current = "patients"
        self.manager.transition.direction = "left"

    def abrir_nuevo_paciente(self):
        self.manager.current = "newpatient"
        self.manager.transition.direction = "left"
        
# =================================================================
# ======= PANTALLA DE BÚSQUEDA ====================================
# =================================================================
class Patients(MDScreen):
    pacientes_data = []  # Lista completa de pacientes
    
    def on_enter(self): # esperar tantito porque si no se traba
        Clock.schedule_once(self.cargar_datos_inicio, 0.1)               
        
    def cargar_datos_inicio(self, dt):
        self.cargar_pacientes()

    #  Cargar pacientes desde Firestore 
    def cargar_pacientes(self):
        
        # Obtiene todos los pacientes de Firestore y los muestra en la lista
        try:
            pacientes_ref = db.collection("Pacientes")
            docs = pacientes_ref.stream()
            
            # Limpiar lista actual
            lista = self.ids.patients_list
            lista.clear_widgets()
            self.pacientes_data = []
            
            # Agregar cada paciente a la lista
            for doc in docs:
                if doc.exists:
                    datos = doc.to_dict()
                    paciente_id = doc.id
                    
                    nombre_completo = f"{datos.get('Nombre', '')} {datos.get('Apellido', '')}".strip()
                    
                    # Guardar datos completos para búsqueda
                    self.pacientes_data.append({
                        'id': paciente_id,
                        'nombre': nombre_completo,
                        'datos': datos
                    })
                    
                    # print(self.pacientes_data) # ver la info

                    # Crear item de lista
                    item = TwoLineListItem(
                        text=nombre_completo if nombre_completo else "Sin nombre",
                        secondary_text=f"ID: {paciente_id}",
                        on_release=lambda x, pid=paciente_id: self.abrir_paciente(pid)
                    )
                    
                    lista.add_widget(item)
            
            if not self.pacientes_data:
                # Si no hay pacientes, mostrar mensaje
                item = TwoLineListItem(
                    text="No hay pacientes registrados",
                    secondary_text="Presiona + para agregar uno"
                )
                lista.add_widget(item)
                
        except Exception as e:
            print(f"Error cargando pacientes: {e}")
    
    #  Buscar pacientes filtrando el listado
    def buscar_paciente(self, texto_busqueda):
        texto = texto_busqueda.lower().strip()
        
        lista = self.ids.patients_list
        lista.clear_widgets()
        # Filtra la lista de pacientes según el texto de búsqueda
        if not texto:
            # Si está vacío, recargar todos
            self.cargar_pacientes()
            return
        
        # Filtrar pacientes
        pacientes_filtrados = [
            p for p in self.pacientes_data
            if texto in p['id'].lower() or texto in p['nombre'].lower()
        ]
        
        if pacientes_filtrados: # Buscar en la lista
            for paciente in pacientes_filtrados:
                item = TwoLineListItem(
                    text=paciente['nombre'],
                    secondary_text=f"ID: {paciente['id']}",
                    on_release=lambda x, pid=paciente['id']: self.abrir_paciente(pid)
                )
                lista.add_widget(item)
        else:
            item = TwoLineListItem(
                text="No se encontraron pacientes",
                secondary_text="Intenta con otro término"
            )
            lista.add_widget(item)
    
    #  Ir a la pagina de pacientes 
    def abrir_paciente(self, paciente_id):
        print(f"Abriendo paciente: {paciente_id}")
        
        # Guardar ID del paciente en la app para usarlo en la siguiente pantalla
        app = MDApp.get_running_app()
        app.paciente_actual = paciente_id
        
        # Cambiar a pantalla de paciente
        self.manager.current = "details"
        self.manager.transition.direction = "left"
    
    # Ir a la página para registrar un nuevo paciente 
    def abrir_nuevo_paciente(self):
        self.manager.current = "newpatient"
        self.manager.transition.direction = "left"
        
# =================================================================
# ======= PANTALLA DE NUEVO  PACIENTE  ============================
# =================================================================
class New_Patient(MDScreen):
    
    sesiones_programadas = 0  # Valor inicial
    trayectorias = 0  # Valor inicial
    dialog = None
    
    def on_enter(self):
        # Se ejecuta al entrar a la pantalla
        self.limpiar_formulario()

    #  Guardar paciente 
    def guardar_paciente(self):
        try:
            # Obtener datos del formulario
            nombre = self.ids.nombre_field.text.strip()
            apellido = self.ids.apellido_field.text.strip()
            fecha_nacimiento = self.ids.nacimiento.text.strip()
            diagnostico = self.ids.diagnostico_field.text.strip()
            
            # Validaciones
            if not nombre:
                self.ids.nombre_field.error = True
                self.mostrar_mensaje("Atención", "El nombre es obligatorio")
                return
            
            if not apellido:
                self.ids.apellido_field.error = True
                self.mostrar_mensaje("Atención", "El apellido es obligatorio")
                return
            
            # Crear ID del paciente (NombreApellido)
            nombre = nombre.strip()
            apellido = apellido.strip()
            # 3 primeras letras del nombre y apellido
            parte_nombre = nombre[:3].capitalize() if len(nombre) >= 3 else nombre.capitalize()
            parte_apellido = apellido[:3].capitalize() if len(apellido) >= 3 else apellido.capitalize()
            # Eliminar separadores de fecha
            solo_numeros_fecha = "".join([c for c in fecha_nacimiento if c.isdigit()])
            # Construir ID final
            paciente_id = f"{parte_nombre}{parte_apellido}{solo_numeros_fecha}"
            
            # Verificar si ya existe
            doc_ref = db.collection("Pacientes").document(paciente_id)
            doc = doc_ref.get()
            if doc.exists:
                self.mostrar_mensaje(
                    "Paciente duplicado",
                    f"Ya existe un paciente con ID: {paciente_id}\nIntente con otro nombre."
                )
                return
            
            # Obtener terapeuta actual
            app = MDApp.get_running_app()
            terapeuta_email = getattr(app, 'user_email', 'desconocido')
            terapeuta_id = terapeuta_email.split('@')[0]
            
            # Datos a guardar en Firestore
            datos_paciente = {
                'IDPaciente': paciente_id,
                'Nombre': nombre,
                'Apellido': apellido,
                'FechaNacimiento': fecha_nacimiento if fecha_nacimiento else '',
                'Diagnostico': diagnostico if diagnostico else '',
                'SesionesCompletadas': 0,
                'TerapeutaAsignado': terapeuta_id,
                'FechaRegistro': firestore.SERVER_TIMESTAMP
            }
            
            # Guardar en Firestore
            doc_ref.set(datos_paciente)
            
            print(f"Paciente guardado: {paciente_id}")
            print(f"Datos: {datos_paciente}")
            
            # Mostrar mensaje de éxito
            self.mostrar_mensaje(
                "Paciente registrado",
                f"Paciente {nombre} {apellido} registrado exitosamente.\nID: {paciente_id}",
                callback=self.cancelar
            )
            
        except Exception as e:
            print(f"Error guardando paciente: {e}")
            import traceback
            traceback.print_exc()
            self.mostrar_mensaje("Error", f"No se pudo guardar el paciente:\n{str(e)}")
    
    # Para cancelar limpiar campos y regresar a home 
    def cancelar(self):
        self.limpiar_formulario()
        self.manager.current="patients"
        self.manager.transition.direction = "right"

    # Limpia todos los campos del formulario
    def limpiar_formulario(self):
        
        self.ids.nombre_field.text = ""
        self.ids.apellido_field.text = ""
        self.ids.nacimiento.text = ""
        self.ids.diagnostico_field.text = ""
        
        # Resetear errores
        self.ids.nombre_field.error = False
        self.ids.apellido_field.error = False
    
    #  Mensajesss de dialogo 
    def mostrar_mensaje(self, titulo, texto, callback=None):
        if not self.dialog:
            self.dialog = MDDialog(
                title=titulo,
                text=texto,
                buttons=[
                    MDFlatButton(
                        text="OK",
                        on_release=lambda x: self.cerrar_dialogo(callback)
                    )
                ]
            )
        else:
            self.dialog.title = titulo
            self.dialog.text = texto
            # Actualizar callback del botón
            if self.dialog.buttons:
                self.dialog.buttons[0].on_release = lambda x: self.cerrar_dialogo(callback)
        
        self.dialog.open()
    def cerrar_dialogo(self, callback=None):
        # Cierra el diálogo y ejecuta callback si existe
        if self.dialog:
            self.dialog.dismiss()
        
        if callback:
            callback()

# =================================================================
# ======= PANTALLA DE PACIENTE  ===================================
# =================================================================
class Details_Patient(MDScreen):
    paciente_id = None
    datos_paciente = {}
    sesiones_lista = []
    trayectorias_cache = {} # cache local: {trayectoria_id: [puntos]}
    canvas_grafica = None # referencia al canvas matplotlib actual

    # Paletade colores a usar (combinen con la app)
    COLOR_TERAPEUTA = "#000000"
    COLOR_PACIENTE = "#0097a9"

    # Parametros de procesamiento de trayectoria
    VENTANA_SUAVIZADO = 5

    def on_enter(self):
        Clock.schedule_once(self.cargar_datos_paciente, 0.1)

    # Cargar datos desde firestore  
    def cargar_datos_paciente(self, dt=None):
        try:
            app = MDApp.get_running_app()
            self.paciente_id = getattr(app, 'paciente_actual', None)

            if not self.paciente_id:
                print("No hay paciente seleccionado")
                return

            doc_ref = db.collection("Pacientes").document(self.paciente_id)
            doc = doc_ref.get()

            if doc.exists:
                self.datos_paciente = doc.to_dict()
                self.cargar_sesiones() # llena self.sesiones_lista
                self.cargar_trayectorias_cache() # llena self.trayectorias_cache
                self.mostrar_datos() # depende de los dos anteriores
                self.mostrar_grafica_vacia()
            else:
                print(f"No se encontro el paciente: {self.paciente_id}")

        except Exception as e:
            print(f"Error cargando datos del paciente: {e}")
            import traceback
            traceback.print_exc()

    # Cargar trayectorias del terapeuta a cache local  
    def cargar_trayectorias_cache(self):
        try:
            self.trayectorias_cache = {}
            tray_ref = (db.collection("Pacientes")
                          .document(self.paciente_id)
                          .collection("Trayectorias"))
            for doc in tray_ref.stream():
                if doc.exists:
                    data = doc.to_dict()
                    puntos = data.get("TrayectoriaCompleta", [])
                    self.trayectorias_cache[doc.id] = puntos
            # print(f"Trayectorias en cache: {len(self.trayectorias_cache)}")
        except Exception as e:
            print(f"Error cargando trayectorias: {e}")

    # Actualizar info personal y metricas promedio 
    def mostrar_datos(self):
        try:
            nombre = self.datos_paciente.get('Nombre', '')
            apellido = self.datos_paciente.get('Apellido', '')
            self.ids.nombre_label.text = f"{nombre} {apellido}"

            # Contadores
            num_sesiones = len(self.sesiones_lista)
            num_trayectorias = len(self.trayectorias_cache)
            self.ids.contador_sesiones.text = str(num_sesiones)
            self.ids.contador_trayectorias.text = str(num_trayectorias)

            # Tabla de metricas promedio
            promedios = self.calcular_metricas_promedio()
            self.ids.prom_errores.text = f"{promedios['errores']:.2f}"
            self.ids.prom_estrellas.text = f"{promedios['estrellas']:.2f}"
            self.ids.prom_tiempo.text = f"{promedios['tiempo']:.2f} s"
            self.ids.prom_porcentaje.text = f"{promedios['porcentaje']:.2f} %"

            print(f"Datos mostrados para: {nombre} {apellido}")

        except Exception as e:
            print(f"Error mostrando datos: {e}")
            import traceback
            traceback.print_exc()

    # Calcular promedios globales de metricas 
    def calcular_metricas_promedio(self):
        promedios = {'errores': 0.0, 'estrellas': 0.0,
                     'tiempo': 0.0, 'porcentaje': 0.0}

        if not self.sesiones_lista:
            return promedios

        n = len(self.sesiones_lista)
        suma_errores = 0.0
        suma_estrellas = 0.0
        suma_tiempo = 0.0
        suma_porcentaje = 0.0

        for s in self.sesiones_lista:
            suma_errores    += float(s.get('TotalErrors', 0) or 0)
            suma_estrellas  += float(s.get('stars', 0) or 0)
            suma_tiempo     += float(s.get('TotalTime', 0) or 0)
            suma_porcentaje += float(s.get('InsideTimePercentage', 0) or 0)

        promedios['errores'] = suma_errores / n
        promedios['estrellas'] = suma_estrellas / n
        promedios['tiempo'] = suma_tiempo / n
        promedios['porcentaje'] = suma_porcentaje / n
        return promedios

    # Descargar las metricas de las sesiones  
    def cargar_sesiones(self):
        try:
            self.ids.sesiones_list.clear_widgets()
            self.sesiones_lista = []

            sesiones_ref = (db.collection("Pacientes")
                              .document(self.paciente_id)
                              .collection("Sesiones"))
            docs = sesiones_ref.order_by(
                "DateTime", direction=firestore.Query.DESCENDING
            ).stream()

            for doc in docs:
                if doc.exists:
                    sesion_data = doc.to_dict()
                    sesion_data['id'] = doc.id
                    self.sesiones_lista.append(sesion_data)

            sesion_count = len(self.sesiones_lista)

            # La sesion mas antigua es la #1
            # La lista esta en orden descendente, invertir
            for i, sesion_data in enumerate(self.sesiones_lista):
                numero_cronologico = sesion_count - i
                self.agregar_sesion_card(sesion_data, numero_cronologico)

            # Actualizar el SesionesCompletadas en firestore
            doc_ref = db.collection("Pacientes").document(self.paciente_id)
            doc_ref.update({'SesionesCompletadas': sesion_count})

            if sesion_count == 0:
                from kivymd.uix.label import MDLabel
                mensaje = MDLabel(
                    text="No hay sesiones registradas",
                    halign="center",
                    theme_text_color="Hint",
                    size_hint_y=None,
                    height=50
                )
                self.ids.sesiones_list.add_widget(mensaje)

            print(f"Sesiones cargadas: {sesion_count}")

        except Exception as e:
            print(f"Error cargando sesiones: {e}")
            import traceback
            traceback.print_exc()

    # Mostrar en la tarjeta las sesiones como lista 
    def agregar_sesion_card(self, sesion_data, numero_sesion):
        METRIC_NAMES = {
            "InsideTimePercentage": "Tiempo dentro de la trayectoria",
            "stars": "Estrellas obtenidas",
            "radio": "Tolerancia de la trayectoria (cm)",
            "TotalErrors": "Cantidad de errores",
            "TotalTime": "Tiempo de la sesion"
        }

        CAMPOS_EXCLUIDOS = ["DateTime", "IDSesion", "CantidadPuntosPaciente",
                            "TrayectoriaPaciente", "id"]

        # tarjeta principal para presionar
        card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            size_hint_x=0.95,
            adaptive_height=True,
            padding=20,
            spacing=12,
            elevation=0.5,
            radius=[12],
            ripple_behavior=True,
            focus_behavior=True
        )
        # Closure para capturar la sesion concreta
        card.bind(on_release=lambda x, s=sesion_data: self.seleccionar_sesion(s))

        # titulo con numero y Fecha
        header_box = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=35,
            spacing=15
        )

        numero_box = MDBoxLayout(
            size_hint_x=None,
            width=80,
            orientation="horizontal",
            spacing=8
        )

        sesion_numero = MDLabel(
            text=f"#{numero_sesion}",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color,
            halign="center"
        )
        numero_box.add_widget(sesion_numero)
        header_box.add_widget(numero_box)

        id_sesion = sesion_data.get("IDSesion", f"Sesion {numero_sesion}")
        titulo_label = MDLabel(
            text=f"{id_sesion}",
            font_style="Subtitle1",
            bold=True,
            size_hint_x=0.6
        )
        header_box.add_widget(titulo_label)

        fecha = sesion_data.get("DateTime", "Sin fecha")
        try:
            if hasattr(fecha, 'strftime'):
                fecha_str = fecha.strftime("%d/%m/%Y %H:%M")
            else:
                fecha_str = str(fecha)
        except Exception:
            fecha_str = str(fecha)

        fecha_label = MDLabel(
            text=fecha_str,
            font_style="Caption",
            halign="right",
            theme_text_color="Secondary"
        )
        header_box.add_widget(fecha_label)

        card.add_widget(header_box)

        metricas_titulo = MDLabel(
            text="Metricas de desempeno:",
            font_style="Subtitle2",
            bold=True,
            size_hint_y=None,
            height=28,
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_dark
        )
        card.add_widget(metricas_titulo)

        metricas_container = MDBoxLayout(
            orientation="vertical",
            spacing=8,
            size_hint_y=None,
            adaptive_height=True,
            padding=[10, 5, 10, 5]
        )

        metricas_encontradas = False
        for key, value in sesion_data.items():
            if key not in CAMPOS_EXCLUIDOS:
                metricas_encontradas = True
                nombre_metrica = METRIC_NAMES.get(key, key)

                if isinstance(value, float):
                    if key == "radio":
                        value_cm = value * 100 # Formato de cm
                        valor_formateado = f"{value_cm:.2f}"
                    else:
                        valor_formateado = f"{value:.2f}"

                    if key == "InsideTimePercentage":
                        valor_formateado = f"{valor_formateado}%"
                else:
                    valor_formateado = str(value)

                metrica_box = MDBoxLayout(
                    orientation="horizontal",
                    size_hint_y=None,
                    height=24,
                    spacing=10
                )

                nombre_label = MDLabel(
                    text=f"{nombre_metrica}:",
                    font_style="Body2",
                    size_hint_x=None,
                    width=300
                )
                metrica_box.add_widget(nombre_label)

                valor_label = MDLabel(
                    text=valor_formateado,
                    font_style="Body2",
                    bold=True,
                    halign="right",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color
                )
                metrica_box.add_widget(valor_label)

                metricas_container.add_widget(metrica_box)

        if not metricas_encontradas:
            sin_metricas = MDLabel(
                text="Sin metricas registradas",
                font_style="Caption",
                theme_text_color="Hint",
                size_hint_y=None,
                height=30,
                italic=True
            )
            metricas_container.add_widget(sin_metricas)

        metricas_container.height = len(metricas_container.children) * 24 + 16

        card.add_widget(metricas_container)

        altura_total = 35 + 1 + 28 + metricas_container.height + 52
        card.height = altura_total

        self.ids.sesiones_list.add_widget(card)

    # Click en tarjeta de sesion: graficar  
    def seleccionar_sesion(self, sesion_data):
        try:
            id_traj = sesion_data.get("Trayectoria", None)
            traj_terapeuta = self.trayectorias_cache.get(id_traj, []) if id_traj else []
            traj_paciente = sesion_data.get("TrayectoriaPaciente", [])

            self.dibujar_trayectorias(traj_terapeuta, traj_paciente, id_traj,
                                       sesion_data.get("IDSesion", ""))
        except Exception as e:
            print(f"Error al seleccionar sesion: {e}")
            import traceback
            traceback.print_exc()

    # Procesamiento de trayectorias  
    def _puntos_a_array(self, puntos):
        if not puntos:
            return np.empty((0, 3))
        coords = []
        for p in puntos:
            try:
                coords.append([float(p.get('x', 0.0)),
                               float(p.get('y', 0.0)),
                               float(p.get('z', 0.0))])
            except Exception:
                continue
        return np.array(coords) if coords else np.empty((0, 3))

    def _sincronizar_origen(self, arr):
        if arr.size == 0:
            return arr
        return arr - arr[0]

    def _suavizar(self, arr, ventana=None):
        if arr.size == 0:
            return arr
        if ventana is None:
            ventana = self.VENTANA_SUAVIZADO
        if len(arr) < ventana:
            return arr
        kernel = np.ones(ventana) / ventana
        suav = np.empty_like(arr)
        for i in range(arr.shape[1]):
            suav[:, i] = np.convolve(arr[:, i], kernel, mode='same')
        return suav

    # Renderizado de la grafica  
    def mostrar_grafica_vacia(self):
        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')
        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Z (m)")
        ax.set_title("Selecciona una sesion para visualizar la trayectoria",
                     fontsize=10)
        fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)
        self._reemplazar_canvas(fig)

    def dibujar_trayectorias(self, puntos_terapeuta, puntos_paciente,
                              id_traj, id_sesion):
        arr_t = self._puntos_a_array(puntos_terapeuta)
        arr_p = self._puntos_a_array(puntos_paciente)

        arr_t = self._sincronizar_origen(arr_t)
        arr_p = self._sincronizar_origen(arr_p)

        arr_t = self._suavizar(arr_t)
        arr_p = self._suavizar(arr_p)

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111, projection='3d')

        if arr_t.size > 0:
            ax.plot(arr_t[:, 0], arr_t[:, 1], arr_t[:, 2],
                    color=self.COLOR_TERAPEUTA, linewidth=2,
                    label="Terapeuta")
        if arr_p.size > 0:
            ax.plot(arr_p[:, 0], arr_p[:, 1], arr_p[:, 2],
                    color=self.COLOR_PACIENTE, linewidth=1.8,
                    label="Paciente")

        ax.set_xlabel("X (m)")
        ax.set_ylabel("Y (m)")
        ax.set_zlabel("Z (m)")
        ax.set_title("", fontsize=10)
        ax.legend(loc="best", fontsize=9)
        ax.view_init(elev=25, azim=-60)
        if arr_t.size > 0:
            margen = 0.05
            xs = arr_t[:, 0]
            ys = arr_t[:, 1]
            zs = arr_t[:, 2]
            if arr_p.size > 0:
                xs = np.concatenate([xs, arr_p[:, 0]])
                ys = np.concatenate([ys, arr_p[:, 1]])
                zs = np.concatenate([zs, arr_p[:, 2]])
            ax.set_xlim(xs.min() - margen, xs.max() + margen)
            ax.set_ylim(ys.min() - margen, ys.max() + margen)
            ax.set_zlim(zs.min() - margen, zs.max() + margen)

        fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

        self._reemplazar_canvas(fig)

    def _reemplazar_canvas(self, fig):
        contenedor = self.ids.grafica_container
        contenedor.clear_widgets()
        if self.canvas_grafica is not None:
            try:
                plt.close(self.canvas_grafica.figure)
            except Exception:
                pass
        self.canvas_grafica = FigureCanvasKivyAgg(fig)
        contenedor.add_widget(self.canvas_grafica)

    # Navegacion y dialogos 
    def volver_a_lista(self):
        self.manager.current = "patients"
        self.manager.transition.direction = "right"

    def mostrar_mensaje(self, titulo, texto, callback=None):
        dialog = MDDialog(
            title=titulo,
            text=texto,
            buttons=[
                MDFlatButton(
                    text="OK",
                    on_release=lambda x: self.cerrar_mensaje(dialog, callback)
                )
            ]
        )
        dialog.open()

    def cerrar_mensaje(self, dialog, callback=None):
        dialog.dismiss()
        if callback:
            callback()

    def refresh(self):
        self.cargar_datos_paciente()

# =================================================================
# ======= PANTALLA DEL INFORMACION ================================
# =================================================================
class Information(MDScreen):
    # Solo se visualliza, no interactua.
    # Revisar app.kv <Information>
    pass

# =================================================================
# ======= BUILD ===================================================
# =================================================================
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class MainApp(MDApp):
    title = 'SIR-HAPT' 
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.secondary_palette = "BlueGray"
        Window.set_icon(resource_path('logo.ico'))
        return Builder.load_file(resource_path('app.kv'))

if __name__ == '__main__':
    MainApp().run()