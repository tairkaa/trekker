import csv
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
from datetime import datetime

DATA_FILE = 'tasks.csv'

def load_tasks():
    tasks = []
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["id", "date", "name", "status"])
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

def save_tasks(tasks):
    with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ["id", "date", "name", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(tasks)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            with open('index.html', 'rb') as f:
                self.wfile.write(f.read())

        elif self.path == '/api/tasks':
            tasks = load_tasks()
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps(tasks, ensure_ascii=False).encode('utf-8'))

        else:
            self.send_error(404, "Not found")

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        try:
            data = json.loads(post_data.decode('utf-8'))
        except:
            data = {}

        if self.path == '/api/add':
            tasks = load_tasks()

            new_id = 1
            if tasks:
                new_id = max(int(t["id"]) for t in tasks) + 1

            current_dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')

            new_task = {
                "id": str(new_id),
                "date": current_dt_str,
                "name": data.get("name", ""),
                "status": data.get("status", "pool")
            }
            tasks.append(new_task)
            save_tasks(tasks)

            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Task added!"}, ensure_ascii=False).encode('utf-8'))

        elif self.path == '/api/update':
            task_id = data.get("id")
            new_status = data.get("status")

            tasks = load_tasks()
            for t in tasks:
                if t["id"] == task_id:
                    t["status"] = new_status
                    break
            save_tasks(tasks)

            self.send_response(200)
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"message": "Status updated!"}, ensure_ascii=False).encode('utf-8'))

        else:
            self.send_error(404, "Not found")


def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server run on http://127.0.0.1:8000")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
