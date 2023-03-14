import socket
import time


def send_data(q, protocol, buffer_size, mechanism):
    host = '192.168.1.53'
    port = 12347
    message_size = 10000
    message = b'0' * message_size
    packages_sent = 0
    time.sleep(0.05)
    if protocol == 'UDP':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    try:
        s.connect((host, port))
        num_packets = ((message_size - 1) // buffer_size) + 1
        for i in range(num_packets):
            start = i * buffer_size
            end = min((i + 1) * buffer_size, message_size)
            s.send(message[start:end])
            packages_sent += 1
            if mechanism == 'stop-and-wait':
                s.recv(buffer_size)
    except Exception as e:
        print(e)
    finally:
        s.close()
        q.put(message_size)
