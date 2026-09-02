import socket
import threading
import psutil
from datetime import datetime

HOST = "127.0.0.1";
PORT = 5000;

print("Esperando conexão")

def tratar_cliente(conexao, endereco):

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

    try:
        conexao.send(mensagem.encode());
    except:
        conexao.close();
        return;

    def monitor_memoria(intervalo):
        print(f"[{endereco}]Thread Memória iniciada");

        while not parar_memoria.is_set():

            uso_memoria = psutil.virtual_memory().percent;

            mensagem= f"Memória: {uso_memoria}%";
            conexao.send(mensagem.encode());

            parar_memoria.wait(intervalo);
        
        print("Thread de memória encerrada");
        conexao.send("Monitoramento de memória encerrado".encode());
        
    def monitor_cpu(intervalo):

        print(f"[{endereco}]Thread CPU iniciada");

        while not parar_cpu.is_set():
            uso_cpu = psutil.cpu_percent()

            mensagem = f"CPU: {uso_cpu}%"

            conexao.send(mensagem.encode())

            parar_cpu.wait(intervalo)

        print("Thread de CPU encerrada");
        conexao.send("Monitoramento finalizado".encode());    



    try:
        while not encerrar.is_set():
            try:
                dados = conexao.recv(1024)

                if not dados:
                    break

                comando = dados.decode().strip();
            except Exception:
                break;

            print(f"[{endereco}[Comando:", comando)



            if comando.lower() == "exit":
                parar_cpu.set();
                parar_memoria.set();
                encerrar.set();
                break;

            partes = comando.split("-")

            if partes[0].lower() == "quit":
                if len(partes) < 2:
                    conexao.send("Comando Inválido. Use Quit-CPU ou Quit-memoria".encode());
                    continue;
                if partes[1].lower() == "cpu":
                    parar_cpu.set()
                if partes[1].lower() == "memoria" or partes[1].lower() == "memória":
                    parar_memoria.set()
                else:
                    conexao.send("Comando não reconhecido".encode())
                    continue;

            if partes[0].lower() == "cpu":

                if len(partes) < 2:
                    conexao.send("Comando Inválido. Use CPU-<segundos>".encode());
                    continue;

                
                try:
                    intervalo = int(partes[1])
                except ValueError:
                    conexao.send("Intervalo Inválido. Use um número inteiro".encode());
                    continue;

                parar_cpu.clear()
                threading.Thread(target=monitor_cpu, args=(intervalo,), daemon=True).start()
                continue

            if partes[0].lower() == "memoria" or partes[0].lower() == "memória":

                if len(partes) < 2:
                    conexao.send("Comando Inválido. Use memoria-<segundos>".encode());
                    continue;

                try:
                    intervalo = int(partes[1])
                except ValueError:
                    conexao.send("Intervalo Inválido. Use um número inteiro".encode());
                    continue

                parar_memoria.clear();

                threading.Thread(target=monitor_memoria, args=(intervalo,), daemon=True).start()
                continue

            conexao.send("Comando não reconhecido".encode());
            
    finally:
        parar_cpu.set()
        parar_memoria.set()
        conexao.close()
        print(f"Cliente desconectado: {endereco}")

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"Servidor no ar em {HOST}:{PORT}")
    print("Esperando conexões...")

    try:
        while True:
            conexao, endereco = servidor.accept()

            thread_cliente = threading.Thread(
                target=tratar_cliente,
                args=(conexao, endereco),
                daemon=True
            )
            thread_cliente.start()
    except KeyboardInterrupt:
        print("\nEncerrando servidor...")
    finally:
        servidor.close()
        print("Servidor encerrado")

if __name__ == "__main__":
    main()