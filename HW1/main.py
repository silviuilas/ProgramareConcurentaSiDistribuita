import csv
import socket
import threading
import time
from queue import Queue


def send_data(q, protocol, message_size, mechanism):
    host = 'localhost'
    port = 12345
    buffer_size = 1024
    message = b'0' * message_size

    time.sleep(0.05)
    if protocol == 'UDP':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((host, port))

    start_time = time.monotonic()

    if mechanism == 'streaming':
        num_packets = ((message_size - 1) // buffer_size) + 1
        for i in range(num_packets):
            start = i * buffer_size
            end = min((i + 1) * buffer_size, message_size)
            s.send(message[start:end])
    elif mechanism == 'stop-and-wait':
        num_packets = ((message_size - 1) // buffer_size) + 1
        for i in range(num_packets):
            start = i * buffer_size
            end = min((i + 1) * buffer_size, message_size)
            s.send(message[start:end])
            s.recv(buffer_size)

    end_time = time.monotonic()
    transmission_time = end_time - start_time

    s.close()

    q.put((transmission_time, message_size))


def receive_data(q, protocol, message_size, mechanism):
    host = 'localhost'
    port = 12345
    buffer_size = 1024

    if protocol == 'UDP':
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    data = b''
    if protocol == 'UDP':
        s.bind((host, port))
        if mechanism == 'streaming':
            while len(data) < message_size:
                packet, addr = s.recvfrom(buffer_size)
                data += packet
        elif mechanism == 'stop-and-wait':
            while len(data) < message_size:
                packet, addr = s.recvfrom(buffer_size)
                s.sendto(b'ack', addr)
                data += packet
    else:
        s.bind((host, port))
        s.listen(1)
        conn, addr = s.accept()
        while True:
            packet = conn.recv(buffer_size)
            if not packet:
                break
            data += packet
            if mechanism == 'stop-and-wait':
                conn.sendall(b'ack')
        conn.close()
    s.close()
    q.put(len(data))


def generate_message_sizes():
    arr = []
    start = 1
    step = 1000
    while start <= 65535 * 128:
        arr.append(start)
        start += step
    return arr

def save_test_results(data):
    # name of csv file
    filename = "test_results.csv"

    # writing to csv file
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        # writing the data rows
        for row in data:
            csvwriter.writerow(row)

    print(f"File '{filename}' created successfully!")

def run_tests():
    protocols = ['UDP', 'TCP']
    message_sizes = generate_message_sizes()
    mechanisms = ['streaming', 'stop-and-wait']

    data = [["Protocol", "Message Size", "Mechanism Used", "Transmission Time", "Number of Sent Bytes",
             "Number of Received Bytes"]]
    i = 0
    for message_size in message_sizes:
        for protocol in protocols:
            for mechanism in mechanisms:
                q1 = Queue()
                q2 = Queue()
                t1 = threading.Thread(target=send_data, args=(q1, protocol, message_size, mechanism))
                t2 = threading.Thread(target=receive_data, args=(q2, protocol, message_size, mechanism))
                t1.start()
                t2.start()
                t1.join()
                t2.join()

                transmission_time, bytes_sent = q1.get()
                bytes_received = q2.get()

                print('Protocol Used:', protocol)
                print('Message Size:', message_size)
                print('Mechanism Used:', mechanism)
                print('Transmission Time:', transmission_time)
                print('Number of Sent Bytes:', bytes_sent)
                print('Number of Received Bytes:', bytes_received)
                print()
                data.append([protocol, message_size, mechanism, transmission_time, bytes_sent, bytes_received])
        i+=1
        if i % 100 == 0:
            save_test_results(data)

    print(">>>>>Finished<<<<<<")
    save_test_results(data)


if __name__ == '__main__':
    run_tests()
