# Sistema Web de Votaciones del Festival de la Leyenda Vallenata

Entrega 2 de Desarrollo Web. Aplicación Django MVT con MySQL.

## Funcionalidades

- Ediciones, categorías, votaciones y opciones relacionadas y administrables desde Django Admin.
- Inicio público con totales del catálogo obtenidos de la base de datos.
- Recorrido edición → categoría → votación → detalle y opciones, con enlaces y mensajes de catálogo vacío.
- Registro mediante UserCreationForm y el usuario estándar de Django.
- Inicio de sesión mediante LoginView y AuthenticationForm.
- Mi cuenta protegida por sesión y cierre de sesión por POST con CSRF.
- Diseño responsive sin dependencias de estilos o scripts externos.
- Los usuarios registrados públicamente no reciben permisos de administración.

La inscripción académica usa nombre de usuario y contraseña, sin solicitar documentos
ni otros datos personales no confirmados. Esta decisión preliminar no define la
identificación ni elegibilidad del votante definitivo. No registra votos ni calcula resultados.
Django Admin continúa siendo el administrador permitido en este eje.

## Estado de validación

La base inicial se comprobó localmente por Andrés con Python 3.13.15, Django 5.2.18,
mysqlclient 2.3.0 y MySQL 8.4.9: migraciones, acceso a Admin y datos de prueba.

La incorporación de cuentas y catálogo público supera 24 pruebas automatizadas
con Django 5.2.18 en una base SQLite temporal de pruebas. Esto verifica lógica,
formularios, sesiones, permisos, plantillas y consultas ORM; no es una validación
contra MySQL ni de visualización real en móvil. La aplicación normal conserva
MySQL. Andrés también ejecutó las 24 pruebas en Windows y confirmó el recorrido
manual de catálogo, registro, inicio y cierre de sesión con su configuración MySQL.
Cada integrante debe verificar su instalación. Falta reunir las capturas y grabar
el video. Ver docs/validacion_eje2.md.

## Preparar un computador

Trabajar en la raíz que contiene manage.py. Crear un entorno propio; no copiar venv.

Windows CMD:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

macOS o Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Si mysqlclient necesita compilarse, instalar las bibliotecas y herramientas de su
plataforma. En la prueba Windows se instaló una rueda compatible sin compilación.

## MySQL y variables de entorno

Crear una base propia llamada votaciones (utf8mb4) y un usuario votaciones_app con
permisos sobre esa base. Utilizar contraseñas locales propias. La aplicación recibe:

| Variable | Valor predeterminado |
| --- | --- |
| DJANGO_SECRET_KEY | Obligatoria; clave secreta aleatoria del entorno |
| MYSQL_PASSWORD | Obligatoria; contraseña del usuario de la aplicación |
| DJANGO_DEBUG | False; True solo en desarrollo |
| DJANGO_ALLOWED_HOSTS | localhost,127.0.0.1 |
| MYSQL_DATABASE | votaciones |
| MYSQL_USER | votaciones_app |
| MYSQL_HOST | 127.0.0.1 |
| MYSQL_PORT | 3306 |

.env.example documenta los nombres, no contiene credenciales reales y no se carga
automáticamente. Copiarlo a .env no configura por sí solo el proceso.

Windows CMD (reemplazar valores privados localmente y no compartir el historial):

```bat
set "DJANGO_SECRET_KEY=CLAVE_ALEATORIA_LOCAL"
set "MYSQL_PASSWORD=PASSWORD_LOCAL"
set "DJANGO_DEBUG=True"
```

PowerShell: usar `$env:NOMBRE = "valor"`. macOS/Linux: `export NOMBRE="valor"`.
Conservar una clave secreta estable en el entorno local para mantener sesiones
entre reinicios. No guardarla en archivos compartidos ni commits.

## Ejecutar con MySQL

```bash
python manage.py check
python manage.py migrate
python manage.py runserver
```

No hay nuevos modelos ni migraciones para cuentas: usa el usuario estándar y las
migraciones de auth ya compartidas. No regenerar 0001_initial.py.

Abrir http://127.0.0.1:8000/ para las páginas públicas.
Registro: /cuentas/registro/. Login: /cuentas/ingresar/.
Mi cuenta: /cuentas/mi-cuenta/. Logout: botón de formulario POST.
Admin: /admin/ (requiere usuario staff/superusuario).

Opcional en una base de demostración nueva:

```bash
python manage.py loaddata datos_prueba
python manage.py createsuperuser
```

El fixture tiene cinco registros ficticios: una edición, una categoría, una votación
y dos opciones. Sus claves primarias pueden colisionar con datos existentes: no
cargarlo sobre datos importantes sin revisión. No contiene usuarios ni contraseñas.
El participante C creado localmente en Admin no forma parte del fixture compartido.

## Pruebas automatizadas

Pruebas aisladas sin tocar MySQL ni requerir sus credenciales:

```bash
python manage.py test cuentas votaciones --settings=config.test_settings
```

config.test_settings usa SQLite en memoria y un hasher rápido solo para pruebas.
No usar esa configuración para servir la aplicación o presentar la conexión MySQL.

Para probar la misma suite con MySQL, desde un entorno de pruebas y con las
variables configuradas:

```bash
python manage.py test cuentas votaciones
```

