# StockFlow-Gesti-n-concurrente-stock-tienda

Gestión concurrente de stock en Python: de la condición de carrera a la sincronización de hilos (PSP · UD2 · 2º DAM).

## Fase 1: Análisis de Concurrencia y Condición de Carrera

### 1. Sección Crítica

La sección crítica se encuentra en el bloque donde múltiples hilos (cajas) acceden, leen y modifican simultáneamente el recurso compartido `inventario`:

```python
if pedido[2] <= unidades:
    inventario[producto] -= pedido[2] concurrente sin protección
```

**¿Por qué es crítica?**

Esta operación de "leer y restar" no es atómica. Si dos cajas leen el mismo stock disponible al mismo tiempo, ambas validarán el pedido de manera independiente y descontarán unidades, lo que provoca que el inventario real quede desincronizado o alcance valores negativos.

### 2. Resultados Inconsistentes

Al no utilizar ningún mecanismo de exclusión mutua (`Lock`), la ejecución múltiple de la aplicación revela:

- **Condiciones de carrera:** Las cajas compiten de forma descontrolada por las últimas unidades de un mismo producto.
- **Anomalías detectadas:** Stock restante en negativo y variación inestable en los contadores globales (`contador` y `contador_inventario`) según el orden de ejecución de los hilos.

## Fase 6 · Refactorización con RLock

En esta fase he organizado el código creando una clase llamada `GestorInventario`, para tener todo lo relacionado con el inventario más ordenado.

Dentro de la clase he metido el inventario, las reposiciones, el registro y los mecanismos de sincronización que se utilizan para proteger los datos.

También he creado dos métodos:

- `descontar()`: comprueba si hay stock suficiente y, si lo hay, descuenta las unidades del producto.
- `registrar()`: guarda en el registro los mensajes de las operaciones realizadas.

### ¿Por qué utilizo RLock?

He utilizado `RLock` porque en este caso un método necesita llamar a otro mientras ya tiene adquirido el cerrojo.

Por ejemplo, cuando se ejecuta `descontar()`, primero se adquiere el cerrojo y después se llama a `registrar()`, que también necesita utilizarlo.

Si utilizara un `Lock` normal, el programa se quedaría bloqueado porque intentaría adquirir el mismo cerrojo dos veces desde el mismo hilo.

Con `RLock` esto no ocurre, ya que permite que el mismo hilo pueda adquirir el cerrojo varias veces sin bloquearse.

## Fase 7 · Prevención de deadlock

En esta fase he revisado los mecanismos de sincronización utilizados en el programa para evitar posibles bloqueos entre los hilos.

### 1. Recursos de sincronización utilizados

En el programa se utilizan los siguientes mecanismos:

- `RLock`: protege el acceso al inventario y al registro de operaciones. También permite que un método protegido pueda llamar a otro método que utiliza el mismo cerrojo.
- `Condition`: permite que las cajas esperen cuando no hay suficiente stock. Mientras esperan, liberan temporalmente el cerrojo para que los almacenes puedan realizar las reposiciones.
- `Semaphore`: limita el número de cajas que pueden utilizar los terminales de cobro al mismo tiempo.
- `Barrier`: permite que los revisores esperen hasta que todos hayan terminado su trabajo antes de continuar con el cierre.

### 2. Orden de adquisición de recursos

Para evitar posibles bloqueos, se ha tenido en cuenta el orden en el que se utilizan los mecanismos de sincronización.

Las cajas realizan las operaciones sobre el inventario utilizando `Condition` y `RLock`. Una vez terminada esa parte, salen del bloque protegido y solicitan un terminal mediante `Semaphore`.

De esta forma, una caja no mantiene bloqueado el inventario mientras espera a que quede libre un terminal de cobro.

También se evita mantener los cerrojos durante operaciones que no necesitan proteger datos compartidos, como las pausas realizadas con `time.sleep()`.

### 3. Posible situación de deadlock

Un posible deadlock podría producirse si dos hilos adquieren los mismos recursos en un orden diferente.

Por ejemplo:

- El hilo A adquiere el `RLock` y después intenta conseguir el `Semaphore`.
- El hilo B adquiere el `Semaphore` y después intenta conseguir el `RLock`.

Si ambos se quedan esperando por el recurso que tiene el otro hilo, ninguno podrá continuar y el programa quedará bloqueado.

### 4. ¿Cómo se evita?

Para evitar esta situación, el programa sigue un orden de trabajo en el que las cajas terminan primero las operaciones protegidas del inventario y después solicitan el terminal de cobro.

Además, se procura liberar los recursos lo antes posible y no mantenerlos ocupados mientras se realizan esperas innecesarias.

Con estas medidas se reducen las posibilidades de que los hilos se queden bloqueados esperando unos por otros.