> Nota de actualización: los puntos 2 y 3 ya tienen implementación; su estado actual y la validación pendiente con MySQL se describen en README.md y docs/validacion_eje2.md. Los resultados de la parte 1 que siguen son históricos.

# Integracion del equipo

## Preparar cada computador

1. Guardar los cambios locales antes de actualizar el repositorio.
2. Actualizar la rama acordada; si es main: git pull origin main.
3. Crear el entorno virtual e instalar requirements.txt.
4. Preparar MySQL y las variables de entorno con credenciales propias.
5. Ejecutar python manage.py migrate.
6. En una base de prueba nueva, ejecutar python manage.py loaddata datos_prueba.
7. Crear su propio administrador con python manage.py createsuperuser.
8. Ejecutar python manage.py runserver.

No volver a generar la migracion inicial: ya esta compartida. La base local, el entorno virtual y los usuarios administradores no viajan con Git. El fixture tiene identificadores; revisar conflictos antes de cargarlo sobre datos existentes.

## Modelos compartidos

Importar Edicion, Categoria, Votacion y Opcion desde votaciones.models.

Relaciones:
- edicion.categorias.all()
- categoria.votaciones.all()
- votacion.opciones.all()

Se utiliza el usuario estandar de Django y sus tablas ya se migraron. Coordinar cualquier propuesta de cambio antes de implementarla.

## Coordinacion

Avisar antes de modificar settings.py, urls.py, requirements.txt o los modelos. Cada persona debe trabajar con su propia cuenta y aportar evidencias de su parte. No compartir contrasenas ni tokens.

## Pendientes del equipo

- Registro, inicio y cierre de sesion publicos.
- Rutas, vistas y plantillas con datos reales de MySQL.
- Pruebas de integracion y correccion de errores.
- Capturas comentadas, informe PDF y enlaces accesibles.
- Video con participacion de los cuatro integrantes.

## Base de datos y Docker

La configuracion comprobada utiliza MySQL como servicio local de Windows. Docker no es obligatorio segun la consigna y la transcripcion aportadas. No hace falta instalarlo para trabajar con esta base.
