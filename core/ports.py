"""
En la Arquitectura Hexagonal, un "Puerto" es simplemente una interfaz (o clase abstracta en Python). Es un contrato que dice qué necesitamos que haga la base de datos o la IA, pero no cómo lo hace.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from .entities import User, AttendanceRecord

class UserRepositoryPort(ABC):
    """
    Puerto (Interfaz) para el almacenamiento de usuarios.
    Cualquier base de datos que usemos en el futuro debe cumplir con este contrato.
    """

    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def get_all(self) -> List[User]:
        pass


class AttendanceRepositoryPort(ABC):
    """
    Puerto (Interfaz) para el almacenamiento de los registros de asistencia.
    """
    
    @abstractmethod
    def save(self, record: AttendanceRecord) -> None:
        pass

    @abstractmethod
    def get_daily_records(self, target_date: date) -> List[AttendanceRecord]:
        """Obtiene todos los registros de una fecha específica."""
        pass

    @abstractmethod
    def get_last_record_for_user(slf, user_id: str) -> Optional[AttendanceRecord]:
        """Obtiene el último registro de un usuario para saber si está a bordo o no."""
        pass

    
class FaceRecognitionPort(ABC):
    """
    Puerto para el motor de visión por computadora.
    Aísla la dependencia de DeepFace o cualquier otra librería futura.
    """

    @abstractmethod
    def register_face(self, user_id: str, image_frame: bytes) -> str:
        """Guarda el rostro y retorna la ruta del archivo o encoding."""
        pass

    @abstractmethod
    def identify_face(self, image_frame: bytes) -> Optional[str]:
        """Analiza un frame y retorna la matrícula (user_id) si hay coincidencias."""
        pass

"""
Si después queremos cambiar la base de datos en memoria por PostgreSQL, o cambiar DeepFace por otra librería de IA, gracias a estos contratos, solo tendré que escribir un nuevo "adaptador" que herede de estas clases, y el resto del sistema ni se enterará del cambio. Es la clave para que el código sea verdaderamente agnóstico.

Capa de Dominio está completa. No tiene dependencias ni librerías externas, solo Python puro.
"""