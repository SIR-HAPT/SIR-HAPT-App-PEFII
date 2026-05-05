Instrucciones para crear nuevo proyecto con kivy y kivymd

1. Abrir VS Code y una carpeta de proyecto
    Abre VS Code.
    File → Open Folder... → selecciona la carpeta donde trabajarás
    Abre la terminal integrada: Terminal → New Terminal.

2. Verifica Python y configúralo en VS Code
    python --version

3. Crear entorno virtual
    python -m venv kivy_venv

4. Permitir acceso
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

5. Activar entorno virtual
    app_venv\Scripts\activate

6. Instalar kivy (Dejas que se decargue todo)
    python -m pip install "kivy[base]" kivy_examples

7. Actualizar la cosa porque si no no funciona
    pip install --upgrade setuptools

8. Instalar kivy md (Dejas que se decargue todo)
    pip install kivymd

9. Instalar firebase (Dejas que se decargue todo)
    pip install pyrebase4
    pip install firebase-admin google-cloud-firestore
    pip install kivy_garden.matplotlib

10. Verificar lo que tienes instalado en el entorno virtual 
    pip list

Listoo!

Instrucciones para abrir un proyecto

1.  Abrir el proyecto en File > OpenFolder y selecciona la carpeta del proyecto

2.  Ejectuar los permisos y verificar la versión de Python y que esten las librerias
    app_venv\Scripts\activate
    pip list

3.  Activar el Run en el entorno virtual: Ctrl + Shift + P > Select Interpreter > selecciona el kivy_venv

Listoo, dale run y sigue editando c:

