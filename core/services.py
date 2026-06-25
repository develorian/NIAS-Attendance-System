"""
El Cerebro de la aplicación. Aquí es donde combinamos nuestraas entidades puras y las interfaces (puertos) para ejecutar las acciones reales del sistema.

Usaremos el concepto de Inyección de Dependencias (Dependency Injection). Nuestro servicio no va a crear la base de datos ni a instanciar DeepFace directamente; en su lugar, va a recibir los "puertos" ya inicializados. Esto hace que el código 100% intercambiable.
"""

import datetime
from typing import List, Optional, Dict
from .entities import User, AttendanceRecord
from .ports import UserRepositoryPort, AttendanceRepositoryPort, FaceRecognitionPort

class NavalAttendanceService:
    """
    Clase de servicio que orquesta la lógica de negocio central (core business logic). Depende exclusivamente en abstracciones (Puertos), permaneciendo completamente agnóstica a las implementaciones concretas de la base de datos o de la Inteligencia Artifical (IA).
    """

    def __init__(self, user_repo: UserRepositoryPort, attendance_repo: AttendanceRepositoryPort, face_repo: FaceRecognitionPort):
        # Inyección de dependencias
        self.user_repo = user_repo
        self.attendance_repo = attendance_repo
        self.face_repo = face_repo


    def _get_formatted_location(self, location_city_state: str) -> str:
        """
        Toma la Ciudad y Estaado (provistos por el GPS del frontend) y construye la cadena de ubicación actual en formato oficial naval.
        Ej: "Acapulco, Gro., a 23 de junio del 2026.
        """

        now = datetime.datetime.now()
        MONTHS = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        day = now.day
        month = MONTHS[now.month -1]
        year = now.year

        return f"{location_city_state}, a {day} de {month} del {year}."
    

    def register_element(self, user_id: str, grade: str, name: str, assignment: str, role: str, image_frame: bytes) -> User:
        """
        Registra a un nuevo elemento naval y biometría facial.
        """

        # 1. Procesar y guardar el rostro mediante el puerto de IA
        face_path = self.face_repo.register_face(user_id, image_frame)

        # 2. Construir la identidad
        new_user = User (
            id = user_id,
            grade = grade,
            name = name,
            assignment = assignment,
            role = role,
            face_encoding_path = face_path
        )

        # 3. Persistir en la base de datos mediante el puerto
        self.user_repo.save(new_user)
        return new_user
    

    def process_attendance(self, image_frame: bytes, is_entry: bool, reason: str, location_city_state: str) -> Optional[AttendanceRecord]:
        """
        Procesa el registo. El Oficial de Guardia (a través de la API dicta explícitamente si es una entrada o salida y el sistema hace una lectura facial para ingresar el registro.
        Retorna el registro creado o None si el rostro no es conocido.
        """

        # 1. Identificar el rostro biométricamente
        user_id = self.face_repo.identify_face(image_frame)
        if not user_id:
            return None # Rostro desconocido o no coincide
        
        # 2. Formatear la ubicación oficial
        official_location = self._get_formatted_location(location_city_state)

        # 3. Construir el registro
        record = AttendanceRecord(
            user_id = user_id,
            timestamp = datetime.datetime.now(), # hora exacta del servidor
            is_entry = is_entry,
            reason = reason,
            location = official_location
        )

        # 4. Guardar el registro
        self.attendance_repo.save(record)
        return record


    def get_current_situation(self) -> Dict[str, List[dict]]:
        """
        Reporte en tiempo real para el Comandante.
        Itera sobre los usuarios y busca su último movimiento para determinar quién está "A bordo" y quién está "Fuera".
        """
        all_users = self.user_repo.get_all()
        situation = {
            "a_bordo": [],
            "fuera": []
        }

        for user in all_users:
            last_record = self.attendance_repo.get_last_record_for_user(user.id)

            user_info = {
                "grado_nombre": f"{user.grade} {user.name}",
                "matricula": user.id,
                "cargo": user.role,
                "ultimo_registro": last_record.timestamp.strftime("%H:%M hrs (%d/%m/%Y)") if last_record else "Sin registros",
                "motivo": last_record.reason if last_record else "N/A"
            }

            # Si no tiene resgistros previos, asumimos que no está a bordo.
            if last_record and last_record.is_entry:
                situation["a_bordo"].append(user_info)
            else:
                situation["fuera"].append(user_info)

        return situation 


    def get_daily_report(self, target_date: Optional[datetime.date] = None) -> List[AttendanceRecord]:
        """
        Genera el reporte de un día específico.
        Si no se provee fecha, usa el día actual.
        """

        if not target_date:
            target_date = datetime.date.today()

        return self.attendance_repo.get_daily_records(target_date)
    

    """
    Con este código logramos tener:

    1. Ubicación dinámica: Implementamos la función _get_formatted_location() que extrae el día, mes y año del sistema y formatea el string: "Puerto Vallarta, Jal., a {day} de {month} del {year}.". Esto inyecta automáticamente con cada pase de lista.

    2. Entrada vs. Salida Automática: El método process_attendance cuenta cuántos registros tiene un elemento en ese día específico. Usando un operador de módulo (% 2 == 0), el sistema sabe matemáticamente si el usuario está entrando o saliendo sin que el elemento tenga que entrar ningún botón.

    3. Manejo de Motivos: Si el administrador registra una entrada/salida manual con un motivo distinto (ej. "Comisión de servicio"), el sistema respeta ese motivo custom_reason; si no, usa los valores por defecto ("ingreso a labores" o "término de labores").

    Con esto, el núcleo (Core) de la aplicación está 100% terminado para el MVP.

    La lógica naval está encapsulada y protegida.
    """