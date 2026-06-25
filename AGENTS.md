# AGENTS.md — NIAS

## Arranque rápido

```bash
python api/app.py        # Sirve en http://0.0.0.0:5000
python test_local.py     # Prueba manual sin DeepFace (usa MockFaceAdapter)
```

No hay `requirements.txt` ni `pyproject.toml`. Dependencias instaladas manualmente:
`Flask flask-restful flask-cors deepface opencv-python pydantic schedule`

## Arquitectura (Hexagonal / Puertos y Adaptadores)

```
core/         → Dominio puro (sin dependencias externas)
  entities.py → User, AttendanceRecord (dataclasses)
  ports.py    → Interfaces abstractas (UserRepositoryPort, AttendanceRepositoryPort, FaceRecognitionPort)
  services.py → NavalAttendanceService (casos de uso, inyección de dependencias)

infra/        → Adaptadores concretos
  deepface_adapter.py → Reconocimiento facial (DeepFace)
  json_repository.py  → Almacenamiento en JSON (users.json, attendance.json)

api/          → Capa de presentación (Flask + flask-restful)
  app.py      → Ensamblaje de componentes, registro de endpoints, cron job
  routes.py   → Recursos RESTful

ui/           → Frontend estático (HTML/JS, sin build)
```

## Convenciones importantes

- **El directorio se llama `infra/`**, no `infrastructure/` (el README dice "infrastructure" pero es incorrecto).
- **Comentarios y docstrings en español**, nombres de funciones/clases/variables en inglés.
- `app.py` usa `sys.path.append` para resolver imports de `core/` e `infra/`. No mover `app.py` de posición.
- Los datos se guardan en `infra/data/` (archivos JSON y carpetas de rostros). Esta carpeta es runtime-generated.
- DeepFace descarga pesos pre-entrenados en la primera ejecución. Requiere internet la primera vez.
- CORS habilitado para todas las rutas (`flask_cors`).
- El scheduler corre en un hilo daemon separado. `debug=False` para evitar doble ejecución por auto-reload.

## Endpoints API

| Método | Ruta                          | Descripción                         |
|--------|-------------------------------|-------------------------------------|
| POST   | `/api/v1/users`              | Registra elemento naval con imagen  |
| POST   | `/api/v1/attendance`         | Pase de lista facial (entrada/salida) |
| GET    | `/api/v1/reports/situation`  | Situación en tiempo real (a bordo/fuera) |
| GET    | `/api/v1/reports/daily`      | Reporte diario de movimientos       |

## Errores conocidos

- `core/ports.py:43` — `get_last_record_for_user` tiene un typo: primer parámetro es `slf` en vez de `self`.
- `api/routes.py:14` — La clave de error dice `"mesage"` en vez de `"message"` (solo en el POST de usuarios).
- `api/app.py:44` — Comentario sugiere duda sobre si `DailyReportResource` está correctamente registrado. Lo está.

## Testing

No hay framework de tests. Solo existe `test_local.py` que usa un `MockFaceAdapter` para simular DeepFace. Ejecutar con `python test_local.py` desde la raíz.

## No hay

- Linter, formatter, typecheck
- CI/CD
- Docker
- `.gitignore`
- Tests automatizados