Django crea y elimina una base test_votaciones. Usar una cuenta autorizada para
crear/eliminar esa base de pruebas. No ampliar permisos globales del usuario de
la aplicación sin necesidad. El usuario local restringido solo a votaciones puede
no tener permisos suficientes para ejecutar esa suite.

## Organización

- config/: configuración y rutas generales.
- cuentas/: formularios, vistas, rutas y pruebas de autenticación.
- votaciones/: modelos, administración, vistas, rutas y pruebas del catálogo.
- templates/: base, cuentas, catálogo y página 404.
- static/css/festival.css: estilos del sitio público.
- docs/validacion_eje2.md: evidencias y validación pendiente con MySQL.

Coordinar cambios en settings.py, urls.py y modelos antes de integrar otras ramas.
No reemplazar el modelo de usuario estándar después de las migraciones iniciales.
El estilo adapta la paleta azul/dorado y las tarjetas del prototipo suministrado;
los datos estáticos y la simulación de registro/voto se sustituyen por Django real.

## Pendientes de la entrega

Verificar la instalación en los demás equipos y la visualización móvil, tomar capturas comentadas,
actualizar el informe con fragmentos de código y resultados, y grabar un video de
al menos cinco minutos con participación de los cuatro. La entrega oficial es un
PDF por equipo con enlaces accesibles al repositorio y video.

Las reglas de voto, identidad definitiva, publicación de resultados y despliegue
productivo siguen fuera de esta fase. Una edición por año y nombres de categoría
únicos por edición son propuestas de modelado del equipo, no reglas oficiales.

## Credenciales

No subir .env, claves privadas, contraseñas, datos personales, venv o bases locales.
Usar datos de prueba. Cambiar credenciales que hayan quedado expuestas o sean débiles.


## Inicio y reinicio en Windows (CMD)

Requisitos: Python, Git y MySQL instalados; servicio MySQL iniciado; base
`votaciones` y usuario `votaciones_app` preparados como se indica arriba.
Cada integrante utiliza su propia contraseña local de MySQL.
Los comandos siguientes son para CMD, no para PowerShell ni para la consola mysql>.

### Primera instalación

Clonar el repositorio si todavía no se tiene:

```bat
git clone https://github.com/aloaiza35-eng/desarrollo-web-votaciones.git
cd desarrollo-web-votaciones
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

Si ya está clonado, entrar a su carpeta, guardar los cambios propios y actualizar
con `git pull --ff-only origin main`. No volver a clonar ni crear el entorno en
cada inicio. La ubicación de la carpeta puede ser diferente en cada computador.

### Variables: configurar en cada terminal nueva

Desde la raíz del proyecto y con el entorno virtual activo:

```bat
set "DJANGO_DEBUG=True"
set "DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1"
set "MYSQL_DATABASE=votaciones"
set "MYSQL_USER=votaciones_app"
set "MYSQL_HOST=127.0.0.1"
set "MYSQL_PORT=3306"
python -c "import os,secrets,getpass,subprocess; os.environ['DJANGO_SECRET_KEY']=secrets.token_urlsafe(50); os.environ['MYSQL_PASSWORD']=getpass.getpass('Password de votaciones_app: '); subprocess.call(['cmd.exe','/D'])"
```

El último comando solicita la contraseña del usuario MySQL `votaciones_app`,
no la del administrador de Django ni la de root. Al escribirla no se muestra.
Se abre una consola CMD hija con las variables; continuar dentro de ella.
Este método no escribe las credenciales en el repositorio.

La clave Django generada es temporal para desarrollo: al repetir este comando
cambia y las sesiones anteriores pueden dejar de ser válidas; los datos de MySQL
se conservan. Para mantener sesiones entre reinicios, configurar una clave estable
privada mediante el entorno local. `.env.example` es solo una referencia: copiarlo
a `.env` no carga variables automáticamente.

### Preparar la base y ejecutar

En la consola que tiene las variables:

```bat
python manage.py check
python manage.py migrate
```

Solo en una base de demostración nueva, cargar los cinco registros compartidos:

```bat
python manage.py loaddata datos_prueba
```

El fixture usa identificadores fijos y puede sobrescribir registros con esos
identificadores; no cargarlo en cada inicio ni sobre datos propios sin revisar.
Crear un administrador propio una sola vez:

```bat
python manage.py createsuperuser
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ y mantener la terminal abierta. Admin está en
http://127.0.0.1:8000/admin/. Cada integrante crea su administrador; Git no incluye
usuarios ni la base local. Para los siguientes inicios basta activar el entorno,
configurar las variables y ejecutar `python manage.py runserver`.
Después de actualizar el código compartido, ejecutar `python manage.py migrate`.

### Errores frecuentes

- `KeyError: DJANGO_SECRET_KEY` o `MYSQL_PASSWORD`: faltan variables en esa terminal;
  repetir el bloque de configuración y continuar en la consola hija.
- `Access denied`: verificar usuario y contraseña de MySQL.
- Error de conexión/puerto 3306: comprobar que el servicio MySQL esté iniciado.
- `No migrations to apply`: es normal; la base ya está al día.
- Las pruebas con `config.test_settings` usan SQLite temporal y no configuran las
  variables de la terminal ni sustituyen la ejecución de la aplicación con MySQL.
