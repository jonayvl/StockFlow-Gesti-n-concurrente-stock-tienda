from datos import STOCK_INICIAL, PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES
import threading
import time

NUM_ALMACENES = 2

inventario = STOCK_INICIAL.copy()
pedidos = PEDIDOS.copy()
reposiciones = REPOSICIONES.copy()

numeroCajas = []
numeroAlmacenes = []
registro = []

lock = threading.Lock()
lock_terminales = threading.RLock()
semaforo_terminales = threading.Semaphore(NUM_TERMINALES)
condicion = threading.Condition(lock)


def reponer(producto):
    nombre = threading.current_thread().name

    for r in reposiciones:
        if r[1] == producto:
            reposiciones.remove(r)
            inventario[producto] += r[2]
            registro.append(
                f"Almacén {nombre}: {r[0]} repone {r[2]} de {producto}"
            )
            condicion.notify_all()
            return True

    return False


def hilo_almacen():
    while True:
        with condicion:
            if not reposiciones:
                condicion.notify_all()
                break

            reponer(reposiciones[0][1])

        time.sleep(0.05)


def Repartir_Procesar():
    caja = threading.current_thread().name

    while True:
        pedido_procesar = None

        with condicion:
            if not pedidos:
                break

            pedido = pedidos.pop(0)
            producto = pedido[1]
            cantidad = pedido[2]

            if producto in inventario:
                while cantidad > inventario[producto] and reposiciones:
                    condicion.wait()
                

                if cantidad <= inventario[producto]:
                    inventario[producto] -= cantidad
                    pedido_procesar = pedido
                else:
                    registro.append(
                        f"sin stock para el pedido : {pedido} (caja {caja})"
                    )
            else:
                registro.append(
                    f"pedido {pedido} descartado: producto inexistente"
                )

        if pedido_procesar:
            with lock_terminales:
                semaforo_terminales.acquire()

            with lock:
                registro.append(f"Caja {caja} OBTIENE terminal de cobro")

            time.sleep(0.01)

            with lock:
                registro.append(
                    f"consumido el pedido : {pedido_procesar} por la caja: {caja}"
                )
                registro.append(f"Caja {caja} LIBERA terminal de cobro")

            semaforo_terminales.release()

        time.sleep(0.001)


for i in range(NUM_ALMACENES):
    hilo = threading.Thread(
        target=hilo_almacen,
        name=f"almacen-{i + 1}"
    )
    numeroAlmacenes.append(hilo)
    hilo.start()

for i in range(NUM_CAJAS):
    hilo = threading.Thread(
        target=Repartir_Procesar,
        name=f"{i + 1}"
    )
    numeroCajas.append(hilo)
    hilo.start()

for hilo in numeroAlmacenes:
    hilo.join()

for hilo in numeroCajas:
    hilo.join()

for linea in registro:
    print(linea)

print("\n--- INVENTARIO FINAL ---")
print(inventario)