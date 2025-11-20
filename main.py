import mimetypes
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("."))


DATA_FILE = "storage/data.json"


class HttpHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            data = self.rfile.read(int(self.headers["Content-Length"]))
            print(data)
            data_parse = urllib.parse.unquote_plus(data.decode())
            print(data_parse)
            data_dict = {
                key: value
                for key, value in [el.split("=") for el in data_parse.split("&")]
            }
            print(data_dict)
            username = data_dict.get("username", "")
            message = data_dict.get("message", "")

            self.save_message(username, message)
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
        else:
            self.send_html_file("error.html", 404)

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == "/":
            self.send_html_file("index.html")
        elif pr_url.path == "/message":
            self.send_html_file("message.html")
        elif pr_url.path == "/read":
            messages = self.read_message()

            messages_list = [
                {"time": k, "username": v["username"], "message": v["message"]}
                for k, v in messages.items()
            ]

            template = env.get_template("read.html")
            html = template.render(messages=messages_list)

            self.send_html(html)
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file("error.html", 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        with open(filename, "rb") as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", "text/plain")
        self.end_headers()
        with open(f".{self.path}", "rb") as file:
            self.wfile.write(file.read())

    def send_html(self, html, status=200):
        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html)

    def read_message(self):
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def save_message(self, username, message):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

        timestamp = str(datetime.now())

        data[timestamp] = {"username": username, "message": message}

        with open(DATA_FILE, "w") as f:
            json.dump(data, f)


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ("", 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()
