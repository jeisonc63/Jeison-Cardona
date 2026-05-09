"""
reservas.py – Clase Reserva y GestorReservas (Software FJ)

Implementa la gestión de reservas con:
  - Estados: pendiente → confirmada → cancelada / procesada
  - Manejo de excepciones: try/except, try/except/else, try/except/finally
  - Encadenamiento de excepciones (raise ... from ...)
  - Integración con el logger para registro de eventos
"""

import uuid
from datetime import datetime
from exceptions import (
    ReservaInvalidaError, ParametroFaltanteError,
    ServicioNoDisponibleError, CostoInconsistenteError
)


# ─────────────────────────────────────────────────────────────────────────────
# Clase Reserva
# ─────────────────────────────────────────────────────────────────────────────
class Reserva:
    """
    Representa una reserva de un servicio por parte de un cliente.

    Estados posibles:
      'pendiente'   → recién creada, sin confirmar
      'confirmada'  → procesada y activa
      'cancelada'   → anulada antes de su procesamiento
      'procesada'   → servicio ya ejecutado (histórico)

    Atributos:
      id_reserva (str):  Identificador único (UUID corto)
      cliente    (Cliente): Titular de la reserva
      servicio   (Servicio): Servicio reservado
      horas      (float): Duración solicitada
      estado     (str):  Estado actual
      fecha      (datetime): Fecha/hora de creación

    Excepciones:
      ParametroFaltanteError  – cliente o servicio None
      ReservaInvalidaError    – horas <= 0, servicio no disponible, estado inválido
    """

    ESTADOS_VALIDOS = {"pendiente", "confirmada", "cancelada", "procesada"}

    def __init__(self, cliente, servicio, horas: float, logger=None):
        self._logger = logger
        self._fecha = datetime.now()
        self._id = str(uuid.uuid4())[:8].upper()

        # ── Bloque try/except/finally ──────────────────────────
        try:
            # Validar cliente
            if cliente is None:
                raise ParametroFaltanteError("cliente", "Reserva.__init__")

            # Validar servicio
            if servicio is None:
                raise ParametroFaltanteError("servicio", "Reserva.__init__")

            # Validar disponibilidad del servicio
            if not servicio.disponible:
                raise ReservaInvalidaError(
                    f"el servicio '{servicio.nombre}' no está disponible",
                    self._id
                )

            # Validar horas
            if not isinstance(horas, (int, float)):
                raise ReservaInvalidaError(
                    f"horas debe ser numérico, se recibió: {type(horas).__name__}",
                    self._id
                )
            if horas <= 0:
                raise ReservaInvalidaError(
                    f"la duración debe ser positiva, se recibió: {horas}",
                    self._id
                )

            self._cliente = cliente
            self._servicio = servicio
            self._horas = float(horas)
            self._estado = "pendiente"

        except (ParametroFaltanteError, ReservaInvalidaError):
            if self._logger:
                self._logger.error(f"Error creando reserva {self._id}")
            raise  # Re-lanzar para que el llamador lo maneje

        finally:
            # Este bloque siempre se ejecuta (éxito o fallo)
            if self._logger:
                self._logger.info(f"Intento de creación de reserva {self._id}")

    # ── Propiedades (solo lectura) ────────────────────────────
    @property
    def id_reserva(self) -> str:
        return self._id

    @property
    def cliente(self):
        return self._cliente

    @property
    def servicio(self):
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def fecha(self) -> datetime:
        return self._fecha

    # ── Métodos de ciclo de vida ──────────────────────────────
    def confirmar(self):
        """
        Confirma la reserva si está en estado 'pendiente'.

        try/except/else:
          - try: intenta confirmar
          - except: captura errores de estado o servicio
          - else: registra éxito solo si no hubo excepciones
        """
        try:
            if self._estado != "pendiente":
                raise ReservaInvalidaError(
                    f"solo reservas 'pendiente' pueden confirmarse "
                    f"(estado actual: '{self._estado}')",
                    self._id
                )
            if not self._servicio.disponible:
                raise ServicioNoDisponibleError(
                    self._servicio.nombre,
                    "fue desactivado antes de confirmar la reserva"
                )
            self._estado = "confirmada"

        except (ReservaInvalidaError, ServicioNoDisponibleError) as e:
            if self._logger:
                self._logger.error(f"Fallo al confirmar reserva {self._id}: {e}")
            raise ReservaInvalidaError(str(e), self._id) from e

        else:
            # Solo se ejecuta si NO hubo excepción
            if self._logger:
                self._logger.info(f"Reserva {self._id} confirmada exitosamente")

    def cancelar(self):
        """
        Cancela la reserva si su estado lo permite.

        try/except/finally:
          - try: intenta cancelar
          - except: captura estado inválido
          - finally: siempre registra el intento
        """
        try:
            if self._estado in {"cancelada", "procesada"}:
                raise ReservaInvalidaError(
                    f"no se puede cancelar una reserva '{self._estado}'",
                    self._id
                )
            self._estado = "cancelada"

        except ReservaInvalidaError:
            if self._logger:
                self._logger.warning(f"Intento de cancelación inválida: {self._id}")
            raise

        finally:
            # Siempre se registra el intento, haya funcionado o no
            if self._logger:
                self._logger.info(f"Intento de cancelación procesado para reserva {self._id}")

    def procesar(self):
        """Marca la reserva como ejecutada (servicio prestado)."""
        if self._estado != "confirmada":
            raise ReservaInvalidaError(
                f"solo reservas 'confirmada' pueden procesarse "
                f"(estado actual: '{self._estado}')",
                self._id
            )
        self._estado = "procesada"
        if self._logger:
            self._logger.info(f"Reserva {self._id} procesada (servicio prestado)")

    # ── Cálculo de costos (método sobrecargado) ───────────────
    def calcular_total(self, descuento: float = 0.0, impuesto: float = 0.0) -> float:
        """
        Calcula el total de la reserva delegando al servicio.

        Variantes (sobrecarga por parámetros opcionales):
          calcular_total()                       → precio puro
          calcular_total(descuento=0.10)         → con descuento del 10%
          calcular_total(impuesto=0.19)          → con IVA del 19%
          calcular_total(descuento=0.10, impuesto=0.19) → ambos

        Raises:
          CostoInconsistenteError: si el cálculo produce un valor inválido
        """
        try:
            total = self._servicio.calcular_costo(self._horas, descuento, impuesto)
        except CostoInconsistenteError as e:
            if self._logger:
                self._logger.error(f"Costo inconsistente en reserva {self._id}: {e}")
            raise
        except Exception as e:
            msg = f"Error inesperado calculando total de reserva {self._id}"
            if self._logger:
                self._logger.error(f"{msg}: {e}")
            raise ReservaInvalidaError(msg, self._id) from e

        return total

    def __str__(self) -> str:
        return (
            f"Reserva[{self._id}] "
            f"│ Cliente: {self._cliente.nombre} "
            f"│ Servicio: {self._servicio.nombre} "
            f"│ {self._horas}h "
            f"│ Estado: {self._estado.upper()} "
            f"│ Fecha: {self._fecha.strftime('%Y-%m-%d %H:%M')}"
        )

    def __repr__(self) -> str:
        return self.__str__()


