from core.services import NavalAttendanceService
from infra.json_repository import JSONUserRepository, JSONAttendanceRepository
from core.ports import FaceRecognitionPort
from typing import Optional

# 1. Creamos un Simulador de IA (Mock) para no necesitar cámara web en esta prueba
class MockFaceAdapter(FaceRecognitionPort):
    def register_face(self, user_id: str, image_frame: bytes) -> str:
        return f"infra/data/faces/{user_id}.jpg"

    def identify_face(self, image_frame: bytes) -> Optional[str]:
        # Simulamos que la "foto" en bytes es simplemente el texto de la matrícula
        return image_frame.decode('utf-8')

def ejecutar_prueba():
    print("--- INICIANDO SISTEMA DE PRUEBA NIAS ---")
    
    # 2. Instanciamos los repositorios reales (esto creará la carpeta infra/data/)
    user_repo = JSONUserRepository(file_path="infra/data/users.json")
    att_repo = JSONAttendanceRepository(file_path="infra/data/attendance.json")
    face_repo = MockFaceAdapter()
    
    # 3. Inicializamos el cerebro del sistema
    service = NavalAttendanceService(user_repo, att_repo, face_repo)
    
    # 4. PRUEBA: Registro de Elementos
    print("\n[+] Registrando Elementos...")
    
    # MODIFICA AQUÍ: Puedes agregar más elementos copiando una de estas líneas
    # y cambiando la matrícula (ej. "111222"), grado, nombre y cargo.
    service.register_element("123456", "Teniente de Navío", "Juan Pérez", "Batallón 1", "Comandante", b"123456")
    service.register_element("654321", "Cabo", "Luis Gómez", "Batallón 1", "Chofer", b"654321")
    
    print("Elementos registrados con éxito. (Revisa infra/data/users.json)")

    # 5. PRUEBA: Pase de lista (Simulando al Oficial de Guardia)
    print("\n[+] Registrando Movimientos...")
    
    # Juan y Luis entran a la unidad
    # MODIFICA AQUÍ: Puedes cambiar la ubicación, o poner is_entry=False para simular una salida directa.
    service.process_attendance(b"123456", is_entry=True, reason="Ingreso a labores", location_city_state="Ixtapa, Jal.")
    service.process_attendance(b"654321", is_entry=True, reason="Ingreso a labores", location_city_state="Ixtapa, Jal.")
    
    # Juan sale de comisión
    # MODIFICA AQUÍ: Intenta agregar otro movimiento, por ejemplo, que el "654321" salga al hospital.
    # Solo copia esta línea de abajo, pon la matrícula 654321 y cambia el reason a "Cita médica".
    service.process_attendance(b"123456", is_entry=False, reason="Comisión de servicio al Banco", location_city_state="Ixtapa, Jal.")
    
    print("Movimientos registrados con éxito. (Revisa infra/data/attendance.json)")

    # 6. PRUEBA: Reporte del Comandante
    print("\n[!] --- REPORTE DE SITUACIÓN EN TIEMPO REAL ---")
    
    # Esta función evalúa todos los movimientos que modificaste arriba y genera el reporte.
    situacion = service.get_current_situation()
    
    print("\n[ A BORDO ]")
    for p in situacion["a_bordo"]:
        print(f" > {p['grado_nombre']} ({p['cargo']}) - Ingresó: {p['ultimo_registro']}")
        
    print("\n[ FUERA DE LA UNIDAD ]")
    for p in situacion["fuera"]:
        print(f" > {p['grado_nombre']} ({p['cargo']}) - Salió: {p['ultimo_registro']} | Motivo: {p['motivo']}")

if __name__ == "__main__":
    ejecutar_prueba()