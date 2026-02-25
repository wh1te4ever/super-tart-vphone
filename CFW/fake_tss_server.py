from http.server import BaseHTTPRequestHandler, HTTPServer

class SimpleHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            self.rfile.read(content_length)

        if self.path == '/TSS/controller?action=2':
            self.send_response(200)
            self.end_headers()
            
            try:
                with open('tss_response', 'rb') as f:
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.wfile.write(b"apticket file not found.")
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        self.do_POST()

if __name__ == '__main__':
    print("Server running on http://127.0.0.1:1337 ...")
    HTTPServer(('127.0.0.1', 1337), SimpleHandler).serve_forever()