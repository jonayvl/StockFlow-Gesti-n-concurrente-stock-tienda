from datos import STOCK_INICIAL, PEDIDOS, REPOSICIONES, NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES
import threading
import time

NUM_ALMACENES = 2

inventario = STOCK_INICIAL.copy()
pedidos = PEDIDOS.copy()
reposiciones = REPOSICIONES.copy()

numeroCajas = []
numeroAlmacenes = []
numeroRevisores = []
registro = []
revisados = 0  # CAMBIADO

lock = threading.Lock()
semaforo_terminales = threading.Semaphore(NUM_TERMINALES)  # CAMBIADO: sin lock_terminales
condicion = threading.Condition(lock)
barrera = threading.Barrier(NUM_REVISORES)


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
            with semaforo_terminales:  # CAMBIADO
                with lock:
                    registro.append(f"Caja {caja} OBTIENE terminal de cobro")

                time.sleep(0.01)

                with lock:
                    registro.append(
                        f"consumido el pedido : {pedido_procesar} por la caja: {caja}"
                    )
                    registro.append(f"Caja {caja} LIBERA terminal de cobro")

        time.sleep(0.001)


def revisar():  # CAMBIADO
    global revisados
    revisor = threading.current_thread().name

    while True:
        with lock:
            if not pendientes:
                break

            producto = pendientes.popitem()[0]
            revisados += 1

            if inventario[producto] >= 0:
                estado = "OK"
            else:
                estado = "ERROR"

            registro.append(
                f"{revisor} revisa {producto}: {inventario[producto]} {estado}"
            )

        time.sleep(0.01)

    barrera.wait()

    with lock:
        registro.append(f"{revisor}: cierre autorizado")


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

pendientes = inventario.copy()

for i in range(NUM_REVISORES):
    hilo = threading.Thread(
        target=revisar,
        name=f"revisor-{i + 1}"
    )
    numeroRevisores.append(hilo)
    hilo.start()

for hilo in numeroRevisores:
    hilo.join()

for linea in registro:
    print(linea)

print("\n--- RESUMEN FINAL ---")
print(f"Productos revisados: {revisados}")  # CAMBIADO
print(f"Pedidos pendientes: {len(pedidos)}")
print(f"Reposiciones pendientes: {len(reposiciones)}")

print("\n--- INVENTARIO FINAL ---")
print(inventario)