# ─────────────────────────────────────────────────────────────────────────────
# Clase GestorReservas
# ─────────────────────────────────────────────────────────────────────────────
class GestorReservas:
    """
    Administra el conjunto de reservas del sistema.

    Funciones:
      - Almacena reservas en una lista interna (sin base de datos)
      - Permite filtrar por estado o cliente
      - Calcula el total facturado de reservas activas
    """

    def __init__(self, logger=None):
        self._reservas: list[Reserva] = []
        self._logger = logger

    def agregar_reserva(self, reserva: Reserva):
        """Agrega una reserva validada al gestor."""
        if not isinstance(reserva, Reserva):
            raise ParametroFaltanteError("reserva", "GestorReservas.agregar_reserva")
        self._reservas.append(reserva)
        if self._logger:
            self._logger.info(f"Reserva {reserva.id_reserva} añadida al gestor")

    def buscar_por_id(self, id_reserva: str) -> Reserva:
        """Busca y retorna una reserva por su ID."""
        for r in self._reservas:
            if r.id_reserva == id_reserva:
                return r
        raise ReservaInvalidaError(f"reserva con ID '{id_reserva}' no encontrada", id_reserva)

    def listar_reservas(self, estado: str = None):
        """Lista todas las reservas, opcionalmente filtradas por estado."""
        filtradas = self._reservas
        if estado:
            estado = estado.lower()
            filtradas = [r for r in self._reservas if r.estado == estado]

        if not filtradas:
            print("  (Sin reservas registradas)")
            return

        for r in filtradas:
            print(f"  → {r}")
            try:
                print(f"     Total: ${r.calcular_total():,.0f} COP")
            except Exception as e:
                print(f"     [Sin total disponible: {e}]")

    def total_facturado(self) -> float:
        """Suma el costo de todas las reservas confirmadas o procesadas."""
        total = 0.0
        for r in self._reservas:
            if r.estado in {"confirmada", "procesada"}:
                try:
                    total += r.calcular_total()
                except Exception as e:
                    if self._logger:
                        self._logger.warning(f"Omitiendo reserva {r.id_reserva} en total: {e}")
        return total

    def contar_por_estado(self) -> dict:
        """Retorna un conteo de reservas agrupadas por estado."""
        conteo = {e: 0 for e in Reserva.ESTADOS_VALIDOS}
        for r in self._reservas:
            conteo[r.estado] = conteo.get(r.estado, 0) + 1
        return conteo

    def __len__(self) -> int:
        return len(self._reservas)
