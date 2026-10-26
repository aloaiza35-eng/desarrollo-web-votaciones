# Validación de autenticación y catálogo público

## Pruebas automatizadas ejecutadas

24 pruebas con Django 5.2.18 y SQLite temporal en memoria: 15 de autenticación y
9 de catálogo. Resultado: OK. No se ejecutaron contra MySQL en el entorno del
implementador. La configuración normal sigue usando MySQL, sin cambios de modelos.

Cobertura: registro válido, hash de contraseña, usuario duplicado, contraseñas
incompatibles/débiles y campos vacíos; login válido/inválido e inactivo; cuenta
privada; next externo rechazado; logout POST y GET rechazado; CSRF y permisos de
Admin; jerarquía de categorías/votaciones/opciones; ediciones múltiples; datos
nuevos o editados; catálogo vacío; 404; escape HTML y consultas sin N+1 en detalle.

## Verificación manual pendiente en el computador con MySQL

1. Guardar trabajo local y actualizar código sin reemplazar aportes ajenos.
2. Activar .venv y configurar las variables privadas habituales.
3. Ejecutar python manage.py check y python manage.py migrate.
4. Iniciar python manage.py runserver y abrir la raíz del sitio.
5. Recorrer edición 2027, categoría, votación y sus opciones A/B y C si existe localmente.
6. En Admin editar el nombre de una opción o crear una nueva; volver al detalle y
   recargar para comprobar que se refleja. Restaurar el nombre si el equipo lo necesita.
7. Crear una segunda edición/categoría/votación de prueba. Comprobar que no mezcla opciones.
8. Crear cuenta pública con un nombre nuevo y contraseña que cumpla las validaciones.
9. Repetir usuario, probar contraseñas distintas y una débil: deben mostrar errores.
10. Iniciar sesión con credenciales válidas e inválidas; revisar Mi cuenta.
11. Cerrar sesión con el botón y volver a /cuentas/mi-cuenta/: debe pedir acceso.
12. Comprobar que un usuario normal no puede entrar a Django Admin.
13. Probar a 360, 768 y 1280 px, navegación por teclado y mensajes de catálogo vacío.

No presentar esta lista como realizada hasta verificarla y registrar resultados.

## Capturas para el PDF

- Migraciones aplicadas en MySQL y check sin errores.
- Inicio público y recorrido del catálogo con datos reales del proyecto.
- Antes/después de un cambio desde Admin reflejado públicamente.
- Registro con validación y registro completado.
- Login inválido y Mi cuenta con sesión activa; no capturar contraseñas visibles.
- Cierre de sesión y solicitud de acceso posterior.
- Vistas de móvil y computador.

En el informe explicar que el Model es el modelo ORM, la View consulta/procesa,
y el Template genera el HTML. Señalar funciones de votaciones/views.py y
cuentas/views.py, rutas y formularios estándar usados. No copiar todo el proyecto.

## Fuentes técnicas

Django 5.2, documentación oficial: https://docs.djangoproject.com/en/5.2/topics/auth/default/
Se usan UserCreationForm, AuthenticationForm, LoginView y LogoutView; cierre de
sesión mediante POST y formularios con token CSRF. No se implementó un sistema
propio de contraseñas ni se hicieron cambios a las migraciones de usuarios.
