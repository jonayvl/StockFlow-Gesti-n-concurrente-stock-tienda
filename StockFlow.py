from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS
import threading
import time

inventario = STOCK_INICIAL.copy()
pedidos = PEDIDOS.copy()
numeroCajas = []
registro = []                                   # nuevo: aquí se guardan los mensajes
lock = threading.Lock()


def Repartir_Procesar():                            # ahora sí se usa la barrera
    while True:
        with lock:
            if not pedidos:
                break

            pedido = pedidos[0]
            producto = pedido[1]
            cantidad = pedido[2]
            caja = threading.current_thread().name

            if producto in inventario:
                if cantidad <= inventario[producto]:
                    inventario[producto] -= cantidad
                    pedidos.pop(0)
                    registro.append(f"consumido el pedido : {pedido} por la caja: {caja}")
                else:
                    pedidos.pop(0)
                    registro.append(f"sin stock para el pedido : {pedido} (caja {caja})")
            else:
                pedidos.pop(0)
                registro.append(f"pedido {pedido} descartado: producto inexistente")

        time.sleep(0.001)                        


for i in range(NUM_CAJAS):
    hilo = threading.Thread(target=Repartir_Procesar, name=f"{i + 1}")
    numeroCajas.append(hilo)
    hilo.start()

for hilo in numeroCajas:
    hilo.join()

for linea in registro:                          # se imprime todo al final
    print(linea)
print(inventario)