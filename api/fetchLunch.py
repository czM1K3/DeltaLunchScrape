from http.server import BaseHTTPRequestHandler
import xml.etree.ElementTree as ET
import json
import socket
from io import BytesIO

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect(('www.strava.cz', 80))
        conn.send(b'GET /foxisapi/foxisapi.dll/istravne.istravne.process?xmljidelnickyA&zarizeni=0304\r\n')
        buffer = BytesIO()
        while True:
            chunk = conn.recv(4096)
            if chunk:
                buffer.write(chunk)
            else:
                break
        data = buffer.getvalue()

        array = []

        root = ET.fromstring(data)
        for child in root:
            if child.tag != 'pomjidelnic_xmljidelnic':
                continue
            day = next((x for x in array if x["year"] == child[0].text), None)
            if day is None:
                array.append({
                    'year': child[0].text,
                    'soup': None,
                    'lunch1': None,
                    'lunch2': None,
                    'lunch3': None,
                    'extra': None
                })
                day = array[-1]
            if child[1].text == "0":
                day["soup"] = child[3].text
            elif child[1].text == "1":
                day["lunch1"] = child[3].text
            elif child[1].text == "2":
                day["lunch2"] = child[3].text
            elif child[1].text == "3":
                day["lunch3"] = child[3].text
            elif child[1].text == "D":
                day["extra"] = child[3].text

        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps(array).encode())
        return