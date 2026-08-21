import socket
import threading
import time
import psutil
from datetime import datetime

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("127.0.0.1", 5000))
servidor.listen()

print("Esperando conexão")

conexao, endereco = servidor.accept()

print("Cliente conectado:", endereco)

parar_cpu = threading.Event();

encerrar = threading.Event();

horario = datetime.now().strftime("%H:%M:%S")
mensagem = f"{horario}: CONECTADO!!"

conexao.send(mensagem.encode())


def monitor_cpu(intervalo):

    print("Thread CPU iniciada");

    

    while not parar_cpu.is_set():
        uso_cpu = psutil.cpu_percent()

        mensagem = f"CPU: {uso_cpu}%"

        conexao.send(mensagem.encode())

        parar_cpu.wait(intervalo);

    print("Thread CPU encerrada");

    conexao.send("Monitoramento finalizado.".encode());    


def receber_comandos():

    while not encerrar.is_set():
        try:
            dados = conexao.recv(1024)

            if not dados:
                break

            comando = dados.decode().strip();

            print("Comando:", comando)

            if comando.lower() == "exit":
                parar_cpu.set()
                encerrar.set()
                break

            if comando.lower() == "quit":
                parar_cpu.set();
                continue;

            partes = comando.split("-")

            if partes[0].lower() == "cpu":
                intervalo = int(partes[1])

                parar_cpu.clear();

                thread_cpu = threading.Thread(
                    target=monitor_cpu,
                    args=(intervalo,)
                )

                thread_cpu.start()

        except:
            break


thread_recebimento = threading.Thread(target=receber_comandos)

thread_recebimento.start()

thread_recebimento.join()

conexao.close()
servidor.close()

print("Servidor Encerrado");