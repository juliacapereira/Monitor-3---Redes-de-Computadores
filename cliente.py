import socket
import threading

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect(("127.0.0.1", 5000))



def enviar_comandos():
    while True:
        comando = input("Digite um comando: ")

        cliente.send(comando.encode())

        if comando.lower() == "exit":
            break

def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024)

            if not mensagem:
                break

            print("\nServidor:", mensagem.decode())

        except:
            break

mensagem_inicial = cliente.recv(1024);
print(mensagem_inicial.decode());

thread_envio = threading.Thread(target=enviar_comandos)
thread_recebimento = threading.Thread(target=receber_mensagens)

thread_envio.start()
thread_recebimento.start()

thread_envio.join()


cliente.close()