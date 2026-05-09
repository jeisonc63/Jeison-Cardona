# 🏢 Software FJ – Sistema Integral de Gestión

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![OOP](https://img.shields.io/badge/Paradigma-Orientado%20a%20Objetos-green)
![Status](https://img.shields.io/badge/Estado-Funcional-brightgreen)
![License](https://img.shields.io/badge/Licencia-Educativa-orange)

Sistema de gestión de **clientes, servicios y reservas** para la empresa **Software FJ**, desarrollado íntegramente en Python 3 bajo el paradigma de **Programación Orientada a Objetos**. No utiliza bases de datos; toda la información se gestiona en memoria mediante objetos y listas, con registro de eventos en archivos de log.

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Arquitectura](#arquitectura)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Principios OOP Aplicados](#principios-oop-aplicados)
- [Manejo de Excepciones](#manejo-de-excepciones)
- [Cómo Ejecutar](#cómo-ejecutar)
- [Simulación de Operaciones](#simulación-de-operaciones)
- [Autor](#autor)

---

## 📌 Descripción

Software FJ ofrece tres tipos de servicios:

| Servicio | Descripción | Precio base |
|---|---|---|
| 🏛️ Sala de Reunión | Reserva de salas por hora | $50.000 COP/h |
| 💻 Alquiler de Equipo | Laptop, proyector, servidor | $15.000–$80.000 COP/h |
| 🎓 Asesoría Técnica | Junior / Senior / Expert | $80.000–$250.000 COP/h |

---

## 🏗️ Arquitectura

```
EntidadBase (ABC)
│
├── Cliente
│     ├── Encapsulación: __nombre, __email, __telefono
│     ├── Validación: regex email, teléfono 10 dígitos, nombre ≥ 3 chars
│     └── Propiedades con getters/setters
│
└── Servicio (ABC)
      ├── SalaReunion      → precio base + suplemento capacidad
      ├── AlquilerEquipo   → precio según tipo × cantidad
      └── AsesoriaTecnica  → tarifa según nivel del asesor

Reserva
  └── Integra Cliente + Servicio + duración + estado
        ├── Estados: pendiente → confirmada → cancelada / procesada
        └── Ciclo de vida: confirmar(), cancelar(), procesar()

GestorReservas
  └── Lista interna de reservas, filtros, totales facturados

Logger
  └── Registro de eventos en logs/sistema.log

Excepciones personalizadas
  SoftwareFJError (base)
    ├── ClienteInvalidoError
    ├── ServicioNoDisponibleError
    ├── ReservaInvalidaError
    ├── ParametroFaltanteError
    ├── CapacidadExcedidaError
    └── CostoInconsistenteError
```

---

## 📁 Estructura del Proyecto

```
software_fj/
│
├── main.py           # Punto de entrada y simulación de operaciones
├── clientes.py       # Clase EntidadBase (ABC) y Cliente
├── servicios.py      # Clase Servicio (ABC) + SalaReunion, AlquilerEquipo, AsesoriaTecnica
├── reservas.py       # Clase Reserva y GestorReservas
├── exceptions.py     # Jerarquía de excepciones personalizadas
├── logger.py         # Logger de eventos (escribe en archivo)
├── logs/
│   └── sistema.log   # Generado automáticamente al ejecutar
└── README.md
```

---

## ⚙️ Principios OOP Aplicados

### Abstracción
- `EntidadBase` (ABC): define la interfaz mínima `validar()` y `__str__()`
- `Servicio` (ABC): define `calcular_costo()` y `describir()` que cada servicio implementa a su manera

### Herencia
```python
EntidadBase → Cliente
EntidadBase → Servicio → SalaReunion
                      → AlquilerEquipo
                      → AsesoriaTecnica
```

### Encapsulación
```python
# Cliente: atributos privados con propiedades
@property
def email(self) -> str:
    return self.__email

@email.setter
def email(self, valor: str):
    if not self._PATRON_EMAIL.match(valor):
        raise ClienteInvalidoError("email", valor, "formato inválido")
    self.__email = valor.strip().lower()
```

### Polimorfismo
```python
# Mismo método, comportamiento diferente según el tipo de servicio
for servicio in [sala_a, equipo_laptop, asesoria_cloud]:
    print(servicio.describir())          # descripción propia
    print(servicio.calcular_costo(2))    # cálculo propio
```

### Sobrecarga de métodos (parámetros opcionales)
```python
# Tres variantes del mismo método
sala.calcular_costo(2)                         # precio puro
sala.calcular_costo(2, descuento=0.10)         # con 10% descuento
sala.calcular_costo(2, impuesto=0.19)          # con IVA 19%
sala.calcular_costo(2, descuento=0.10, impuesto=0.19)  # ambos
```

---

## 🚨 Manejo de Excepciones

### Tipos de bloques utilizados

```python
# try / except
try:
    cliente = Cliente("", "email@ok.com", "3001234567", logger)
except ClienteInvalidoError as e:
    print(f"Error esperado: {e}")

# try / except / else
try:
    reserva.confirmar()
except ReservaInvalidaError as e:
    logger.error(str(e))
else:
    logger.info("Reserva confirmada exitosamente")  # solo si no hubo error

# try / except / finally
try:
    reserva.cancelar()
except ReservaInvalidaError:
    logger.warning("Cancelación inválida")
    raise
finally:
    logger.info("Intento de cancelación procesado")  # SIEMPRE

# Encadenamiento de excepciones
except ServicioNoDisponibleError as e:
    raise ReservaInvalidaError(str(e), self._id) from e
```

### Jerarquía de excepciones

| Excepción | Código | Cuándo se lanza |
|---|---|---|
| `SoftwareFJError` | Base | Clase raíz |
| `ClienteInvalidoError` | 1001 | Email/nombre/teléfono inválidos |
| `ServicioNoDisponibleError` | 2001 | Servicio con parámetros incorrectos |
| `CapacidadExcedidaError` | 2002 | Asistentes > capacidad sala |
| `CostoInconsistenteError` | 2003 | Cálculo produce valor inválido |
| `ReservaInvalidaError` | 3001 | Duración negativa, estado incorrecto |
| `ParametroFaltanteError` | 4001 | Argumento `None` u omitido |

---

## ▶️ Cómo Ejecutar

### Requisitos
- Python 3.10 o superior
- Sin dependencias externas (solo biblioteca estándar)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/software-fj.git
cd software-fj

# 2. Ejecutar el sistema
python main.py
```

### Salida esperada
```
╔══════════════════════════════════════════════════════════╗
║       SOFTWARE FJ - Sistema Integral de Gestión         ║
║       Clientes, Servicios y Reservas                    ║
╚══════════════════════════════════════════════════════════╝

============================================================
  REGISTRO DE CLIENTES
============================================================
[OK] Cliente(nombre='Ana García', email='ana.garcia@email.com', tel='3101234567')
[OK] Cliente(nombre='Carlos Pérez', email='carlos.perez@empresa.com', tel='3209876543')
[ERROR esperado] [Código 1001] Cliente inválido – Campo 'email': 'correo-invalido' → formato de correo inválido
...
```

El archivo `logs/sistema.log` se genera automáticamente con todos los eventos.

---

## 🔄 Simulación de Operaciones (≥ 10)

| # | Operación | Resultado Esperado |
|---|---|---|
| 1 | Registrar cliente válido (Ana García) | ✅ Creado |
| 2 | Registrar cliente válido (Carlos Pérez) | ✅ Creado |
| 3 | Registrar cliente con email inválido | ❌ `ClienteInvalidoError` |
| 4 | Registrar cliente con nombre vacío | ❌ `ClienteInvalidoError` |
| 5 | Crear Sala Ejecutiva A (cap. 10) | ✅ Creada |
| 6 | Crear Alquiler Laptop Dell (5 unidades) | ✅ Creado |
| 7 | Crear Asesoría Cloud AWS (Senior) | ✅ Creada |
| 8 | Crear sala con capacidad negativa | ❌ `ServicioNoDisponibleError` |
| 9 | Reservar sala 3 horas → confirmar | ✅ Confirmada |
| 10 | Reservar asesoría 2 horas → confirmar | ✅ Confirmada |
| 11 | Cancelar reserva de sala | ✅ Cancelada |
| 12 | Reservar equipo con duración negativa | ❌ `ReservaInvalidaError` |
| 13 | Reservar sin cliente (None) | ❌ `ParametroFaltanteError` |
| 14 | Comparación polimórfica de servicios | ✅ Descripción y costo por tipo |

---

## 👤 Autor

**[Tu Nombre Completo]**  
Estudiante de Ingeniería de Sistemas  
Materia: Programación Orientada a Objetos  
Institución: [Tu Universidad]  
Año: 2025

---

> *"El código limpio hace una cosa bien. La programación orientada a objetos lo hace con elegancia."*
