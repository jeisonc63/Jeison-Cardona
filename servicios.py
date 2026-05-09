"""
servicios.py – Clases de servicios con herencia, polimorfismo y métodos sobrecargados
Software FJ

Jerarquía:
  EntidadBase (ABC)
      └── Servicio (ABC)
              ├── SalaReunion
              ├── AlquilerEquipo
              └── AsesoriaTecnica
"""

from abc import abstractmethod
from clientes import EntidadBase
from exceptions import (
    ServicioNoDisponibleError, CapacidadExcedidaError,
    CostoInconsistenteError, ParametroFaltanteError
)
import math


# ─────────────────────────────────────────────────────────────────────────────
# Clase abstracta Servicio
# ─────────────────────────────────────────────────────────────────────────────
class Servicio(EntidadBase):
    """
    Clase abstracta que representa cualquier servicio ofrecido por Software FJ.

    Obliga a los subtipos a implementar:
      - calcular_costo(horas, descuento, impuesto): polimorfismo en precio
      - describir(): descripción detallada del servicio
      - validar(): coherencia interna del servicio

    Atributos comunes:
      nombre     (str): Nombre del servicio
      disponible (bool): Si puede recibir nuevas reservas
    """

    def __init__(self, nombre: str, disponible: bool = True, logger=None):
        if not nombre or not nombre.strip():
            raise ParametroFaltanteError("nombre", "Servicio.__init__")
        self._nombre = nombre.strip()
        self._disponible = disponible
        self._logger = logger

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def disponible(self) -> bool:
        return self._disponible

    def desactivar(self):
        self._disponible = False
        if self._logger:
            self._logger.warning(f"Servicio desactivado: {self._nombre}")

    def activar(self):
        self._disponible = True

    @abstractmethod
    def calcular_costo(self, horas: float, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """
        Calcula el costo del servicio con parámetros opcionales.
        Método sobrecargado (a través de parámetros con valores por defecto).

        Args:
            horas     (float): Duración en horas
            descuento (float): Porcentaje de descuento, ej: 0.10 = 10%
            impuesto  (float): Porcentaje de impuesto, ej: 0.19 = 19% (IVA)

        Returns:
            float: Costo final calculado

        Raises:
            CostoInconsistenteError: si el resultado es negativo o infinito
        """
        ...

    @abstractmethod
    def describir(self) -> str:
        """Retorna una descripción completa del servicio."""
        ...

    def _validar_horas(self, horas: float):
        """Validación común de duración para todos los servicios."""
        if horas is None:
            raise ParametroFaltanteError("horas", self._nombre)
        if not isinstance(horas, (int, float)):
            raise ServicioNoDisponibleError(self._nombre, f"horas debe ser numérico, se recibió: {type(horas)}")
        if horas <= 0:
            raise ServicioNoDisponibleError(self._nombre, f"horas debe ser positivo, se recibió: {horas}")

    def _aplicar_modificadores(self, costo_base: float, descuento: float, impuesto: float) -> float:
        """Aplica descuento e impuesto al costo base."""
        if not (0.0 <= descuento < 1.0):
            raise ServicioNoDisponibleError(self._nombre, f"descuento inválido: {descuento} (debe estar entre 0 y 1)")
        if impuesto < 0.0:
            raise ServicioNoDisponibleError(self._nombre, f"impuesto inválido: {impuesto}")
        costo = costo_base * (1 - descuento) * (1 + impuesto)
        if not math.isfinite(costo) or costo < 0:
            raise CostoInconsistenteError(self._nombre, costo)
        return round(costo, 2)

    def __str__(self) -> str:
        estado = "Disponible" if self._disponible else "No disponible"
        return f"{self.__class__.__name__}('{self._nombre}', {estado})"

    def __repr__(self) -> str:
        return self.__str__()


# ─────────────────────────────────────────────────────────────────────────────
# Servicio 1: Sala de Reuniones
# ─────────────────────────────────────────────────────────────────────────────
class SalaReunion(Servicio):
    """
    Reserva de salas de reuniones por horas.

    Precio base: $50.000 COP/hora
    Suplemento por capacidad > 5 personas: +$10.000 COP/hora
    """

    PRECIO_BASE_HORA = 50_000       # COP/hora
    SUPLEMENTO_GRANDE = 10_000      # COP/hora adicional para capacidad > 5

    def __init__(self, nombre: str, capacidad: int, logger=None):
        try:
            super().__init__(nombre, disponible=True, logger=logger)
            if not isinstance(capacidad, int) or capacidad <= 0:
                raise CapacidadExcedidaError(capacidad_max=1, solicitada=capacidad)
            self._capacidad = capacidad
        except CapacidadExcedidaError as e:
            raise ServicioNoDisponibleError(nombre, f"capacidad inválida: {capacidad}") from e

    @property
    def capacidad(self) -> int:
        return self._capacidad

    def validar_asistentes(self, asistentes: int):
        """Valida que los asistentes no excedan la capacidad."""
        if asistentes > self._capacidad:
            raise CapacidadExcedidaError(self._capacidad, asistentes)

    def calcular_costo(self, horas: float, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """
        Calcula el costo de reservar la sala.

        Variantes del método (sobrecarga):
          calcular_costo(horas)                          → precio puro
          calcular_costo(horas, descuento=0.10)          → con descuento
          calcular_costo(horas, impuesto=0.19)           → con IVA
          calcular_costo(horas, descuento=0.10, impuesto=0.19) → descuento + IVA
        """
        self._validar_horas(horas)
        precio_hora = self.PRECIO_BASE_HORA
        if self._capacidad > 5:
            precio_hora += self.SUPLEMENTO_GRANDE
        costo_base = precio_hora * horas
        return self._aplicar_modificadores(costo_base, descuento, impuesto)

    def describir(self) -> str:
        return (
            f"[Sala de Reunión] {self._nombre} "
            f"│ Capacidad: {self._capacidad} personas "
            f"│ Precio: ${self.PRECIO_BASE_HORA:,.0f} COP/h"
        )

    def validar(self) -> bool:
        return bool(self._nombre) and self._capacidad > 0


# ─────────────────────────────────────────────────────────────────────────────
# Servicio 2: Alquiler de Equipos
# ─────────────────────────────────────────────────────────────────────────────
class AlquilerEquipo(Servicio):
    """
    Alquiler de equipos tecnológicos por horas.

    Precios según tipo (COP/hora):
        laptop: $25.000 | proyector: $15.000 | servidor: $80.000
    """

    PRECIOS = {
        "laptop":    25_000,
        "proyector": 15_000,
        "servidor":  80_000,
    }

    def __init__(self, nombre: str, tipo_equipo: str, cantidad: int, logger=None):
        super().__init__(nombre, disponible=True, logger=logger)
        tipo_equipo = tipo_equipo.lower().strip()
        if tipo_equipo not in self.PRECIOS:
            raise ServicioNoDisponibleError(
                nombre,
                f"tipo de equipo '{tipo_equipo}' no reconocido. "
                f"Opciones: {list(self.PRECIOS.keys())}"
            )
        if not isinstance(cantidad, int) or cantidad <= 0:
            raise ServicioNoDisponibleError(nombre, f"cantidad debe ser entero positivo, se recibió: {cantidad}")
        self._tipo_equipo = tipo_equipo
        self._cantidad = cantidad

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def cantidad(self) -> int:
        return self._cantidad

    def calcular_costo(self, horas: float, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """
        Calcula el costo del alquiler.

        El costo base es: precio_por_hora × cantidad × horas

        Variantes:
          calcular_costo(horas)                     → sin modificadores
          calcular_costo(horas, descuento=0.10)     → con descuento
          calcular_costo(horas, impuesto=0.19)      → con IVA
        """
        self._validar_horas(horas)
        precio_hora = self.PRECIOS[self._tipo_equipo]
        costo_base = precio_hora * self._cantidad * horas
        return self._aplicar_modificadores(costo_base, descuento, impuesto)

    def describir(self) -> str:
        precio = self.PRECIOS[self._tipo_equipo]
        return (
            f"[Alquiler Equipo] {self._nombre} "
            f"│ Tipo: {self._tipo_equipo} × {self._cantidad} unidades "
            f"│ Precio: ${precio:,.0f} COP/h por unidad"
        )

    def validar(self) -> bool:
        return (
            bool(self._nombre)
            and self._tipo_equipo in self.PRECIOS
            and self._cantidad > 0
        )


# ─────────────────────────────────────────────────────────────────────────────
# Servicio 3: Asesoría Especializada
# ─────────────────────────────────────────────────────────────────────────────
class AsesoriaTecnica(Servicio):
    """
    Asesoría técnica especializada facturada por hora.

    Tarifas según nivel del asesor (COP/hora):
        Junior:  $80.000 | Senior: $150.000 | Expert: $250.000
    """

    TARIFAS = {
        "junior": 80_000,
        "senior": 150_000,
        "expert": 250_000,
    }

    def __init__(self, nombre: str, area: str, nivel_asesor: str, logger=None):
        super().__init__(nombre, disponible=True, logger=logger)
        nivel = nivel_asesor.lower().strip()
        if nivel not in self.TARIFAS:
            raise ServicioNoDisponibleError(
                nombre,
                f"nivel '{nivel_asesor}' no reconocido. "
                f"Opciones: {list(self.TARIFAS.keys())}"
            )
        if not area or not area.strip():
            raise ParametroFaltanteError("area", "AsesoriaTecnica.__init__")
        self._area = area.strip()
        self._nivel = nivel

    @property
    def area(self) -> str:
        return self._area

    @property
    def nivel(self) -> str:
        return self._nivel

    def calcular_costo(self, horas: float, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """
        Calcula el costo de la asesoría.

        Tarifa varía según el nivel del asesor.

        Variantes:
          calcular_costo(horas)                          → tarifa base
          calcular_costo(horas, descuento=0.15)          → tarifa con descuento
          calcular_costo(horas, descuento=0.10, impuesto=0.19) → descuento + IVA
        """
        self._validar_horas(horas)
        tarifa = self.TARIFAS[self._nivel]
        costo_base = tarifa * horas
        return self._aplicar_modificadores(costo_base, descuento, impuesto)

    def describir(self) -> str:
        tarifa = self.TARIFAS[self._nivel]
        return (
            f"[Asesoría Técnica] {self._nombre} "
            f"│ Área: {self._area} "
            f"│ Nivel: {self._nivel.capitalize()} "
            f"│ Tarifa: ${tarifa:,.0f} COP/h"
        )

    def validar(self) -> bool:
        return (
            bool(self._nombre)
            and bool(self._area)
            and self._nivel in self.TARIFAS
        )
