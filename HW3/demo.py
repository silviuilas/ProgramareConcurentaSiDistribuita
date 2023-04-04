import subprocess
import time

servers = [
    "10.0.0.1:9999",
    "10.0.0.1:9998",
    "10.0.0.1:9997",
    "10.0.0.2:9996",
    "10.0.0.2:9995",
]
if __name__ == '__main__':

    commands = []

    for i in range(len(servers)):
        command = f"python kvserver.py 800{9-i} dump.bin "
        for j in range(len(servers)):
            command += servers[(i+j)%len(servers)] + " "
        commands.append(command)

    processes = []

    for command in commands:
        print(f"Starting process for command: {command}")
        process = subprocess.Popen(command.split())
        processes.append(process)
        time.sleep(0.5)

    while True:
        print("Enter a command (start/stop/restart/exit):")
        command = input()
        servers = command.split()[1:]
        if command.startswith("start "):
            for server in servers:
                for process in processes:
                    if process.poll() is not None and server in process.args:
                        print(f"Starting process for server {server}...")
                        process = subprocess.Popen(process.args)
                        processes.append(process)
                        time.sleep(0.5)
                print(f"Server {server} is running.")

        elif command.startswith("stop "):
            for server in servers:
                for process in processes:
                    if process.poll() is None and server in process.args[2]:
                        print(f"Stopping process for server {server}...")
                        process.kill()
                print(f"Server {server} is stopped.")
        elif command.startswith("restart"):
            to_open_args = []
            for process in processes:
                if process.poll() is None:
                    print("Restarting process...")
                    process.kill()
                    time.sleep(0.5)
                    to_open_args.append(process.args)
            for args in to_open_args:
                process = subprocess.Popen(args)
                processes.append(process)
            print("All processes are restarted.")

        elif command == "exit":
            for process in processes:
                if process.poll() is None:
                    print("Stopping process...")
                    process.kill()
            print("Exiting...")
            break

        else:
            print("Invalid command.")