"""Solo pruebas aisladas: no sustituye MySQL en la aplicación ni en la entrega."""
import os
os.environ.setdefault("DJANGO_SECRET_KEY", "clave-exclusiva-pruebas-no-produccion")
os.environ.setdefault("MYSQL_PASSWORD", "no-se-usa-en-pruebas-sqlite")
from .settings import *  # noqa: F403
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
