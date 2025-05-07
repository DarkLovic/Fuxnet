# Author: FAZ-28 
# Description: This module acts as a proxy 
import socket
import threading
import struct
import select

BUFFER_SIZE = 4096

class Socks5Server:
    def __init__(self, host='::', port=1080):
        self.host = host
        self.port = port

    def start(self):
        server = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(100)
        print(f"[+] SOCKS5 proxy server listening on [{self.host}]:{self.port}")

        while True:
            client, addr = server.accept()
            threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()

    def handle_client(self, client_sock):
        try:
            version, nmethods = struct.unpack("!BB", client_sock.recv(2))
            if version != 5:
                client_sock.close()
                return
            client_sock.recv(nmethods)
            client_sock.sendall(struct.pack("!BB", 5, 0))

            version, cmd, _, atyp = struct.unpack("!BBBB", client_sock.recv(4))
            if atyp == 1:  # IPv4
                addr = socket.inet_ntoa(client_sock.recv(4))
            elif atyp == 3:  # Domain
                domain_len = struct.unpack("!B", client_sock.recv(1))[0]
                addr = client_sock.recv(domain_len).decode()
            elif atyp == 4:  # IPv6
                addr = socket.inet_ntop(socket.AF_INET6, client_sock.recv(16))
            else:
                client_sock.close()
                return

            port = struct.unpack('!H', client_sock.recv(2))[0]

            if cmd != 1:
                client_sock.close()
                return

            try:
                resolved = socket.getaddrinfo(addr, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
            except socket.gaierror:
                client_sock.close()
                return

            remote = None
            for family, _, _, _, sockaddr in resolved:
                try:
                    remote = socket.socket(family, socket.SOCK_STREAM)
                    remote.connect(sockaddr)
                    break
                except:
                    if remote:
                        remote.close()
                    continue

            if not remote:
                client_sock.close()
                return

            bind_addr = remote.getsockname()
            if family == socket.AF_INET:
                rep = struct.pack("!BBBB", 5, 0, 0, 1)
                rep += socket.inet_aton(bind_addr[0]) + struct.pack("!H", bind_addr[1])
            else:
                rep = struct.pack("!BBBB", 5, 0, 0, 4)
                rep += socket.inet_pton(socket.AF_INET6, bind_addr[0]) + struct.pack("!H", bind_addr[1])

            client_sock.sendall(rep)
            self.relay(client_sock, remote)

        except Exception as e:
            print(f"[!] Error: {e}")
            client_sock.close()

    def relay(self, client, remote):
        sockets = [client, remote]
        while True:
            r, _, _ = select.select(sockets, [], [])
            for s in r:
                try:
                    data = s.recv(BUFFER_SIZE)
                    if not data:
                        client.close()
                        remote.close()
                        return
                    if s is client:
                        remote.sendall(data)
                    else:
                        client.sendall(data)
                except:
                    client.close()
                    remote.close()
                    return

def run_socks5_proxy(host='::', port=1080):
    server = Socks5Server(host, port)
    threading.Thread(target=server.start, daemon=True).start()
