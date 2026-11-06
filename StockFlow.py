
from datos import (
    STOCK_INICIAL, PEDIDOS, REPOSICIONES,
    NUM_CAJAS, NUM_TERMINALES, NUM_REVISORES
)
import threading
import time


NUM_ALMACENES = 2

pedidos = PEDIDOS.copy()
pendientes = {}

numeroCajas = []
numeroAlmacenes = []
numeroRevisores = []

semaforo_terminales = threading.Semaphore(NUM_TERMINALES)
barrera = threading.Barrier(NUM_REVISORES)


class GestorInventario:

    def __init__(self, stock, reposiciones):
        self.inventario = stock.copy()
        self.reposiciones = reposiciones.copy()
        self.registro = []

        self.lock = threading.RLock()
        self.condicion = threading.Condition(self.lock)

    # Operación protegida
    def registrar(self, mensaje):
        with self.lock:
            self.registro.append(mensaje)

    # Operación protegida que llama a otra operación protegida
    def descontar(self, producto, cantidad, pedido, caja):
        with self.lock:
            if self.inventario[producto] >= cantidad:
                self.inventario[producto] -= cantidad

                self.registrar(
                    f"Consumido el pedido: {pedido} por la caja: {caja}"
                )

                return True

            return False

    # Gestionar las reposiciones
    def reponer(self, producto):
        with self.condicion:
            for r in self.reposiciones:
                if r[1] == producto:
                    self.reposiciones.remove(r)

                    self.inventario[producto] += r[2]

                    self.registrar(
                        f"Almacén {threading.current_thread().name}: "
                        f"{r[0]} repone {r[2]} de {producto}"
                    )

                    self.condicion.notify_all()
                    return True

            return False


# Crear el gestor
gestor = GestorInventario(STOCK_INICIAL, REPOSICIONES)


def hilo_almacen():

    while True:
        with gestor.condicion:

            if not gestor.reposiciones:
                gestor.condicion.notify_all()
                break

            producto = gestor.reposiciones[0][1]
            gestor.reponer(producto)

        time.sleep(0.05)


def Repartir_Procesar():

    caja = threading.current_thread().name

    while True:
        pedido_procesar = None

        with gestor.condicion:

            if not pedidos:
                break

            pedido = pedidos.pop(0)
            producto = pedido[1]
            cantidad = pedido[2]

            if producto in gestor.inventario:

                while (
                    cantidad > gestor.inventario[producto]
                    and gestor.reposiciones
                ):
                    gestor.condicion.wait()

                if cantidad <= gestor.inventario[producto]:

                    if gestor.descontar(
                        producto, cantidad, pedido, caja
                    ):
                        pedido_procesar = pedido

                else:
                    gestor.registrar(
                        f"Sin stock para el pedido: {pedido} "
                        f"(caja {caja})"
                    )

            else:
                gestor.registrar(
                    f"Pedido {pedido} descartado: producto inexistente"
                )

        if pedido_procesar:

            with semaforo_terminales:

                gestor.registrar(
                    f"Caja {caja} OBTIENE terminal de cobro"
                )

                time.sleep(0.01)

                gestor.registrar(
                    f"Caja {caja} LIBERA terminal de cobro"
                )

        time.sleep(0.001)


def revisar():

    revisor = threading.current_thread().name

    while True:

        with gestor.lock:

            if not pendientes:
                break

            producto = pendientes.popitem()[0]

            if gestor.inventario[producto] >= 0:
                estado = "OK"
            else:
                estado = "ERROR"

            gestor.registrar(
                f"{revisor} revisa {producto}: "
                f"{gestor.inventario[producto]} {estado}"
            )

        time.sleep(0.01)

    # Esperar a que terminen todos los revisores
    barrera.wait()

    gestor.registrar(f"{revisor}: cierre autorizado")


# Crear y lanzar almacenes
for i in range(NUM_ALMACENES):

    hilo = threading.Thread(
        target=hilo_almacen,
        name=f"almacen-{i + 1}"
    )

    numeroAlmacenes.append(hilo)
    hilo.start()


# Crear y lanzar cajas
for i in range(NUM_CAJAS):

    hilo = threading.Thread(
        target=Repartir_Procesar,
        name=f"{i + 1}"
    )

    numeroCajas.append(hilo)
    hilo.start()


# Esperar a los almacenes
for hilo in numeroAlmacenes:
    hilo.join()


# Esperar a las cajas
for hilo in numeroCajas:
    hilo.join()


# Preparar inventario para los revisores
with gestor.lock:
    pendientes = gestor.inventario.copy()


# Crear y lanzar revisores
for i in range(NUM_REVISORES):

    hilo = threading.Thread(
        target=revisar,
        name=f"revisor-{i + 1}"
    )

    numeroRevisores.append(hilo)
    hilo.start()


# Esperar a que todos los revisores terminen
for hilo in numeroRevisores:
    hilo.join()


# Mostrar registro
for linea in gestor.registro:
    print(linea)


# Resumen final
print("\n--- RESUMEN FINAL ---")
print(f"Productos revisados: {len(gestor.inventario)}")
print(f"Pedidos pendientes: {len(pedidos)}")
print(f"Reposiciones pendientes: {len(gestor.reposiciones)}")


# Inventario final
print("\n--- INVENTARIO FINAL ---")
print(gestor.inventario)
