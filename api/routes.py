from flask import request
from flask_restful import Resource
import base64

class UserRegisterResource(Resource):
    def __init__(self, **kwargs):
        # Inyectamos el servicio central
        self.service = kwargs.get('service')
        super().__init__()

    def post(self):
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
        situacion = self.service.get_current_situation()
        return situacion, 200


class DailyReportResource(Resource):
    def __init__(self, **kwargs):
        self.service = kwargs.get('service')
        super().__init__()


    def get(self):
        # Genera la lista de todos los movimientos del día
        # situation = self.service.get_current_situation() # Esto lo arrojo copilot de VSCode ¿Es correcto?
        records = self.service.get_daily_report()
        # Convertimos las dataclases a diccionarios para que Flask pueda devolverlas como JSON
        return [vars(r) for r in records], 200