import socket


def receive_data(q, protocol, buffer_size, mechanism):
    host = '192.168.1.53'
    port = 12347
    message_size = 10000
    print(" >>>> Starting server")
    if protocol == 'UDP':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)

    packages_received = 0

    data = b''
    try:
        if protocol == 'UDP':
            s.bind((host, port))
            while len(data) < message_size:
                packet, addr = s.recvfrom(buffer_size)
                packages_received += 1
                data += packet
                if mechanism == 'stop-and-wait':
                    s.sendto(b'ack', addr)
        else:
            s.bind((host, port))
            s.listen(1)
            conn, addr = s.accept()
            while True:
                packet = conn.recv(buffer_size)
                if not packet:
                    break
                packages_received += 1
                data += packet
                if mechanism == 'stop-and-wait':
                    conn.sendall(b'ack')
            conn.close()
    except Exception as e:
        print(e)
    finally:
        s.close()
        q.put(len(data))
