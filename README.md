# Backend - Talbot Hotels API

API REST del sistema de gestión hotelera construida con FastAPI.

## Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **SQLAlchemy** - ORM para base de datos
- **PostgreSQL** - Base de datos principal
- **JWT** - Autenticación con tokens
- **Pydantic** - Validación de datos
- **Docker** - Containerización

## Estructura del Proyecto

```
app/
├── api/
│   ├── routers/
│   │   ├── __init__.py
│   │   └── auth.py          # Endpoints de autenticación
│   └── __init__.py
├── core/
│   ├── __init__.py
│   ├── config.py            # Configuración de la aplicación
│   ├── dependencies.py     # Dependencias de FastAPI
│   └── security.py          # Funciones de seguridad y JWT
├── db/
│   ├── __init__.py
│   └── database.py          # Configuración de base de datos
├── models/
│   ├── __init__.py
│   └── user.py              # Modelos de SQLAlchemy
├── repositories/
│   ├── __init__.py
│   └── user_repository.py   # Operaciones CRUD
├── schemas/
│   ├── __init__.py
│   ├── token.py             # Esquemas de tokens
│   └── user.py              # Esquemas de usuario
├── services/
│   ├── __init__.py
│   └── auth_service.py      # Lógica de negocio
└── __init__.py
main.py                      # Punto de entrada
requirements.txt             # Dependencias
.env.example                 # Variables de entorno de ejemplo
```

## Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone <url-del-repositorio>
   cd talbot
   ```

2. **Crear un entorno virtual:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # En Windows
   # source venv/bin/activate  # En Linux/Mac
   ```

3. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno:**
   ```bash
   copy .env.example .env  # En Windows
   # cp .env.example .env  # En Linux/Mac
   ```
   Edita el archivo `.env` con tus configuraciones.

5. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```
   O usando uvicorn directamente:
   ```bash
   uvicorn main:app --reload
   ```

## Uso

### Documentación de la API

Una vez que la aplicación esté ejecutándose, puedes acceder a:

- **Swagger UI:** http://localhost:8001/docs
- **ReDoc:** http://localhost:8001/redoc

### Endpoints Principales

#### Autenticación

- `POST /api/v1/auth/register` - Registrar nuevo usuario
- `POST /api/v1/auth/login` - Iniciar sesión (form data)
- `POST /api/v1/auth/login-json` - Iniciar sesión (JSON)
- `GET /api/v1/auth/me` - Obtener información del usuario actual
- `POST /api/v1/auth/change-password` - Cambiar contraseña
- `POST /api/v1/auth/logout` - Cerrar sesión
- `GET /api/v1/auth/protected` - Ruta protegida de ejemplo

### Ejemplo de Uso

#### 1. Registrar un usuario
```bash
curl -X POST "http://localhost:8001/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "usuario_test",
       "email": "test@example.com",
       "password": "mi_contraseña_segura",
       "full_name": "Usuario de Prueba"
     }'
```

#### 2. Iniciar sesión
```bash
curl -X POST "http://localhost:8001/api/v1/auth/login-json" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "usuario_test",
       "password": "mi_contraseña_segura"
     }'
```

#### 3. Acceder a ruta protegida
```bash
curl -X GET "http://localhost:8001/api/v1/auth/me" \
     -H "Authorization: Bearer <tu_token_aqui>"
```

## Configuración

### Base de Datos

Por defecto, la aplicación usa SQLite. Para cambiar a PostgreSQL o MySQL:

1. Instala el driver correspondiente:
   ```bash
   # PostgreSQL
   pip install psycopg2-binary
   
   # MySQL
   pip install PyMySQL
   ```

2. Actualiza la variable `DATABASE_URL` en tu archivo `.env`:
   ```bash
   # PostgreSQL
   DATABASE_URL="postgresql://usuario:contraseña@localhost/nombre_db"
   
   # MySQL
   DATABASE_URL="mysql+pymysql://usuario:contraseña@localhost/nombre_db"
   ```

### Seguridad

⚠️ **Importante:** Cambia la `SECRET_KEY` en el archivo `.env` antes de usar en producción.

## Desarrollo

### Ejecutar en modo desarrollo
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

### Estructura de Archivos

- **models/**: Modelos de base de datos (SQLAlchemy)
- **schemas/**: Esquemas de validación (Pydantic)
- **repositories/**: Capa de acceso a datos
- **services/**: Lógica de negocio
- **api/routers/**: Endpoints de la API
- **core/**: Configuración y utilidades centrales

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT.