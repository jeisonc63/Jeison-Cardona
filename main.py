"""
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Software FJ - Desarrollado por: [Tu nombre]
Materia: Programación Orientada a Objetos
"""

import os
import sys
from datetime import datetime

# Asegurar que el directorio de logs exista
os.makedirs("logs", exist_ok=True)

from exceptions import (
    ClienteInvalidoError, ServicioNoDisponibleError,
    ReservaInvalidaError, ParametroFaltanteError, CapacidadExcedidaError
)
from logger import Logger
from clientes import Cliente
from servicios import SalaReunion, AlquilerEquipo, AsesoriaTecnica
from reservas import Reserva, GestorReservas

logger = Logger("logs/sistema.log")


def separador(titulo: str):
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print('='*60)


def ejecutar_simulacion():
    """Simula más de 10 operaciones completas del sistema."""

    gestor = GestorReservas(logger)

    # ─────────────────────────────────────────────────────────────
    # BLOQUE 1: Registro de clientes
    # ─────────────────────────────────────────────────────────────
    separador("REGISTRO DE CLIENTES")

    # Operación 1 – Cliente válido
    try:
        c1 = Cliente("Ana García", "ana.garcia@email.com", "3101234567", logger)
        print(f"[OK] Cliente registrado: {c1}")
        logger.info(f"Cliente registrado: {c1.nombre}")
    except ClienteInvalidoError as e:
        print(f"[ERROR] {e}")

    # Operación 2 – Cliente válido
    try:
        c2 = Cliente("Carlos Pérez", "carlos.perez@empresa.com", "3209876543", logger)
        print(f"[OK] Cliente registrado: {c2}")
        logger.info(f"Cliente registrado: {c2.nombre}")
    except ClienteInvalidoError as e:
        print(f"[ERROR] {e}")

    # Operación 3 – Email inválido (error controlado)
    try:
        c_malo = Cliente("Pedro Sin Email", "correo-invalido", "3001112222", logger)
        print(f"[OK] {c_malo}")
    except ClienteInvalidoError as e:
        print(f"[ERROR esperado] {e}")
        logger.warning(f"Intento de registro con email inválido: correo-invalido")

    # Operación 4 – Nombre vacío (error controlado)
    try:
        c_malo2 = Cliente("", "valido@email.com", "3001112222", logger)
    except ClienteInvalidoError as e:
        print(f"[ERROR esperado] {e}")
        logger.warning("Intento de registro con nombre vacío")

    # ─────────────────────────────────────────────────────────────
    # BLOQUE 2: Creación de servicios
    # ─────────────────────────────────────────────────────────────
    separador("CREACIÓN DE SERVICIOS")

    # Operación 5 – Sala de reuniones válida
    try:
        sala_a = SalaReunion("Sala Ejecutiva A", 10, logger)
        print(f"[OK] Servicio: {sala_a.describir()}")
        print(f"     Costo base (2h): ${sala_a.calcular_costo(2):,.0f}")
        print(f"     Con descuento 10%: ${sala_a.calcular_costo(2, descuento=0.10):,.0f}")
        print(f"     Con impuesto 19%: ${sala_a.calcular_costo(2, impuesto=0.19):,.0f}")
        logger.info(f"Servicio creado: {sala_a.nombre}")
    except ServicioNoDisponibleError as e:
        print(f"[ERROR] {e}")

    # Operación 6 – Alquiler de equipo válido
    try:
        equipo_laptop = AlquilerEquipo("Laptop Dell XPS", "laptop", 5, logger)
        print(f"[OK] Servicio: {equipo_laptop.describir()}")
        print(f"     Costo base (3h): ${equipo_laptop.calcular_costo(3):,.0f}")
        logger.info(f"Servicio creado: {equipo_laptop.nombre}")
    except ServicioNoDisponibleError as e:
        print(f"[ERROR] {e}")

    # Operación 7 – Asesoría técnica válida
    try:
        asesoria_cloud = AsesoriaTecnica("Consultoría Cloud AWS", "cloud computing", "Senior", logger)
        print(f"[OK] Servicio: {asesoria_cloud.describir()}")
        print(f"     Costo base (1h): ${asesoria_cloud.calcular_costo(1):,.0f}")
        print(f"     Con descuento 15%: ${asesoria_cloud.calcular_costo(1, descuento=0.15):,.0f}")
        logger.info(f"Servicio creado: {asesoria_cloud.nombre}")
    except ServicioNoDisponibleError as e:
        print(f"[ERROR] {e}")

    # Operación 8 – Sala con capacidad inválida (error controlado)
    try:
        sala_mala = SalaReunion("Sala Fantasma", -5, logger)
    except (ServicioNoDisponibleError, CapacidadExcedidaError) as e:
        print(f"[ERROR esperado] {e}")
        logger.warning("Intento de crear sala con capacidad negativa")

    # ─────────────────────────────────────────────────────────────
    # BLOQUE 3: Gestión de reservas
    # ─────────────────────────────────────────────────────────────
    separador("GESTIÓN DE RESERVAS")

    # Operación 9 – Reserva válida: sala
    try:
        r1 = Reserva(c1, sala_a, 3, logger)
        r1.confirmar()
        print(f"[OK] {r1}")
        print(f"     Costo total: ${r1.calcular_total():,.0f}")
        logger.info(f"Reserva confirmada: {r1.id_reserva}")
    except ReservaInvalidaError as e:
        print(f"[ERROR] {e}")

    # Operación 10 – Reserva válida: asesoría
    try:
        r2 = Reserva(c2, asesoria_cloud, 2, logger)
        r2.confirmar()
        print(f"[OK] {r2}")
        print(f"     Costo total: ${r2.calcular_total():,.0f}")
        print(f"     Costo con IVA (19%): ${r2.calcular_total(impuesto=0.19):,.0f}")
        gestor.agregar_reserva(r2)
        logger.info(f"Reserva confirmada: {r2.id_reserva}")
    except ReservaInvalidaError as e:
        print(f"[ERROR] {e}")

    # Operación 11 – Cancelación de reserva
    try:
        r1.cancelar()
        print(f"[OK] Reserva cancelada: {r1.id_reserva} → Estado: {r1.estado}")
        logger.info(f"Reserva cancelada: {r1.id_reserva}")
    except ReservaInvalidaError as e:
        print(f"[ERROR] {e}")

    # Operación 12 – Reserva con duración inválida
    try:
        r_mala = Reserva(c1, equipo_laptop, -2, logger)
        r_mala.confirmar()
    except ReservaInvalidaError as e:
        print(f"[ERROR esperado] {e}")
        logger.error(f"Reserva inválida: duración negativa")

    # Operación 13 – Reserva sin cliente (None)
    try:
        r_mala2 = Reserva(None, sala_a, 1, logger)
        r_mala2.confirmar()
    except (ReservaInvalidaError, ParametroFaltanteError, TypeError) as e:
        print(f"[ERROR esperado] {type(e).__name__}: {e}")
        logger.error("Intento de reserva sin cliente")

    # ─────────────────────────────────────────────────────────────
    # BLOQUE 4: Operaciones avanzadas con gestor
    # ─────────────────────────────────────────────────────────────
    separador("GESTOR DE RESERVAS")

    gestor.agregar_reserva(r1)

    try:
        r3 = Reserva(c1, equipo_laptop, 4, logger)
        r3.confirmar()
        gestor.agregar_reserva(r3)
        logger.info(f"Reserva adicional: {r3.id_reserva}")
    except Exception as e:
        print(f"[ERROR] {e}")

    print("\n📋 Listado de todas las reservas:")
    gestor.listar_reservas()

    print(f"\n💰 Total facturado: ${gestor.total_facturado():,.0f}")

    # ─────────────────────────────────────────────────────────────
    # BLOQUE 5: Polimorfismo en acción
    # ─────────────────────────────────────────────────────────────
    separador("POLIMORFISMO - COMPARACIÓN DE SERVICIOS")

    servicios = [sala_a, equipo_laptop, asesoria_cloud]
    horas = 2

    for srv in servicios:
        try:
            costo = srv.calcular_costo(horas)
            desc = srv.describir()
            print(f"  • {desc}")
            print(f"    Costo ({horas}h): ${costo:,.0f}\n")
        except Exception as e:
            logger.error(f"Error calculando costo de {srv.nombre}: {e}")
            print(f"[ERROR] {srv.nombre}: {e}")

    separador("SIMULACIÓN FINALIZADA")
    print(f"  Logs guardados en: logs/sistema.log")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*60)


if __name__ == "__main__":
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║       SOFTWARE FJ - Sistema Integral de Gestión         ║")
    print("║       Clientes, Servicios y Reservas                    ║")
    print("╚══════════════════════════════════════════════════════════╝")
    ejecutar_simulacion()
