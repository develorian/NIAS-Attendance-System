import os
import cv2
import numpy as np
from typing import Optional
from deepface import DeepFace
from core.ports import FaceRecognitionPort

class DeepFaceAdapter(FaceRecognitionPort):
    """
    Adaptador que envuelve la librería DeepFace.
    Aísla la lógica de reconocimiento facial del núcleo del sistema.
    """

    def __init__(self, db_path: str = "infra/data/faces"):
        self.db_path = db_path
        os.makedirs(self.db_path, exist_ok=True)

    
    def register_face(self, user_id: str, image_frame: bytes) -> str:
        """
        Toma la imagen capturada, la decodifica y la guarda en la carpeta del elemento.
        """

        nparr = np.frombuffer(image_frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        user_dir = os.path.join(self.db_path, user_id)
        os.makedirs(user_dir, exist_ok=True)

        file_path = os.path.join(user_dir, f"{user_id}_base.jpg")
        cv2.imwrite(file_path, img)

        return file_path
    
    
    def identify_face(self, image_frame: bytes) -> Optional[str]:
        """Busca el rostro en la base de datos de rostros usando DeepFace."""
        # return super().identify_face(image_frame)   #### -> Esto está bien?

        nparr = np.frombuffer(image_frame, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        try:
            # enforce_detection=False evita que el programa colapse si no hay rostros claros en el frame
            dfs = DeepFace.find(img_path = img, db_path = self.db_path, enforce_detection = False, silent=True)

            if len(dfs) > 0 and not dfs[0].empty:
                # Extraemos la ruta del rostro que hizo match
                matched_path = dfs[0].iloc[0]['identity']

                # Extraemos la matrícula (el nombre de la carpeta).
                normalized_path = os.path.normpath(matched_path)
                user_id = normalized_path.split(os.sep)[-2]

                return user_id
            
        except Exception as e:
            print(f"Error de DeepFace: {e}")
            return None
        
        return None