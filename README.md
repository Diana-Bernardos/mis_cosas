# Mis cosas

Aplicación Django para gestionar tareas personales con cuentas de usuario, un
calendario mensual y opciones para crear, modificar y eliminar tareas.

## Instalación en Windows

Desde la carpeta raíz del repositorio, abre PowerShell y ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd mis_cosas
python manage.py migrate
python manage.py runserver
```

Abre `http://127.0.0.1:8000/`. Si todavía no tienes cuenta, regístrate en
`http://127.0.0.1:8000/registro/`.

## Clave secreta

En desarrollo, Django utiliza una clave local de respaldo. Para cualquier
despliegue, define `DJANGO_SECRET_KEY` en el entorno antes de iniciar el
servidor. No guardes claves reales en Git.

```powershell
$env:DJANGO_SECRET_KEY = "pega-aqui-una-clave-secreta-generada-para-tu-entorno"
```

La base de datos SQLite se crea en `mis_cosas/db.sqlite3` y está excluida de
Git para no publicar cuentas ni tareas locales. `python manage.py migrate`
crea las tablas necesarias en cada instalación.

## Pruebas

```powershell
cd mis_cosas
python manage.py test mis_tareas
```
