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
| Santiago Rios Bonilla | main.py, Test | riosbonilla93-art |
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

## Aporte de Santiago Rios

### 1. Programa principal y menú interactivo (`main.py`)
- `main.py`: implementación del punto de entrada del sistema mediante un menú interactivo en consola (`while True` e `input()`) para gestionar clientes, servicios (salas, equipos y asesorías) y el ciclo completo de reservas en memoria (sin bases de datos).
- **Control robusto de errores:** encapsulamiento de todas las entradas del usuario y llamadas a la lógica de negocio mediante bloques `try / except / else / finally`, capturando tanto errores de entrada (`ValueError`, `IndexError`) como las excepciones personalizadas del dominio (`ErrorSoftwareFJ` y derivadas) para evitar cierres inesperados y garantizar el registro automático en `logs/software_fj.log`.
- **Simulación automática obligatoria:** integración de la rutina de simulación de 10 operaciones completas (combinando registros válidos e inválidos de clientes, creación correcta e incorrecta de servicios y reservas exitosas y fallidas), demostrando la estabilidad y resiliencia del sistema ante fallos.

### 2. Suite de pruebas unitarias (`tests/`)
- `tests/test_sistema.py`: desarrollo de las pruebas automatizadas utilizando la librería estándar `unittest` para verificar la integridad y el correcto funcionamiento de todo el modelo orientado a objetos.
- **Cobertura de validación:**
  - Creación exitosa de instancias de `Cliente` y verificación del lanzamiento de `ClienteInvalidoError` ante datos mal formados (correos inválidos, documentos o campos vacíos).
  - Validación del comportamiento polimórfico y métodos sobrecargados en el cálculo de costos (`calcular_costo`, con impuestos y descuentos) para `ReservaSala`, `AlquilerEquipo` y `AsesoriaEspecializada`.
  - Pruebas de flujo de estados y manejo de excepciones en `Reserva` (confirmación, cancelación, procesamiento y bloqueo de operaciones no permitidas).
