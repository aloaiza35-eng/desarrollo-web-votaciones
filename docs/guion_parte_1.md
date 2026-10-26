# Guion de la parte 1

Intervencion orientativa de 80 a 100 segundos. El video completo debe durar al menos cinco minutos y mostrar la participacion de los cuatro integrantes. Falta grabarlo.

## Explicacion sugerida

Mi responsabilidad fue preparar el proyecto Django, conectar MySQL y configurar los modelos y su administracion. La estructura relaciona ediciones, categorias, votaciones y opciones mediante claves foraneas.

Genere la migracion inicial y la aplique en MySQL. La migracion y los cinco registros ficticios iniciales estan compartidos en GitHub para que el equipo pueda reproducir la base en sus computadores.

Desde Django Admin puedo consultar los registros. Tambien cree el participante C y modifique su descripcion. Despues de guardar y reabrir, se debe comprobar que el cambio permanece.

Las credenciales se reciben por variables de entorno y no se comparten en Git. El acceso del administrador es diferente de la autenticacion publica que desarrolla otro integrante. Esta etapa administra el catalogo y todavia no registra votos.

## Secuencia de demostracion

1. Mostrar models.py y explicar las relaciones.
2. Mostrar python manage.py showmigrations votaciones con la migracion marcada [X].
3. Recorrer ediciones, categorias y votaciones desde Admin.
4. Mostrar opciones A, B y C.
5. Abrir C y demostrar una edicion guardada.
6. Mostrar los nombres de variables en .env.example, sin credenciales reales.

No mostrar el historial de comandos con contrasenas. Confirmar el guardado antes de afirmar persistencia. No presentar como implementado el frontend publico.
