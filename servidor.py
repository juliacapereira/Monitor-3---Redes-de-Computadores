import socket
import threading
import psutil
import sys
from datetime import datetime

HOST = "127.0.0.1";
PORT = 5000;

if len(sys.argv)>1:
    valor = sys.argv[1]

else:
    valor = input ("Digite o número maximo de clientes:")
while True:
    try:
        max_clientes = int(valor)

        if max_clientes<=0:
            print("O número de clientes deve ser maior que zero.")
            valor = input("Digite o número maximo de clientes:")
            continue
        break

    except ValueError:
        print("Valor inválido.")
    valor = input("Digite o número maximo de clientes:")

clientes_conectados = 0
lock_clientes = threading.Lock()


def tratar_cliente(conexao, endereco):

    global clientes_conectados

    with lock_clientes:

        if(clientes_conectados>=max_clientes):
            try:
                conexao.send("Limite de clientes atingido".encode());
            except:
                pass
            conexao.close();
            print(f"Cliente {endereco} recusado" 
                  f"limite de {max_clientes} atingido")

            return

        clientes_conectados+=1
    print(f"Cliente conectado: {endereco} - ({clientes_conectados}/{max_clientes})");

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
        liberar_vaga(endereco);
        return

    def monitor_memoria(intervalo):
        print(f"[{endereco}]Thread Memória iniciada");

        while not parar_memoria.is_set():

            uso_memoria = psutil.virtual_memory().percent;
            try:
                conexao.send(f"Memória: {uso_memoria}%".encode());
            except:
                break;
            parar_memoria.wait(intervalo);
        
        print(f"[{endereco}]Thread de memória encerrada");
        try:
            conexao.send("Monitoramento de memória encerrado".encode());
        except:
            pass

    def monitor_cpu(intervalo):
        print(f"[{endereco}]Thread CPU iniciada");

        while not parar_cpu.is_set():
            uso_cpu = psutil.cpu_percent()

            try:
                conexao.send(f"CPU: {uso_cpu}%".encode())
            except:
                break

            parar_cpu.wait(intervalo)

        print(f"[{endereco}] Thread de CPU encerrada");
        try:
            conexao.send("Monitoramento finalizado".encode()); 
        except:
            pass

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
        liberar_vaga(endereco)


    def liberar_vaga(endereco):
        global clientes_desconectados
        with lock_clientes:
            clientes_conectados-=1;
        print(f"Clientes desconectado: {endereco} ({clientes_conectados}/{max_clientes})")

def main():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind((HOST, PORT))
    servidor.listen()

    print(f"Servidor no ar em {HOST}:{PORT} com espaço para {max_clientes} clientes")
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