"""Pruebas con MySQL real y base separada; no usar para runserver."""
from .settings import *  # noqa: F403

DATABASES["default"]["TEST"] = {"NAME": "test_votaciones"}  # noqa: F405
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
