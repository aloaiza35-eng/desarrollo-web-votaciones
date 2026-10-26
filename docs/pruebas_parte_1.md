> Nota de actualización: los puntos 2 y 3 ya tienen implementación; su estado actual y la validación pendiente con MySQL se describen en README.md y docs/validacion_eje2.md. Los resultados de la parte 1 que siguen son históricos.

# Pruebas y evidencias de la parte 1

Resultados basados en las salidas de terminal y capturas compartidas por Andres. No representan pruebas en todos los computadores.

## Comprobaciones realizadas

- Instalacion de dependencias e importacion de MySQLdb: correctas.
- Acceso a MySQL con votaciones_app: correcto.
- python manage.py check: sin incidencias.
- Migracion inicial: cuatro modelos y restriccion de categoria generados.
- python manage.py migrate: todas las migraciones aplicadas con OK.
- Creacion de superusuario y acceso/cierre de sesion de Admin: correctos.
- Insercion ORM: una edicion, una categoria, una votacion y dos opciones.
- Fixture UTF-8: cinco registros comprobados.
- python manage.py loaddata datos_prueba: cinco objetos instalados.
- Creacion del participante C desde Admin: listado con tres opciones.
- Edicion de C: captura con descripcion modificada; confirmar que se conserva despues de guardar y reabrir.

## Capturas para entregar al responsable del PDF

1. Migraciones aplicadas. Para mostrar el estado actual: python manage.py showmigrations.
2. Listado de ediciones con 2027.
3. Categorias y su edicion.
4. Votaciones y su categoria.
5. Listado de opciones A, B y C con su votacion.
6. Formulario de C reabierto con la descripcion guardada.

Las capturas deben reunirse e incorporarse al informe. Este archivo no sustituye las imagenes ni afirma que ya esten adjuntas.

## Texto para explicar las evidencias

El listado muestra tres opciones asociadas a la votacion de demostracion. Las opciones A y B proceden de los datos iniciales y C se creo desde Django Admin.

Una vez confirmado el guardado y reapertura: la descripcion conservada del participante C demuestra la persistencia de la edicion en MySQL.

## Limites

El fixture compartido tiene cinco registros y no incluye al participante C, usuarios ni contrasenas. No se han probado autenticacion publica, interfaces publicas, votos ni resultados. Cambiar las contrasenas expuestas o debiles antes de cerrar la configuracion local; no documentar sus valores.
