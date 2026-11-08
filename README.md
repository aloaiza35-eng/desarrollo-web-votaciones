# Plataforma de Votaciones - Festival de la Leyenda Vallenata 2027

Proyecto académico de Desarrollo Web, Fundación Universitaria del Área Andina.
Entrega 3: módulo de votaciones, validaciones y API GET sobre la base del Eje 2.
Los datos y votos de demostración no tienen validez oficial en el Festival.

## Funcionalidades

- Registro, inicio y cierre de sesión con el usuario estándar de Django.
- Catálogo dinámico: edición → categoría → votación/subevento → opción.
- Selección de una opción y pantalla de confirmación antes de guardar el voto.
- Un voto por usuario, categoría y edición, incluso entre diferentes subeventos.
- Participación permitida en otras categorías y ediciones.
- Validación del servidor: autenticación, categoría y subevento habilitados,
  pertenencia de la opción, CSRF y control de duplicados.
- Historial privado en Mi participación y votos de solo lectura en Django Admin.
- API pública de consulta `GET /api/categorias/`, sin datos de usuarios ni votos.

## Tecnologías y versiones

Python, Django 5.2, patrón MVT y MySQL. El controlador es `mysqlclient`.
`requirements.txt` contiene las dependencias de la aplicación; no se usa
python-dotenv, PyMySQL, Django REST Framework ni Bootstrap.
El CSS es propio. No se necesita Docker.

La base del Eje 2 se verificó en Windows con Python 3.13.15, Django 5.2.18,
mysqlclient 2.3.0 y MySQL 8.4.9. Los resultados específicos de la nueva versión,
sus entornos y límites se registran en [Pruebas del Eje 3](docs/pruebas_eje3.md).
No confundir las pruebas históricas del Eje 2 con las del módulo de votos.

## 1. Descargar el proyecto

Clonar una sola vez. En Windows CMD, por ejemplo:

```bat
cd /d "%USERPROFILE%"
if not exist Universidad mkdir Universidad
cd Universidad
git clone https://github.com/aloaiza35-eng/desarrollo-web-votaciones.git
cd desarrollo-web-votaciones
```

Si ya está clonado, entrar a su carpeta, guardar los cambios propios y actualizar
la rama compartida con `git pull --ff-only origin main`. No reemplazar carpetas
ni volver a clonar encima del trabajo existente. Mientras el Eje 3 esté en una
rama de desarrollo, usar la rama acordada por el equipo.

## 2. Crear el entorno e instalar dependencias

Trabajar siempre en la raíz donde está `manage.py`. No compartir `.venv`.

Windows CMD, primera instalación:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

PowerShell: activar con `.\.venv\Scripts\Activate.ps1`.

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Si mysqlclient no encuentra una rueda compatible, necesita bibliotecas de cliente,
encabezados y compilador de la plataforma. En Ubuntu/Debian se suelen instalar
`python3-dev default-libmysqlclient-dev build-essential pkg-config`. En macOS se
necesitan MySQL o mysql-client y pkg-config, y las rutas de compilación de esa
instalación. En la instalación Windows del equipo se utilizó una rueda compatible.

## 3. Preparar MySQL

Instalar e iniciar el servicio MySQL. Cada integrante prepara su propia base y su
propio usuario; Git no incluye la base local ni usuarios administradores.
Quien ya tiene la base del Eje 2 debe conservarla y pasar al paso 4.

Abrir el cliente de MySQL con una cuenta que pueda crear la base y el usuario.
En el equipo Windows del proyecto, la ruta del cliente es:

```bat
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -h 127.0.0.1 -u root -p
```

En la consola `mysql>`, ejecutar el siguiente SQL. **Antes de copiar la sentencia
CREATE USER, reemplazar `TU_CONTRASENA_ELEGIDA` por la contraseña local que se haya
elegido. Es un marcador de ejemplo, no una contraseña proporcionada por el equipo.**

```sql
CREATE DATABASE votaciones CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'votaciones_app'@'localhost' IDENTIFIED BY 'TU_CONTRASENA_ELEGIDA';
GRANT ALL PRIVILEGES ON votaciones.* TO 'votaciones_app'@'localhost';
EXIT;
```

No repetir CREATE DATABASE/CREATE USER si ya existen. No usar root como usuario
normal de la aplicación. Comprobar la conexión con el usuario de la aplicación:

