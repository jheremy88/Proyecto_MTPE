import os
import unicodedata

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def normalizar_texto(texto):
    if not texto:
        return ""
    texto_str = str(texto).strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFD', texto_str) if unicodedata.category(c) != 'Mn')

class ConexionDB:
    @staticmethod
    def obtener_ruta(nombre_csv):
        return os.path.join(BASE_DIR, nombre_csv)