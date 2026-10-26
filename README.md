# Sistema Web de Votaciones — Festival de la Leyenda Vallenata 2027

Proyecto académico de la asignatura Desarrollo Web, Entrega 2. La aplicación está pensada para organizar las ediciones, categorías, votaciones y opciones del Festival de la Leyenda Vallenata 2027.

## Estado

La base del proyecto fue ejecutada y comprobada localmente en Windows
con Python 3.13.15, Django 5.2.18, mysqlclient 2.3.0 y MySQL 8.4.9.

Verificado:
- Comprobación de Django sin errores.
- Conexión con MySQL mediante el usuario de la aplicación.
- Generación y aplicación de las migraciones.
- Creación del superusuario y acceso a Django Admin.
- Inserción de datos ficticios mediante el ORM.
- Consulta de las opciones de prueba desde Django Admin.

Se incluyen la migración inicial y los datos de prueba de la aplicación.
No se incluyen usuarios, contraseñas ni la base de datos local.

Siguen pendientes la autenticación pública, las interfaces públicas,
las pruebas adicionales y las evidencias de la entrega.

Django y las dependencias de requirements.txt son necesarios
para ejecutar el proyecto.

## Qué quedó preparado

- Proyecto Django con el paquete de configuración `config` y la aplicación `votaciones`.
- Modelos `Edicion`, `Categoria`, `Votacion` y `Opcion`.
- Registro de esos modelos en Django Admin.
- Única ruta configurada: `/admin/`.
- Carpetas `templates/`, `static/css/` y `docs/` (conservadas en Git con `.gitkeep`).
- `requirements.txt` con rangos iniciales de Django y `mysqlclient`.
- `.env.example` con nombres de variables y valores de ejemplo, sin credenciales reales.
- `.gitignore` para excluir entornos virtuales, secretos, archivos de editor y datos locales.

No hay registro de votos, inicio de sesión propio, interfaces públicas ni datos de prueba.

## Instalación del entorno

Crear y activar un entorno virtual antes de instalar dependencias.

macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

`mysqlclient` suele necesitar bibliotecas del sistema además del paquete de Python. En el equipo donde se vaya a ejecutar el proyecto puede hacer falta, según el sistema:

- Windows: un cliente de desarrollo de MySQL (por ejemplo MySQL Connector/C o la instalación de MySQL que incluya las bibliotecas de cliente) para que el compilador o la rueda encuentre los encabezados y las DLL.
- macOS: `mysql-client` o MySQL, a menudo mediante Homebrew, y las variables de compilación que indique el instalador si `pip` no encuentra una rueda compatible.
- Linux: los paquetes de desarrollo del cliente MySQL y de Python (por ejemplo `default-libmysqlclient-dev`, `pkg-config` y los encabezados de Python) antes de instalar `mysqlclient`.

Esas dependencias del sistema no forman parte de este repositorio y hay que resolverlas en cada computador.

Los rangos de `requirements.txt` son un punto de partida. Cuando el equipo ejecute la instalación, conviene fijar y documentar las versiones exactas que sí funcionen.

## Variables de entorno

Obligatorias, sin valor predeterminado en el código:

- `DJANGO_SECRET_KEY`
- `MYSQL_PASSWORD`

Con valor predeterminado si no se definen:

- `DJANGO_DEBUG` (predeterminado `False`; solo `true` en minúsculas activa el modo depuración)
- `DJANGO_ALLOWED_HOSTS` (predeterminado `localhost,127.0.0.1`, separadas por comas)
- `MYSQL_DATABASE` (predeterminado `votaciones`)
- `MYSQL_USER` (predeterminado `votaciones_app`)
- `MYSQL_HOST` (predeterminado `127.0.0.1`)
- `MYSQL_PORT` (predeterminado `3306`)

`.env.example` no se carga automáticamente. Copiarlo a `.env` no basta: hay que exportar esas variables en la terminal, en el entorno del proceso o con el mecanismo que el equipo acuerde. No subas `.env`, contraseñas ni datos personales. El archivo `.env` ya está ignorado por Git.

Ejemplo de exportación en la sesión actual (sustituye los valores de ejemplo):

macOS o Linux:

```bash
export DJANGO_SECRET_KEY="reemplazar-por-una-clave-local-aleatoria"
export DJANGO_DEBUG="True"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
export MYSQL_DATABASE="votaciones"
export MYSQL_USER="votaciones_app"
export MYSQL_PASSWORD="reemplazar-por-la-contrasena-local"
export MYSQL_HOST="127.0.0.1"
export MYSQL_PORT="3306"
```

Windows (PowerShell):

```powershell
$env:DJANGO_SECRET_KEY = "reemplazar-por-una-clave-local-aleatoria"
$env:DJANGO_DEBUG = "True"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
$env:MYSQL_DATABASE = "votaciones"
$env:MYSQL_USER = "votaciones_app"
$env:MYSQL_PASSWORD = "reemplazar-por-la-contrasena-local"
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3306"
```

## Pasos pendientes para ejecutar

La migración inicial ya está incluida. Después de preparar MySQL
y las variables de entorno, ejecutar:

    python manage.py migrate
    python manage.py loaddata datos_prueba
    python manage.py createsuperuser
    python manage.py runserver

Los datos de prueba son ficticios. Cargarlos en una base local nueva
o revisar antes posibles conflictos con registros existentes.

Comandos previstos, después de tener el entorno y las variables:

```bash
python manage.py makemigrations votaciones
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Nada de esto se ejecutó al preparar esta base.

## Modelos

Definidos en `votaciones.models`:

- `Edicion`
- `Categoria`
- `Votacion`
- `Opcion`

Relaciones preparadas:

- `edicion.categorias.all()`
- `categoria.votaciones.all()`
- `votacion.opciones.all()`

No existe un modelo `Voto`. El registro definitivo de votos queda fuera de esta fase.

## Autenticación e interfaces

La autenticación propia (registro, inicio y cierre de sesión) y las interfaces públicas todavía no están hechas. La única ruta configurada es `/admin/`. La página pública de la raíz aún no existe.

Está previsto usar el usuario estándar de Django (`django.contrib.auth`). Cualquier usuario personalizado debe acordarse **antes** de las primeras migraciones, porque cambiar el modelo de usuario después complica el historial de la base de datos.

## Coordinación del equipo

Antes de añadir otra aplicación Django, o de modificar `config/settings.py` y `config/urls.py`, avisen en el grupo y revisen la rama compartida. Así se evita pisar `INSTALLED_APPS`, middleware o rutas.

Siguen pendientes los datos de prueba, las pruebas funcionales, las capturas, el informe y el video de la entrega.

## Decisiones preliminares del equipo

Estas decisiones son propuestas de trabajo, no reglas aprobadas por un cliente:

- Una edición por año (`Edicion.anio` es único).
- El nombre de una categoría es único dentro de una misma edición.
- La eliminación está protegida (`on_delete=models.PROTECT`) cuando un registro tiene elementos asociados.

## Credenciales y datos personales

No incluyas contraseñas, claves secretas, certificados ni datos personales de participantes o del equipo en el repositorio. `.env.example` solo contiene marcadores de ejemplo.
