import http.server
import socketserver
import webbrowser
from threading import Timer
import json
import urllib.parse
import os
from control.siniestro_controller import SiniestroController

PORT = 5050
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def leer_template(nombre_archivo):
    ruta = os.path.join(BASE_DIR, "templates", nombre_archivo)
    with open(ruta, "r", encoding="utf-8") as f:
        return f.read()

class MTPEHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path in ["/", "/inicio", "/inicio.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(leer_template("inicio.html").encode("utf-8"))
            return

        elif parsed.path in ["/estadisticas", "/estadisticas.html"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(leer_template("estadisticas.html").encode("utf-8"))
            return

        elif parsed.path == "/api/siniestros":
            p = urllib.parse.parse_qs(parsed.query)
            data = SiniestroController.obtener_resumen(
                p.get('sector', ['todos'])[0], p.get('ubigeo', ['todos'])[0],
                p.get('gravedad', ['todas'])[0], p.get('fini', [None])[0],
                p.get('ffin', [None])[0], p.get('pagina', [1])[0], p.get('tamano', [10])[0]
            )
            self.responder_json(data)
            return

        elif parsed.path == "/api/dashboard_rf05":
            p = urllib.parse.parse_qs(parsed.query)
            data = SiniestroController.obtener_rf05(
                p.get('ano', ['todos'])[0], p.get('gravedad', ['todas'])[0],
                p.get('sector', ['todos'])[0], p.get('ubigeo', ['todos'])[0]
            )
            self.responder_json(data)
            return

        elif parsed.path.startswith("/api/exportar_csv"):
            p = urllib.parse.parse_qs(parsed.query)
            csv_data = SiniestroController.exportar_csv(
                p.get('sector', ['todos'])[0], p.get('ubigeo', ['todos'])[0],
                p.get('gravedad', ['todas'])[0], p.get('fini', [None])[0],
                p.get('ffin', [None])[0]
            )
            self.send_response(200)
            self.send_header("Content-type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="Siniestros_MTPE_Filtrados.csv"')
            self.end_headers()
            self.wfile.write(csv_data.encode("utf-8"))
            return

        super().do_GET()

    def do_POST(self):
        if self.path == "/api/siniestros/nuevo":
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            SiniestroController.nuevo_siniestro(body)
            self.responder_json({"status": "ok"}, 201)
            return

    def responder_json(self, data, cod=200):
        self.send_response(cod)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

def abrir_navegador():
    webbrowser.open_new(f"http://127.0.0.1:{PORT}/inicio")

if __name__ == "__main__":
    print(f"Monitor MTPE ejecutando en: http://127.0.0.1:{PORT}/inicio")
    Timer(1.0, abrir_navegador).start()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), MTPEHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor cerrado.")