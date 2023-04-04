import json

import requests
from flask import Flask, render_template

app = Flask(__name__)

servers = [
    "10.0.0.1:8009",
    "10.0.0.1:8008",
    "10.0.0.1:8007",
    "10.0.0.2:8006",
    "10.0.0.2:8005",
]


@app.route('/')
def index():
    data = []
    for server in servers:
        url = 'http://' + server + '/status'
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data.append(json.loads(response.text))
        except:
            print()
    print(data)
    return render_template('server_status.html', data=data)


if __name__ == '__main__':
    app.run()
