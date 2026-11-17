# Software FJ – Sistema Integral de Gestión de Clientes, Servicios y Reservas

Proyecto del curso **Programación (213023)** – UNAD, Fase 4.
Aplicación en Python orientada a objetos, **sin base de datos**: todo se maneja con objetos y listas en memoria; el único archivo que se escribe es el log de eventos y errores.

## Ejecución

```bash
python main.py
```

Requiere Python 3.10 o superior. Se genera el archivo `software_fj.log`.

## Estructura

| Archivo | Contenido |
|---|---|
| `excepciones.py` | Excepciones personalizadas (jerarquía desde `SoftwareFJError`) |
| `registro.py` | Configuración del logger (archivo `software_fj.log`) |
| `entidades.py` | `EntidadBase` (abstracta) y `Cliente` con validaciones y encapsulación |
| `servicios.py` | `Servicio` (abstracta), `ReservaSala`, `AlquilerEquipo`, `Asesoria` |
| `reserva.py` | `Reserva`: confirmar, cancelar y procesar con manejo de excepciones |
| `main.py` | Simulación de 14 operaciones (válidas e inválidas) |

## Conceptos aplicados

- **Abstracción:** `EntidadBase` y `Servicio` (`ABC` + `@abstractmethod`).
- **Herencia y polimorfismo:** tres servicios sobrescriben `validar_parametros`, `costo_base` y `describir`.
- **Encapsulación:** atributos privados con `@property` y validación en cada `setter`.
- **Sobrecarga:** `calcular_costo` admite varias combinaciones (IVA, descuento, parámetro posicional).
- **Excepciones:** personalizadas, `try/except`, `try/except/else`, `try/except/finally` y encadenamiento con `raise ... from`.
- **Logs:** todo error y evento relevante se registra en `software_fj.log`.

## Integrantes

Sergio Esteban Carrillo Farfan
David Correa
Javier Olave