```bat
"C:\Program Files\MySQL\MySQL Server 8.4\bin\mysql.exe" -h 127.0.0.1 -u votaciones_app -p votaciones
```

Después de entrar, salir con `EXIT;` para continuar en CMD.

## 4. Variables de entorno

| Variable | Valor o función |
| --- | --- |
| DJANGO_SECRET_KEY | Obligatoria: clave secreta privada de Django |
| MYSQL_PASSWORD | Obligatoria: contraseña del usuario MySQL de la aplicación |
| DJANGO_DEBUG | False por defecto; True solo para desarrollo local |
| DJANGO_ALLOWED_HOSTS | localhost,127.0.0.1 por defecto |
| MYSQL_DATABASE | votaciones por defecto |
| MYSQL_USER | votaciones_app por defecto |
| MYSQL_HOST | 127.0.0.1 por defecto |
| MYSQL_PORT | 3306 por defecto |

`.env.example` documenta los nombres y contiene solo ejemplos. **La aplicación no
carga archivos .env automáticamente:** copiarlo a `.env` no configura las variables.
No subir contraseñas, tokens, claves privadas ni archivos con credenciales.

### Windows CMD: configuración para la sesión actual

Desde la raíz del proyecto, con `.venv` activo:

```bat
set "DJANGO_DEBUG=True"
set "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1"
set "MYSQL_DATABASE=votaciones"
set "MYSQL_USER=votaciones_app"
set "MYSQL_HOST=127.0.0.1"
set "MYSQL_PORT=3306"
python -c "import os,secrets,getpass,subprocess; os.environ['DJANGO_SECRET_KEY']=secrets.token_urlsafe(50); os.environ['MYSQL_PASSWORD']=getpass.getpass('Password de votaciones_app: '); subprocess.call(['cmd.exe','/D'])"
```

El último comando solicita la contraseña de `votaciones_app` sin mostrarla.
No es la contraseña de root ni la del usuario de Django. Continuar en la consola
CMD hija que abre este comando, donde las variables están disponibles.

La clave Django de este método es temporal para desarrollo. Repetirlo cambia la
clave y puede invalidar sesiones anteriores; los datos de MySQL se conservan.
Para mantener sesiones entre reinicios, configurar una clave estable y privada en
el entorno local del proceso. No guardarla en archivos compartidos.

En una terminal nueva, activar el entorno y repetir la configuración de variables.
Activar `.venv` por sí solo no configura MySQL ni la clave Django.

### PowerShell y macOS/Linux

Definir los mismos nombres con `$env:NOMBRE = "valor"` en PowerShell o con
`export NOMBRE="valor"` en bash/zsh. Generar una clave privada con
`python -c "import secrets; print(secrets.token_urlsafe(50))"` y configurarla como
DJANGO_SECRET_KEY local. Introducir MYSQL_PASSWORD solo en el equipo propio;
no compartir el historial ni capturas de credenciales.

## 5. Migraciones, datos de prueba y administrador

Con MySQL iniciado y las variables configuradas:

```bash
python manage.py check
python manage.py migrate
python manage.py preparar_demo_eje3
```

La migración `0002_categoria_habilitada_votacion_habilitada_voto` agrega estados y
el modelo Voto. Conserva la migración inicial y los registros del Eje 2.
No generar otra migración inicial ni borrar la base anterior.

Por defecto, las categorías existentes quedan **cerradas**. Abrir las necesarias
en Admin marcando `Habilitada`. Los subeventos también tienen su propia casilla;
ambos deben estar habilitados para aceptar un voto.

`preparar_demo_eje3` agrega, en la edición 2027:

- Demo - Acordeón, habilitada: dos subeventos y tres opciones para probar duplicados.
- Demo - Canción, habilitada: otra categoría con dos opciones para permitir otro voto.
- Demo - Cerrada, deshabilitada: una opción para comprobar el rechazo.

El comando se puede repetir: no elimina datos, no reinicia votos, no crea usuarios
y no modifica el estado de categorías que ya existían. Si se cerró una categoría
de demostración, habilitarla de nuevo manualmente en Admin cuando corresponda.

Crear el administrador local una sola vez:

```bash
python manage.py createsuperuser
```

