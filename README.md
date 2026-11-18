# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Curso Programación (213023) – UNAD – Fase 4: Prácticas simuladas. Grupo 213023_404.
Proyecto en Python orientado a objetos, sin bases de datos; el único archivo
que se escribe es el log de eventos y errores (`logs/software_fj.log`).

## Estructura
- `software_fj/excepciones.py` – excepciones personalizadas.
- `software_fj/registro_logs.py` – configuración del archivo de logs.
- `software_fj/entidad_base.py` – clase abstracta de entidades generales.
- `software_fj/servicios/` – clase abstracta `Servicio` y servicios hijos.
- `demo_servicios.py` – simulación de 14 operaciones (válidas e inválidas).

## Ejecución
```
python demo_servicios.py
```

## Distribución del trabajo
| Integrante | Responsabilidad | Usuario GitHub |
|---|---|---|
| Kevin David Rojas Ibarra | Servicio + servicios hijos + Reserva + excepciones, logs e integración | KevinRojasI |
| Arleth Juliana Ramirez Huertas | entidad abstracta + Cliente + `main.py` + README + pruebas | ajramirezzh-arch |

## Aporte de Kevin David Rojas Ibarra

### 1. Clase abstracta `Servicio` y servicios hijos
- `software_fj/servicios/servicio.py`: clase abstracta con datos encapsulados y validados, control de disponibilidad y cálculo de costos sobrecargado (`calcular_costo`, `calcular_costo_con_impuesto`, `calcular_costo_con_descuento`). Obliga a cada hijo a implementar `calcular_costo_base`, `validar_parametros` y `describir`.
- `reserva_sala.py`, `alquiler_equipo.py` y `asesoria_especializada.py`: tres servicios especializados que sobrescriben las reglas de validación, costo y descripción (polimorfismo).
- `demo_servicios.py`: simula 14 operaciones válidas e inválidas.

### 2. Clase `Reserva`
- `software_fj/reserva.py`: integra cliente, servicio, duración y estado (`EstadoReserva`: PENDIENTE, CONFIRMADA, CANCELADA, PROCESADA).
- Métodos `confirmar()`, `cancelar()` y `procesar()` con try/except/else/finally; las transiciones no permitidas lanzan `OperacionNoPermitidaError` y los fallos de cálculo se encadenan a `ReservaInvalidaError` (`raise ... from error`).
- `demo_reservas.py`: simula 15 operaciones sobre reservas.

### 3. Excepciones, logs e integración
- `software_fj/excepciones.py`: jerarquía con base `ErrorSoftwareFJ` y códigos de error: SFJ-001 parámetro inválido, SFJ-002 servicio no disponible, SFJ-003 cálculo inconsistente, SFJ-004 cliente inválido, SFJ-005 reserva inválida, SFJ-006 operación no permitida.
- `software_fj/registro_logs.py`: registro de eventos y errores en `logs/software_fj.log`.
- Integración: `Servicio` y `Reserva` heredan de `EntidadBase`; `Cliente` pasó a lanzar `ClienteInvalidoError` (compatible con `ValueError`).

### Cómo ejecutar
```
python demo_servicios.py
python demo_reservas.py
```
