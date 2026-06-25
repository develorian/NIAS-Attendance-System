import sys
import os

# 1. Le decimos a Python que la carpeta raíz de nuestro proyecto está un nivel arriba
# Esto evita el "ModuleNotFoundError: No module named 'core'"
directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(directorio_raiz)

# 2. Ahora sí, los imports normales
import threading
import time
import schedule
from flask import Flask, send_from_directory
from flask_restful import Api
from flask_cors import CORS


# 3. Y por último: Importamos las piezas de la Arquitectura.
from core.services import NavalAttendanceService
from infra.json_repository import JSONUserRepository, JSONAttendanceRepository
from infra.deepface_adapter import DeepFaceAdapter
from api.routes import UserRegisterResource, AttendanceResource, SituationReportResource, DailyReportResource


app = Flask(__name__)

# Ruta al directorio ui/ (un nivel arriba de api/)
# UI_DIR = os.path.join(directorio_raiz, 'ui')


@app.route('/')
def serve_index():
    """Buscamos la carpeta 'ui' desde la raíz del proyecto"""
    directorio_raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    carpeta_ui = os.path.join(directorio_raiz, 'ui')
    return send_from_directory(carpeta_ui, 'index.html')
    """Sirve el frontend principal."""
    # return send_from_directory(UI_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Sirve archivos estáticos del frontend (CSS, JS, etc.)."""
    return send_from_directory(UI_DIR, path)
CORS(app)               # <-- Esto habilita CORS para todas las rutas
api = Api(app)


# 1. Ensamblaje de componentes
user_repo = JSONUserRepository()
att_repo = JSONAttendanceRepository()

# ¡AQUÍ ACTIVAMOS LA IA REAL EN LUGAR DE TESTING O SIMULADOR!
face_repo = DeepFaceAdapter()
naval_service = NavalAttendanceService(user_repo, att_repo, face_repo)


# 2. Registro de Endpoints
# Imyectamos el servicio en cada recurso web
api.add_resource(UserRegisterResource, '/api/v1/users', resource_class_kwargs = {'service': naval_service})
api.add_resource(AttendanceResource, '/api/v1/attendance', resource_class_kwargs = {'service': naval_service})
api.add_resource(SituationReportResource, '/api/v1/reports/situation', resource_class_kwargs = {'service': naval_service}) 
api.add_resource(DailyReportResource, '/api/v1/reports/daily', resource_class_kwargs = {'service': naval_service}) ## Verificar este reporte, porqué no aparece en api.routes??? O sí aparece??


# 3. TAREA AUTOMÁTICA (CRON JOB)
def generate_morning_report():
    """Compila y archiva el reporte diario a la hora establecida."""
    print("\n[SISTEMA] Generando Parte de Novedades automático (07:45 horas)...")

    situacion = naval_service.get_current_situation()
    a_bordo = len(situacion["a_bordo"])
    fuera = len(situacion["fuera"])
    
    print(f"[REPORTE] Personal a Bordo: {a_bordo}")
    print(f"[REPORTE] Personal Fuera: {fuera}")
    # NOTA: Aquí se puede agregar código para guardar el resumen en un PDF
    #       o enviarlo automáticamente por correo electrónico al Mando correspondiente.


def run_scheduler():
    """Ciclo infinito que verifica si es hora de ejecutar tareas pendientes."""
    schedule.every().day.at("07:45").do(generate_morning_report)

    while True:
        schedule.run_pending()
        time.sleep(300) # Revisa el reloj cada 300 segundo (5 minutos | Se puede poner en 60 para que revise cada minuto).


# 4. INICIO DLE SERVIDOR
if __name__ == '__main__':
    # Lanzamos el cronómetro de tareas en un hilo paralelo par no bloquear el servidor web.
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True) # Importante el daemon=True
    scheduler_thread.start()

    print("Iniciando Servidor Naval Identity & Attendance System (NIAS)....")
    # debug=False para evitar que el scheduler se ejecute dos veces por el auto-reload de Flask
    app.run(debug=False, host='0.0.0.0', port=5000)