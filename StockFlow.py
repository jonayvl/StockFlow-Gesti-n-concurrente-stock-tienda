from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS , NUM_TERMINALES
import threading
import time

inventario = STOCK_INICIAL.copy()
pedidos = PEDIDOS.copy()
numeroCajas = []
registro = []                                  
lock = threading.Lock()

semaforo_terminales = threading.Semaphore(NUM_TERMINALES)
lock_terminales = threading.RLock()

def Repartir_Procesar():
    caja = threading.current_thread().name                           
    while True:
        pedido_procesar = None
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
                    pedido_procesar = pedido 
                else:
                    pedidos.pop(0)
                    registro.append(f"sin stock para el pedido : {pedido} (caja {caja})")
            else:
                pedidos.pop(0)
                registro.append(f"pedido {pedido} descartado: producto inexistente")
        
        if pedido_procesar:
            with lock_terminales:
                semaforo_terminales.acquire()

            with lock:
                registro.append(f"Caja {caja} OBTIENE terminal de cobro")        

            time.sleep(0.01)
        
            with lock:
                registro.append(f"consumido el pedido : {pedido_procesar} por la caja: {caja}")
                registro.append(f"Caja {caja} LIBERA terminal de cobro")            

            semaforo_terminales.release()


for i in range(NUM_CAJAS):
    hilo = threading.Thread(target=Repartir_Procesar, name=f"{i + 1}")
    numeroCajas.append(hilo)
    hilo.start()

for hilo in numeroCajas:
    hilo.join()

for linea in registro:                          
    print(linea)

print("\n--- INVENTARIO FINAL ---")
print(inventario)