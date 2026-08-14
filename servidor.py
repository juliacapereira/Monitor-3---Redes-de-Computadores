import socket

servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor.bind(("127.0.0.1", 5000))
servidor.listen()

print("Esperando conexão")
