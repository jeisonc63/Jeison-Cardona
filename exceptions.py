"""
exceptions.py – Excepciones personalizadas del sistema Software FJ

Implementa una jerarquía de excepciones propias que permiten identificar
con precisión el tipo de error ocurrido en cada capa del sistema.
"""


class SoftwareFJError(Exception):
    """
    Excepción base del sistema Software FJ.
    Todas las excepciones personalizadas heredan de esta clase.
    """
    def __init__(self, mensaje: str, codigo: int = 0):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo

    def __str__(self):
        return f"[Código {self.codigo}] {self.mensaje}"


class ClienteInvalidoError(SoftwareFJError):
    """
    Se lanza cuando los datos de un cliente no cumplen las validaciones.
    Ejemplos: email malformado, nombre vacío, teléfono incorrecto.
    """
    def __init__(self, campo: str, valor: str, razon: str):
        mensaje = f"Cliente inválido – Campo '{campo}': '{valor}' → {razon}"
        super().__init__(mensaje, codigo=1001)
        self.campo = campo
        self.valor = valor
        self.razon = razon


class ServicioNoDisponibleError(SoftwareFJError):
    """
    Se lanza cuando un servicio no puede ser creado o está fuera de servicio.
    Ejemplos: parámetros negativos, tipo de equipo no reconocido.
    """
    def __init__(self, servicio: str, motivo: str):
        mensaje = f"Servicio no disponible – '{servicio}': {motivo}"
        super().__init__(mensaje, codigo=2001)
        self.servicio = servicio
        self.motivo = motivo


class ReservaInvalidaError(SoftwareFJError):
    """
    Se lanza cuando una reserva no puede procesarse correctamente.
    Ejemplos: duración negativa, reserva ya cancelada, cliente ausente.
    """
    def __init__(self, motivo: str, id_reserva: str = "N/A"):
        mensaje = f"Reserva inválida [{id_reserva}]: {motivo}"
        super().__init__(mensaje, codigo=3001)
        self.motivo = motivo
        self.id_reserva = id_reserva


class ParametroFaltanteError(SoftwareFJError):
    """
    Se lanza cuando un parámetro obligatorio no fue proporcionado (None o vacío).
    """
    def __init__(self, parametro: str, contexto: str = ""):
        mensaje = f"Parámetro obligatorio faltante: '{parametro}'"
        if contexto:
            mensaje += f" (en {contexto})"
        super().__init__(mensaje, codigo=4001)
        self.parametro = parametro


class CapacidadExcedidaError(SoftwareFJError):
    """
    Se lanza cuando el número de personas supera la capacidad máxima de una sala.
    """
    def __init__(self, capacidad_max: int, solicitada: int):
        mensaje = (
            f"Capacidad excedida: máximo {capacidad_max} personas, "
            f"se solicitaron {solicitada}"
        )
        super().__init__(mensaje, codigo=2002)
        self.capacidad_max = capacidad_max
        self.solicitada = solicitada


class CostoInconsistenteError(SoftwareFJError):
    """
    Se lanza cuando el cálculo de costos produce un resultado inválido
    (negativo, NaN, infinito, etc.).
    """
    def __init__(self, servicio: str, valor_calculado):
        mensaje = (
            f"Costo inconsistente en '{servicio}': "
            f"resultado inválido → {valor_calculado}"
        )
        super().__init__(mensaje, codigo=2003)
        self.valor = valor_calculado
