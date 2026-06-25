from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """
    Representa a un elemento naval registrado en el sistema.
    """
    id: str         # Matrícula  (Identificador único)
    grade: str      # Grado militar (ej. Teniente de Navío)
    name: str       # Nombre Completo
    assignment: str # Adscripción a la que pertenece.
    role: str       # Cargo
    face_encoding_path: Optional[str] = None    # Ruta donde se guardará la referencia facial

@dataclass
class AttendanceRecord:
    """
    Represneta un registro individual de entrada o salida.
    """
    user_id: str        # Matrícula del elemento
    timestamp: datetime # Fecha y hora exacta del registro
    is_entry: bool      # True es para entrada, false para salida.
    reason: str = "Ingreso a labores" # Motivo por defecto.
    location: str = ""  # Ubicación dinámica (ej. Puerto Vallarta, Jal...)

"""
Tener estas clases nos asegura que en todo el sistema (desde la IA hasta la API) siempre sabremos exactamente qué forma tiene un Usuario y un Registro, evitando pasar diccionarios desectructurados que causan errores difíciles de rastrear.
"""

