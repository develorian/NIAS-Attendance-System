from flask import request
from flask_restful import Resource
import base64

class UserRegisterResource(Resource):
    def __init__(self, **kwargs):
        # Inyectamos el servicio central
        self.service = kwargs.get('service')
        super().__init__()

    def post(self):
        """
        Registra un nuevo elemento naval.
        Recibe los datos del elemento y una fotografía en base64 para extraer la biometría facial y darlo de alta en el sistema.
        ---
        tags:
          - Administración
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - id
                - name
                - image_b64
              properties:
                id:
                  type: string
                  description: Matrícula del elemento
                grade:
                  type: string
                  description: Grado militar (ej. Teniente de Navío)
                name:
                  type: string
                  description: Nombre completo
                assignment:
                  type: string
                  description: Adscripción
                role:
                  type: string
                  description: Cargo
                image_b64:
                  type: string
                  description: Fotografía capturada por la cámara en formato base64
        responses:
          201:
            description: Elemento registrado exitosamente.
          400:
            description: Faltan datos o imagen.
          500:
            description: Error interno del servidor.
        """
        data = request.json
        if not data or 'image_b64' not in data:
            return {"mesage": "Faltan datos o imagen"}, 400

        try:
            # Decodificamos la imagen en base64 enviada desde el navegador web
            base64_str = data['image_b64']
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            image_bytes = base64.b64decode(base64_str)

            user = self.service.register_element(
                user_id=data['id'],
                grade=data['grade'],
                name=data['name'],
                assignment=data['assignment'],
                role=data['role'],
                image_frame=image_bytes
            )
            return {"message": "Elemento registrado exitosamente", "user_id": user.id}, 201
        
        except Exception as e:
            return {"message": f"Error interno al registrar: {str(e)}"}, 500
        

class AttendanceResource(Resource):
    def __init__(self, **kwargs):
        self.service = kwargs.get('service')
        super().__init__()

    
    def post(self):
        """
        Registra un pase de lista (Entrada o Salida).
        Identifica al usuario mediante biometría facial y registra su movimiento, tomando en cuenta su ubicación GPS.
        ---
        tags:
          - Pase de Lista
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              required:
                - image_b64
              properties:
                image_b64:
                  type: string
                  description: Fotografía capturada en formato base64
                is_entry:
                  type: boolean
                  description: true para entrada, false para salida
                reason:
                  type: string
                  description: Motivo del movimiento (ej. Ingreso a labores, Comisión)
                location:
                  type: string
                  description: Ubicación detectada por el GPS
        responses:
          200:
            description: Registro procesado exitosamente.
          400:
            description: Faltan datos o imagen.
          404:
            description: Rostro no reconocido o no se encuentra en el sistema.
          500:
            description: Error interno al procesar el registro.
        """
        data = request.json
        if not data or 'image_b64' not in data:
            return {"message": "Faltan datos o imagen"}, 400
        
        try:
            base64_str = data['image_b64']
            if ',' in base64_str:
                base64_str = base64_str.split(',')[1]
            image_bytes = base64.b64decode(base64_str)

            # El frontend enviará la ubicación dictada por el GPS del dispositivo
            record = self.service.process_attendance(
                image_frame=image_bytes,
                is_entry=data.get('is_entry', True),
                reason=data.get('reason', 'Ingreso a labores'),
                location_city_state=data.get('location', 'Ubicación Desconocida')
            )

            if record:
                movimiento = 'Entrada' if record.is_entry else 'Salida'
                return {
                    "message": "Registro exitoso",
                    "user_id": record.user_id,
                    "movimiento": movimiento,
                    "timestamp": record.timestamp.strftime("%H:%M hrs (%d/%m/%Y)"),
                    "ubicacion_oficial": record.location
                }, 200
            else:
                return {"message": "Rostro no reconocido. Acceso denegado."}, 404
            
        except Exception as e:
            return {"message": f"Error al procesar asistencia: {str(e)}"}, 500
        

class SituationReportResource(Resource):
    def __init__(self, **kwargs):
        self.service = kwargs.get('service')
        super().__init__()

    def get(self):
        """
        Obtiene el reporte de situación en tiempo real.
        Este endpoint devuelve la lista del personal a bordo y fuera de la unidad.
        ---
        tags:
          - Reportes
        responses:
          200:
            description: Operación exitosa. Devuelve el JSON con la situación.
        """
        situacion = self.service.get_current_situation()
        return situacion, 200


class DailyReportResource(Resource):
    def __init__(self, **kwargs):
        self.service = kwargs.get('service')
        super().__init__()


    def get(self):
        """
        Obtiene todos los movimientos del día.
        Lista completa de entradas y salidas registradas durante el día actual.
        ---
        tags:
          - Reportes
        responses:
          200:
            description: Lista de movimientos navales.
        """
        # Genera la lista de todos los movimientos del día
        # situation = self.service.get_current_situation() # Esto lo arrojo copilot de VSCode ¿Es correcto?
        records = self.service.get_daily_report()
        # Convertimos las dataclases a diccionarios para que Flask pueda devolverlas como JSON
        return [vars(r) for r in records], 200