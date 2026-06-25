"""
Adaptador de Almacenamiento JSON
Debido al requerimiento agnóstico a la base de datos, este adaptador usará archivos JSON locales. Si en el futuro se requiere o necesita usar PostgreSQL o MongoDB, solo se crearía un adaptador nuevo sin tocar el resto del sistema.
"""

import json
import os
from datetime import date, datetime
from typing import List, Optional
from core.entities import User, AttendanceRecord
from core.ports import UserRepositoryPort, AttendanceRepositoryPort


class JSONUserRepository(UserRepositoryPort):
    """
    Adaptador de almacenamiento en formato JSON para Usuarios.
    Cumple con el contrato de UserRepositoryPort.
    """

    def __init__(self, file_path: str = "infra/data/users.json"):
        self.file_path = file_path

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    
    def save(self, user: User) -> None:
        """ Guarda o actualiza un elemento naval en el archivo JSON. """
        # Eliminar si la matrícula ya existe para actualizar el registro
        users = [u for u in self.get_all() if u.id != user.id]
        users.append(user)

        with open(self.file_path, "w") as f:
            # Convertimos las entidades de Python a diccionarios para serializarlas
            json.dump([vars(u) for u in users], f, indent=4)

    
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Busca un elemento por su matrícula."""
        for user in self.get_all():
            if user.id == user_id:
                return user
        return None
    
    
    def get_all(self) -> List[User]:
        """Obtiene todos los elementos registrados."""
        with open(self.file_path, "r") as f:
            data = json.load(f)
        return [User(**item) for item in data]
    

class JSONAttendanceRepository(AttendanceRepositoryPort):
    """
    Adaptador de almacenamiento en formato JSON para los Registros de Asistencia.
    """

    def __init__(self, file_path: str = "infra/data/attendance.json"):
        self.file_path = file_path

        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    
    def save(self, record: AttendanceRecord) -> None:
        """Guarda un nuevo registro de entrada/salida."""

        records_data = self._read_all()
        # Convertir el objeto datetime a string formato ISO para que JSON lo soporte.
        record_dict = vars(record).copy()
        record_dict['timestamp'] = record.timestamp.isoformat()

        records_data.append(record_dict)
        with open(self.file_path, "w") as f:
            json.dump(records_data, f, indent=4)

    
    def get_daily_records(self, target_date: date) -> list[AttendanceRecord]:
        """Filtra y devuelve los registros correspondientes a una fecha exacta."""
        daily_records = []

        for item in self._read_all():
            # Reconstruir el objeto datetime desde el string guardado
            dt = datetime.fromisoformat(item['timestamp'])
            if dt.date() == target_date:
                item_copy = item.copy()
                item_copy['timestamp'] = dt
                daily_records.append(AttendanceRecord(**item_copy))

        return daily_records
    

    def get_last_record_for_user(self, user_id: str) -> Optional[AttendanceRecord]:
        """Implementación del puerto para buscar la última situación del usuario."""

        records = self._read_all()
        user_records = [r for r in records if r['user_id'] == user_id]

        if not user_records: 
            return None

        # Ordenar por fecha y hora (el más reciente al final)
        user_records.sort(key=lambda x: x['timestamp'])
        last_record_data = user_records[-1]

        # reconstruir la entidad
        dt = datetime.fromisoformat(last_record_data['timestamp'])
        last_record_data['timestamp'] = dt
        return AttendanceRecord(**last_record_data)

    
    def _read_all(self) -> List[dict]:
        """Método auxiliar interno para leer el JSON crudo."""
        with open(self.file_path, "r") as f:
            return json.load(f)