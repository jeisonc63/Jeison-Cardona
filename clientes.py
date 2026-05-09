"""
clientes.py – Clase Cliente con encapsulación y validaciones robustas (Software FJ)

Implementa la entidad Cliente con propiedades privadas, validación
de datos en los setters y uso de excepciones personalizadas.
"""

import re
from abc import ABC, abstractmethod
from exceptions import ClienteInvalidoError, ParametroFaltanteError


# ─────────────────────────────────────────────────────────────────────────────
# Clase abstracta base (requerida por el enunciado)
# ─────────────────────────────────────────────────────────────────────────────
class EntidadBase(ABC):
    """
    Clase abstracta que representa cualquier entidad del sistema Software FJ.
    Define la interfaz mínima que toda entidad debe implementar.
    """

    @abstractmethod
    def validar(self) -> bool:
        """Valida que la entidad sea coherente y esté lista para operar."""
        ...

    @abstractmethod
    def __str__(self) -> str:
        """Representación legible de la entidad."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# Clase Cliente
# ─────────────────────────────────────────────────────────────────────────────
class Cliente(EntidadBase):
    """
    Representa un cliente de Software FJ.

    Aplica encapsulación estricta: todos los atributos son privados y
    se acceden/modifican mediante propiedades con validación integrada.

    Atributos privados:
        __nombre   (str): Nombre completo (≥ 3 caracteres, solo letras/espacios)
        __email    (str): Correo electrónico con formato válido
        __telefono (str): Teléfono de 10 dígitos

    Excepciones:
        ClienteInvalidoError – si algún dato falla la validación
        ParametroFaltanteError – si algún parámetro es None
    """

    # Patrón para validar emails
    _PATRON_EMAIL = re.compile(r"^[\w.\-+]+@[\w\-]+\.[a-zA-Z]{2,}$")
    # Patrón para teléfonos: exactamente 10 dígitos (Colombia)
    _PATRON_TELEFONO = re.compile(r"^\d{10}$")

    def __init__(self, nombre: str, email: str, telefono: str, logger=None):
        self._logger = logger
        # Validar que ningún parámetro sea None antes de asignar
        for campo, valor in [("nombre", nombre), ("email", email), ("telefono", telefono)]:
            if valor is None:
                raise ParametroFaltanteError(campo, "Cliente.__init__")

        # Los setters realizan la validación
        self.nombre = nombre
        self.email = email
        self.telefono = telefono

    # ── Propiedad: nombre ────────────────────────────────────────
    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str):
        valor = valor.strip()
        if not valor:
            raise ClienteInvalidoError("nombre", valor, "no puede estar vacío")
        if len(valor) < 3:
            raise ClienteInvalidoError("nombre", valor, "debe tener al menos 3 caracteres")
        if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚüÜñÑ\s]+$", valor):
            raise ClienteInvalidoError("nombre", valor, "solo se permiten letras y espacios")
        self.__nombre = valor

    # ── Propiedad: email ─────────────────────────────────────────
    @property
    def email(self) -> str:
        return self.__email

    @email.setter
    def email(self, valor: str):
        valor = valor.strip().lower()
        if not valor:
            raise ClienteInvalidoError("email", valor, "no puede estar vacío")
        if not self._PATRON_EMAIL.match(valor):
            raise ClienteInvalidoError("email", valor, "formato de correo inválido (ej: usuario@dominio.com)")
        self.__email = valor

    # ── Propiedad: telefono ──────────────────────────────────────
    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str):
        valor = valor.strip().replace(" ", "").replace("-", "")
        if not valor:
            raise ClienteInvalidoError("telefono", valor, "no puede estar vacío")
        if not self._PATRON_TELEFONO.match(valor):
            raise ClienteInvalidoError("telefono", valor, "debe contener exactamente 10 dígitos")
        self.__telefono = valor

    # ── Métodos de la clase abstracta ───────────────────────────
    def validar(self) -> bool:
        """Verifica que el cliente tenga todos sus datos correctos."""
        try:
            assert len(self.__nombre) >= 3
            assert self._PATRON_EMAIL.match(self.__email)
            assert self._PATRON_TELEFONO.match(self.__telefono)
            return True
        except AssertionError:
            return False

    def __str__(self) -> str:
        return (
            f"Cliente(nombre='{self.__nombre}', "
            f"email='{self.__email}', "
            f"tel='{self.__telefono}')"
        )

    def __repr__(self) -> str:
        return self.__str__()
