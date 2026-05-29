from datetime import datetime

def parsear_fecha(texto: str):
    """Acepta DD/MM/AAAA o YYYY-MM-DD. Valida año, mes y día estrictamente."""
    texto = texto.strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            d = datetime.strptime(texto, fmt).date()
            if d.year < 1990 or d.year > 2100:
                return None
            if d.month < 1 or d.month > 12:
                return None
            if d.day < 1 or d.day > 31:
                return None
            return d
        except ValueError:
            continue
    return None


EVENTOS_VALIDOS = ["Consulta", "Control", "Urgencia", "Cirugía", "Vacunación"]
