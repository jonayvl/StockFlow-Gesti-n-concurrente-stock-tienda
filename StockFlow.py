from datos import STOCK_INICIAL, PEDIDOS, NUM_CAJAS
import threading

inventario = STOCK_INICIAL.copy()
pedidos = PEDIDOS.copy()
numeroCajas = []

contador = 0
contaodor_inventario = 0

def Repartir_Procesar():
    global contador , contaodor_inventario
    while True:
            if not pedidos:
                break

            pedido = pedidos[0]

            for producto, unidades in inventario.items():
                if pedido[1] == producto:
                    if pedido[2] <= unidades:
                        inventario[producto] -= pedido[2]
                        pedidos.pop(0)
                        print(f"consumido el pedido : {pedido} por la caja: {threading.current_thread().name}")
                        contaodor_inventario += 1
                        
                    else:
                        contador += 1
                        pedidos.pop(0)
                        print(f"sin stock para el pedido : {pedido} (caja {threading.current_thread().name})")
                    break
            else:
                pedidos.pop(0)
                print(f"pedido {pedido} descartado: producto inexistente")



                
for i in range(NUM_CAJAS):
    hilo = threading.Thread(target=Repartir_Procesar, name=f"{i + 1}")
    numeroCajas.append(hilo)
    hilo.start()

for hilo in numeroCajas:
    hilo.join()


print(contador)
print(contaodor_inventario)