El fixture histórico `datos_prueba` sigue disponible. Contiene cinco registros,
usa identificadores fijos y puede sobrescribir datos con esos identificadores.
Cargarlo solo en una base nueva o tras revisar posibles conflictos; no hace falta
cargarlo para usar el comando de demostración del Eje 3.

## 6. Ejecutar

```bash
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ y mantener la terminal abierta.
Para los siguientes inicios: entrar a la carpeta, activar `.venv`, configurar
variables y ejecutar runserver. Después de actualizar código compartido, ejecutar
`python manage.py migrate`. No reinstalar MySQL ni borrar los datos en cada inicio.

## Rutas y recorrido

| Ruta | Uso |
| --- | --- |
| / | Inicio público |
| /ediciones/ | Catálogo de ediciones |
| /ediciones/ID/ | Categorías de una edición |
| /categorias/ID/ | Subeventos de una categoría |
| /votaciones/ID/ | Opciones de un subevento |
| /categorias/ID/votar/ | Selección y confirmación; requiere sesión |
| /mi-participacion/ | Historial del usuario autenticado |
| /cuentas/registro/ | Crear cuenta |
| /cuentas/ingresar/ | Iniciar sesión |
| /cuentas/mi-cuenta/ | Cuenta privada |
| /cuentas/salir/ | Cierre de sesión por POST desde el botón |
| /admin/ | Administración; requiere permisos |
| /api/categorias/ | Consulta JSON pública por GET |

Recorrido: entrar con una cuenta pública → edición 2027 → Demo - Acordeón →
elegir opción → revisar → confirmar → Mi participación. Intentar votar en el otro
subevento de Demo - Acordeón debe fallar. Demo - Canción debe permitir otro voto.
Para repetir la demostración completa, registrar otro usuario; no borrar votos.

## API GET

Código: `votaciones/api.py`. Ruta registrada en `config/urls.py`.
Devuelve `{"categorias": [...]}` con id, nombre, descripción, estado, edición y
opciones de cada categoría. Cada opción identifica su votación/subevento y estado.
Incluye categorías cerradas indicando su estado; excluye registros archivados y no expone cuentas ni votos.

- GET `/api/categorias/`: categorías y opciones activas.
- GET `/api/categorias/?edicion=ID`: filtro opcional por identificador de edición.
- Filtro inválido: HTTP 400. Métodos de escritura: HTTP 405.
- Catálogo vacío: `{"categorias": []}`.

Abrir en el navegador o en Postman. `localhost` es solo accesible en el computador
que ejecuta el servidor; para la evaluación, demostrar la API en video e incluir
captura del JSON e instrucciones de ejecución. No hay API POST de voto.

## Integridad y administración

`votaciones/models.py`: Voto relaciona usuario, categoría y opción; fecha automática.
La edición se obtiene de `voto.categoria.edicion`. Cada categoría pertenece a una
única edición, por lo que UNIQUE(usuario, categoria) garantiza la regla por usuario,
categoría y edición sin mantener una edición duplicada que pueda contradecirse.
La restricción en la BD se llama `voto_unico_usuario_categoria`.

`votaciones/services.py`: transacción, bloqueo de la categoría por PK con
`select_for_update()`, revalidación del estado y de la opción, creación y manejo
específico de duplicados. El bloqueo mantiene breve y ordenado el flujo de
confirmación en una categoría; el índice único es la protección final en la BD.

`votaciones/forms.py` limita opciones a la categoría y a subeventos habilitados.
`votaciones/views.py` exige sesión y POST con CSRF para guardar. El usuario se
obtiene de la sesión, no de campos enviados por el navegador.

Los votos son de solo lectura en Admin: no se pueden crear, editar ni borrar desde
ese panel. Los registros referenciados usan PROTECT. Admin y las validaciones de
modelos impiden reasignar a otra edición/categoría/subevento registros con votos.
Los scripts administrativos también deben respetar el servicio y estas relaciones;
las actualizaciones SQL directas o bulk del catálogo omiten validaciones de Django.

## Pruebas

Pruebas rápidas y aisladas con SQLite en memoria:

```bash
python manage.py test cuentas votaciones --settings=config.test_settings
```

CP-09 se omite deliberadamente en SQLite: no demuestra bloqueos reales de MySQL.
No ejecutar la aplicación con test_settings para sustituir la base requerida.

Suite con MySQL real y base separada `test_votaciones`:

```bash
python manage.py test cuentas votaciones --settings=config.test_mysql_settings
```

Esa cuenta debe poder crear y eliminar **solo la base de pruebas** además de usar
la base de la aplicación. Para el usuario local de este ejemplo, un administrador
puede otorgar permisos limitados con:

```sql
GRANT ALL PRIVILEGES ON test_votaciones.* TO 'votaciones_app'@'localhost';
```

Django crea y elimina test_votaciones. Reservar ese nombre para pruebas, nunca
para datos que se necesiten conservar. No conceder permisos globales.
No usar `config.test_mysql_settings` para servir la aplicación; utiliza un hasher
rápido exclusivo de tests. CP-09 usa dos clientes, conexiones e hilos separados.
Procedimientos, resultados y correspondencia CP-01 a CP-10:
[docs/pruebas_eje3.md](docs/pruebas_eje3.md).

## Errores frecuentes

- KeyError DJANGO_SECRET_KEY o MYSQL_PASSWORD: faltan variables en esa terminal;
  repetir la configuración y continuar en la consola hija.
- Access denied: revisar la cuenta MySQL y su contraseña.
- Error al conectar al puerto 3306: comprobar el servicio MySQL.
- Table does not exist / Unknown column: ejecutar las migraciones compartidas.
- No migrations to apply: la base ya está al día; es un resultado normal.
- Categoría cerrada: habilitarla en Admin, junto con el subevento correspondiente.
- Ya registraste un voto: la regla también cubre los otros subeventos de la categoría.

## Organización y entrega

- `config/`: configuración, rutas y configuraciones exclusivas de pruebas.
- `cuentas/`: registro y autenticación.
- `votaciones/`: modelos, servicio de voto, formularios, vistas, API, gestión y tests.
- `templates/` y `static/css/`: páginas y estilos.
- `docs/pruebas_eje3.md`: pruebas y verificaciones del Eje 3.
- Documentos `parte_1` y `validacion_eje2` en docs: históricos de la entrega anterior.

Pendientes de entrega: verificar la versión en Windows, reunir evidencias del equipo,
grabar el video (máximo ocho minutos), registrar sus minutos reales y preparar el
PDF con ficha de acceso después de la portada. Los cuatro integrantes deben enviar
individualmente el mismo PDF. Mantener coherencia entre código, pruebas y video;
identificar el commit entregado. No publicar resultados oficiales, información
personal ni credenciales. Reglas avanzadas de elegibilidad y despliegue productivo
no se implementan en esta entrega.

## Panel propio de gestión del festival

El personal autorizado usa `/gestion/` desde el enlace **Administrar**. Permite
crear y editar ediciones, categorías, subeventos y opciones; consultar votos;
y consultar y descargar un informe CSV con cantidades por categoría.
El CSV es un informe académico de participación, no una publicación oficial
ni un informe de resultados electorales. No incluye nombres de usuarios.

Para acceder se necesita una cuenta activa marcada como personal (`is_staff`).
El superusuario ya creado dispone de acceso; una cuenta registrada públicamente
no. Las modificaciones requieren POST con token CSRF. La página de votos es de
solo lectura. El administrador técnico puede seguir usando `/admin/` para asignar
permisos de personal, pero no es necesario usarlo para gestionar el catálogo.

En las cuatro secciones, **Archivar** pide confirmación y oculta el elemento del
catálogo público y la API conservando el registro y los votos. Archivar un padre
oculta también sus descendientes; se pueden restaurar desde el panel. Si un padre
continúa archivado, restaurar solo el hijo no lo hace visible. `Habilitada` es
una decisión distinta: controla si una categoría o subevento acepta votos.
Los votos conservan sus relaciones; no se pueden reasignar relaciones con votos.
El archivo lógico básico no constituye una auditoría completa de cambios.

La migración `0003` agrega el campo `activo` con valor inicial verdadero a los
cuatro tipos del catálogo para conservar visibles los registros existentes.
Después de actualizar a esta versión y antes de ejecutar el servidor:

```bash
python manage.py migrate
```

Comprobar las altas, ediciones, archivo y restauración, el CSV, el catálogo público
 y los diez casos de voto en el entorno MySQL del equipo. Detalles y resultados
separados por versión en `docs/pruebas_gestion.md` y `docs/pruebas_eje3.md`.
