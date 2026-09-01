# Kitty Finanzas

Aplicación web full-stack de finanzas personales con estética anime, gato mascota pixel-art, login/registro, chatbot "Kitty" de consejos financieros y dashboard analítico.

## Funcionalidades
- **Login / Registro de usuario** guardado en MySQL (contraseñas con hash bcrypt).
- **Dashboard analítico:** balance, categoría más costosa, tendencia mensual, predicción (regresión) y anomalías.
- **Chatbot Kitty:** asistente con sprite de gato pixel-art que responde de forma coherente con datos reales (balance, ahorro, gasto más alto, predicción, anomalías).

## Stack
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Backend:** Python con Flask (API REST), PyJWT, bcrypt
- **Base de datos:** MySQL
- **Análisis:** Pandas, Scikit-learn

## Estructura
```
/backend
  /rutas        # Blueprints de la API (incluye auth y chatbot)
  /modelos      # Conexión a BD y módulo de autenticación
  /analitica    # Pandas + Scikit-learn
  app.py
  requirements.txt
/frontend
  index.html       # Login / registro
  dashboard.html   # Panel del usuario (requiere sesión)
  /css
  /js
  /img          # sprite pixel-art de Kitty
/database
  schema.sql
  seed.sql
README.md
```

## Requisitos
- Python 3.8+
- MySQL local (usuario `root` y contraseña configurable por variables de entorno)

## Instalación
1. Crear la base de datos y cargar datos:
   ```bash
   mysql -u root -p < database/schema.sql
   mysql -u root -p < database/seed.sql
   ```
2. Crear entorno virtual e instalar dependencias:
   ```bash
   cd backend
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```
3. Configurar credenciales (opcional): `DB_PASSWORD` (MySQL) y `SECRET_KEY` (JWT).

## Ejecución
```bash
cd backend
python app.py
```
Servidor en `http://localhost:5000`. Abrir `frontend/index.html` en el navegador (al iniciar sesión te redirige a `dashboard.html`, donde también está el botón de cerrar sesión).

## API
| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | /api/usuarios | Crear usuario |
| POST | /api/categorias | Crear categoría |
| GET | /api/categorias?id_usuario= | Listar categorías |
| POST | /api/movimientos | Registrar movimiento |
| GET | /api/movimientos?id_usuario=&desde=&hasta=&categoria= | Listar movimientos |
| PUT | /api/movimientos/{id} | Editar movimiento |
| DELETE | /api/movimientos/{id} | Eliminar movimiento |
| GET | /api/resumen?id_usuario=&mes= | Totales del periodo |
| GET | /api/analitica/estadisticas?id_usuario= | Distribución y tendencia |
| GET | /api/analitica/prediccion?id_usuario= | Predicción próximo mes |
| GET | /api/analitica/anomalias?id_usuario= | Movimientos anómalos |
| POST | /api/auth/register | Registrar usuario (nombre, email, password) |
| POST | /api/auth/login | Iniciar sesión y obtener token JWT |
| GET | /api/auth/me | Datos del usuario autenticado (requiere JWT) |
| POST | /api/chatbot | Mensaje al chatbot Kitty, responde de forma coherente con datos reales |
