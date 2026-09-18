import socket
import threading
import sys

HOST ="127.0.0.1"
PORT = 5000

cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    cliente.connect((HOST, PORT))

except ConnectionRefusedError:
    print("Não foi possível conectar ao servidor")
    cliente.close()
    sys.exit()

except OSError as erro:
    print("Erro de conexão:", erro)
    cliente.close()
    sys.exit()

def enviar_comandos():
    while True:
        try:
            comando = input("Digite um comando: ")
        except (EOFError, KeyboardInterrupt):
            comando = "exit"

        try:
            cliente.send(comando.encode())
        except OSError:
            print("\nNão foi possível enviar, conexão com o servidor perdida.")
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

        except ConnectionResetError:
            print("\nConexão encerrada pelo servidor")
            break

        except OSError:
            print("\nErro na conexão com o servidor")
            break
try:
    mensagem_inicial = cliente.recv(1024);

    if not mensagem_inicial:
        print("Conexão encerrada pelo servidor")
        cliente.close()
        sys.exit()
except OSError:
    print("Erro na conexão com o servidor")
    cliente.close()
    sys.exit()


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
    thread_recebimento.join()
    cliente.close()