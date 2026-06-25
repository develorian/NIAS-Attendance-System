# NIAS — Naval Identity & Attendance System

Sistema de asistencia por reconocimiento facial para elementos navales. Construido con Python, DeepFace y Flask, siguiendo principios de **Arquitectura Hexagonal** (Puertos y Adaptadores).

## Características

- **Registro biométrico** — Alta de elementos navales con captura facial de referencia.
- **Pase de lista facial** — Identificación en tiempo real por coincidencia biométrica.
- **Ubicación dinámica** — Formato oficial naval: `"Ciudad, Estado, a 23 de junio del 2026."`
- **Reporte de situación** — Estado en tiempo real: quién está "A bordo" y quién está "Fuera".
- **Reporte diario** — Registro completo de movimientos del día.
- **Frontend integrado** — Interfaz de administrador y guardia servida desde Flask.

## Arquitectura

```
core/            → Dominio puro (sin dependencias externas)
  entities.py    → User, AttendanceRecord (dataclasses)
  ports.py       → Interfaces abstractas (repositorios, reconocimiento facial)
  services.py    → NavalAttendanceService (casos de uso)

infra/           → Adaptadores concretos
  deepface_adapter.py → Reconocimiento facial (DeepFace)
  json_repository.py  → Almacenamiento en JSON

api/             → Capa de presentación (Flask + flask-restful)
  app.py         → Ensamblaje, endpoints, cron job
  routes.py      → Recursos RESTful

ui/              → Frontend estático (HTML/JS)
  index.html     — Paneles de Admin y Pase de Lista
```

## Instalación local

### Requisitos

- Python 3.11+
- pip

### Pasos

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/nias_system.git
cd nias_system

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor
python api/app.py
```

El servidor arranca en `http://0.0.0.0:5000`. El frontend se sirve automáticamente en la raíz.

### Prueba sin DeepFace

```bash
python test_local.py
```

Usa un `MockFaceAdapter` que simula el reconocimiento facial sin cámara ni GPU.

## Despliegue con Docker

### Construir y ejecutar

```bash
docker compose up -d
```

El servidor queda disponible en `http://localhost:8000`.

### Despliegue en Dokploy

1. Conectar el repositorio GitHub en Dokploy.
2. Seleccionar **Build type: Dockerfile**.
3. Configurar el dominio (ej. `asistencia.develorian.dev`).
4. Habilitar **HTTPS** (Let's Encrypt automático).
5. Puerto interno: `8000`.
6. Desplegar.

Los datos se almacenan en un volumen Docker (`nias_data`) para persistencia.

## API Endpoints

| Método | Ruta | Descripción | Respuesta |
|--------|------|-------------|-----------|
| `POST` | `/api/v1/users` | Registra elemento naval con imagen | `201` / `400` |
| `POST` | `/api/v1/attendance` | Pase de lista facial (entrada/salida) | `200` / `404` |
| `GET` | `/api/v1/reports/situation` | Situación en tiempo real (a bordo/fuera) | `200` |
| `GET` | `/api/v1/reports/daily` | Reporte diario de movimientos | `200` |

### Ejemplo: Registrar elemento

```bash
curl -X POST http://localhost:8000/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "id": "123456",
    "grade": "Teniente de Navío",
    "name": "Juan Pérez",
    "assignment": "Batallón 1",
    "role": "Comandante",
    "image_b64": "data:image/jpeg;base64,/9j/4AAQ..."
  }'
```

### Ejemplo: Pase de lista

```bash
curl -X POST http://localhost:8000/api/v1/attendance \
  -H "Content-Type: application/json" \
  -d '{
    "image_b64": "data:image/jpeg;base64,/9j/4AAQ...",
    "is_entry": true,
    "reason": "Ingreso a labores",
    "location": "Puerto Vallarta, Jal."
  }'
```

## Notas sobre DeepFace

DeepFace descarga pesos pre-entrenados (VGG-Face, Facenet, etc.) en la primera ejecución. Se requiere conexión a internet la primera vez. Los pesos se cachean en `~/.deepface/`.

## Stack tecnológico

- **Backend:** Python, Flask, flask-restful, flask-cors
- **IA:** DeepFace, OpenCV, TensorFlow/Keras
- **Almacenamiento:** JSON (archivos locales)
- **Frontend:** HTML5, JavaScript vanilla, Geolocation API
- **Despliegue:** Docker, gunicorn, Dokploy

## Licencia

Proyecto privado — Hybridge / Develorian.
