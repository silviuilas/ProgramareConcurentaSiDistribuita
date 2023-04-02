import random
import requests
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

servers = [
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002'

]
counter = 0

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        print(query_params)
        if(len(query_params)!=0):
            self.proxy_requestGetSpecificScore(query_params['playerName'])
        else:
            self.proxy_requestGetAllScores()

    def proxy_requestGetSpecificScore(self,queryParams):
        global counter, servers
        for i in range(0,len(servers)):
            serverURL = servers[counter % len(servers)]
            counter += 1
            serverURL = serverURL + '/' + str(queryParams[0])
            try:
                response = requests.get(serverURL)
                if response.status_code == 200:
                    data = response.text
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(("Score: %s" %data).encode('utf-8'))
                    print(data)
                    break
                else:
                    continue
            except requests.exceptions.RequestException as e:
                continue

    def proxy_requestGetAllScores(self):
        global counter, servers
        for i in range(0,len(servers)):
            serverURL = servers[counter % len(servers)]
            counter += 1
            serverURL += '/'
            try:
                response = requests.get(serverURL)
                if response.status_code == 200:
                    data = json.dumps(response.json())
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(data.encode('utf-8'))
                    print(data)
                    break
                else:
                    continue
            except requests.exceptions.RequestException as e:
                continue
        
    def do_POST(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        print(query_params)
        self.proxy_requestPost(query_params)

    def proxy_requestPost(self, queryParams):
        global counter, servers
        serverURL = servers[counter % len(servers)]
        serverURL = serverURL + '/' + str(queryParams['playerName'][0])
        counter += 1
        print(serverURL)
        for i in range(0,len(servers)):
            headers = {'Content-Type': 'text/plain'}
            try:
                response = requests.post(serverURL, headers=headers, data=queryParams['score'][0])
                if response.status_code == 201:
                    data = response.text
                    self.send_response(201)
                    self.send_header("Content-type", "text/plain")
                    self.end_headers()
                    self.wfile.write(("Created").encode('utf-8'))
                    print(data)
                    break
                else:
                    continue
            except requests.exceptions.RequestException as e:
                continue

if __name__ == '__main__':
    random.shuffle(servers)  
    server = HTTPServer(('localhost', 8080), RequestHandler)
    print("Starting load balancer on http://%s:%d" % server.server_address)
    server.serve_forever()
