import http.server
import socketserver

PORT = 8000

def do_GET(self):
    self.send_response()
    self.send_header('Content-type','text/plain')
    self.send_header('Access-Control-Allow-Origin','*')
    self.end_headers()

Handler = http.server.SimpleHTTPRequestHandler
Handler.do_GET = do_GET()
httpd = socketserver.TCPServer(("127.0.0.1", PORT), Handler)

print("Serving at port", PORT)
httpd.serve_forever()