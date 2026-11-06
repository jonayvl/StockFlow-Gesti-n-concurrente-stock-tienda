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