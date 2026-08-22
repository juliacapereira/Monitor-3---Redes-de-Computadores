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

parar_cpu = threading.Event()
parar_memoria = threading.Event()
encerrar = threading.Event()

horario = datetime.now().strftime("%H:%M:%S")
mensagem = f"""{horario}: CONECTADO!! 
Comandos:
CPU-<intervalo> 
memoria-<intervalo>
Quit-CPU
Quit-memoria
Exit"""

conexao.send(mensagem.encode())

def monitor_memoria(intervalo):
    print("Thread Memória iniciada");

    while not parar_memoria.is_set():

        uso_memoria = psutil.virtual_memory().percent;

        mensagem= f"Memória: {uso_memoria}%";
        conexao.send(mensagem.encode());

        parar_memoria.wait(intervalo);
    
    print("Thread de memória encerrada");
    conexao.send("Monitoramento de memória encerrado".encode());
        
def monitor_cpu(intervalo):

    print("Thread CPU iniciada");

    while not parar_cpu.is_set():
        uso_cpu = psutil.cpu_percent()

        mensagem = f"CPU: {uso_cpu}%"

        conexao.send(mensagem.encode())

        parar_cpu.wait(intervalo)

    print("Thread de CPU encerrada");
    conexao.send("Monitoramento finalizado".encode());    

def receber_comandos():

    while not encerrar.is_set():
        try:
            dados = conexao.recv(1024)

            if not dados:
                break

            comando = dados.decode().strip();

            print("Comando:", comando)

            if comando.lower() == "exit":
                parar_cpu.set();
                parar_memoria.set();
                encerrar.set();
                break;

            partes = comando.split("-")

            if partes[0].lower() == "quit":
                if partes[1].lower() == "cpu":
                    parar_cpu.set()
                if partes[1].lower() == "memoria" or partes[1].lower() == "memória":
                    parar_memoria.set()
                continue;

            if partes[0].lower() == "cpu":
                intervalo = int(partes[1])

                parar_cpu.clear();

                thread_cpu = threading.Thread(
                    target=monitor_cpu,
                    args=(intervalo,)
                )

                thread_cpu.start()

            if partes[0].lower() == "memoria" or partes[0].lower() == "memória":

                intervalo = int(partes[1]);

                parar_memoria.clear();

                thread_memoria = threading.Thread(
                    target=monitor_memoria,
                    args=(intervalo,)
                )
                thread_memoria.start()

        except:
            break


thread_recebimento = threading.Thread(target=receber_comandos)

thread_recebimento.start()

thread_recebimento.join()

conexao.close()
servidor.close()

print("Servidor encerrado");