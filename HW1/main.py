import csv
import threading
import time
from queue import Queue

from HW1.client import send_data
from HW1.server import receive_data


def generate_message_sizes():
    arr = []
    start = 1
    while start <= 65535:
        arr.append(int(start))
        start = start * 1.1
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
    buffer_sizes = generate_message_sizes()
    mechanisms = ['streaming', 'stop-and-wait']

    data = [["Protocol", "Buffer Size", "Mechanism Used", "Transmission Time", "Number of Sent Bytes",
             "Number of Received Bytes"]]
    i = 0
    for message_size in buffer_sizes:
        for protocol in protocols:
            for mechanism in mechanisms:
                start_time = time.monotonic()
                q1 = Queue()
                q2 = Queue()
                t1 = threading.Thread(target=send_data, args=(q1, protocol, message_size, mechanism))
                t2 = threading.Thread(target=receive_data, args=(q2, protocol, message_size, mechanism))
                t1.start()
                t2.start()
                t1.join()
                t2.join()
                end_time = time.monotonic()
                transmission_time = end_time - start_time
                bytes_sent = q1.get()
                bytes_received = q2.get()

                print('Protocol Used:', protocol)
                print('Buffer Size: ', message_size)
                print('Mechanism Used:', mechanism)
                print('Transmission Time:', transmission_time)
                print('Number of Sent Bytes:', bytes_sent)
                print('Number of Received Bytes:', bytes_received)
                print()
                data.append([protocol, message_size, mechanism, transmission_time, bytes_sent, bytes_received])
        i += 1
        if i % 100 == 0:
            save_test_results(data)

    print(">>>>>Finished<<<<<<")
    save_test_results(data)


if __name__ == '__main__':
    run_tests()
