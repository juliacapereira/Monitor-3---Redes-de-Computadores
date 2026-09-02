import socket
import threading

HOST ="127.0.0.1"
PORT = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cliente.connect((HOST,PORT))

def enviar_comandos():
    while True:
        try:
            comando = input("Digite um comando: ")
        except (EOFError, KeyboardInterrupt):
            comando = "exit"

        try:
            cliente.send(comando.encode())
        except:
            break

        if comando.lower() == "exit":
            break

def receber_mensagens():
    while True:
        try:
            mensagem = cliente.recv(1024)

            if not mensagem:
                print("\nConexão encerrada pelo servidor.")
                break

            print("\nServidor--", mensagem.decode())

        except:
            break

mensagem_inicial = cliente.recv(1024);
texto_inicial = mensagem_inicial.decode();
print(texto_inicial);

if "CONECTADO" not in texto_inicial:
    print("Não foi possível conectar, encerrando cliente.")
    cliente.close()

else:
    thread_envio = threading.Thread(target=enviar_comandos)
    thread_recebimento = threading.Thread(target=receber_mensagens)
    thread_envio.start()
    thread_recebimento.start()
    thread_envio.join()
    cliente.close()