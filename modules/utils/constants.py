"""Constantes compartidas del sistema."""

# Stopwords en español para análisis de texto.
# Sin acentos para match normalizado con texto procesado.
SPANISH_STOPWORDS = [
    "el",
    "la",
    "de",
    "en",
    "un",
    "una",
    "que",
    "es",
    "por",
    "con",
    "para",
    "del",
    "los",
    "las",
    "al",
    "se",
    "no",
    "su",
    "sus",
    "muy",
    "mas",
    "ya",
    "esta",
    "este",
    "estos",
    "estas",
    "estan",
    "eso",
    "esa",
    "esos",
    "esas",
    "fue",
    "fueron",
    "son",
    "ser",
    "sido",
    "tiene",
    "tienen",
    "hay",
    "han",
    "hemos",
    "puede",
    "pueden",
    "como",
    "pero",
    "sin",
    "sobre",
    "tambien",
    "entre",
    "cuando",
    "donde",
    "todo",
    "toda",
    "todos",
    "todas",
    "desde",
    "hasta",
    "hacia",
    "otro",
    "otra",
    "otros",
    "otras",
    "porque",
    "era",
    "eran",
    "habia",
    "habian",
    "mismo",
    "misma",
    "mismos",
    "mismas",
    "asi",
    "algo",
    "solo",
    "poco",
    "mucho",
    "muchos",
    "muchas",
    "cada",
    "vez",
    "bien",
    "mal",
    "aqui",
    "ahi",
    "alli",
    "ahora",
    "antes",
    "despues",
    "hoy",
    "ayer",
    "siempre",
    "nunca",
    "nada",
    "nadie",
    "ninguno",
    "ninguna",
    "nos",
    "les",
    "le",
    "me",
    "te",
    "lo",
    "esto",
    "unos",
    "unas",
]

# Set para búsquedas O(1)
SPANISH_STOPWORDS_SET = set(SPANISH_STOPWORDS)

# CSS para reportes PDF/HTML
PDF_CSS = """
    @page {
        size: A4;
        margin: 2cm;
    }
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    body {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 12pt;
        line-height: 1.4;
        color: #333;
    }
    .report-header {
        text-align: center;
        margin-bottom: 30px;
        padding-bottom: 20px;
        border-bottom: 2px solid #2c3e50;
    }
    .report-header h1 {
        color: #2c3e50;
        font-size: 24pt;
        margin-bottom: 10px;
    }
    .report-header .subtitle {
        color: #7f8c8d;
        font-size: 14pt;
    }
    .report-header .date {
        color: #95a5a6;
        font-size: 10pt;
        margin-top: 10px;
    }
    .section {
        margin-bottom: 25px;
    }
    .section h2 {
        color: #2c3e50;
        font-size: 16pt;
        margin-bottom: 15px;
        padding-bottom: 5px;
        border-bottom: 1px solid #bdc3c7;
    }
    .stats-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .stats-table th {
        background-color: #2c3e50;
        color: white;
        padding: 12px;
        text-align: center;
        font-size: 11pt;
        font-weight: bold;
    }
    .stats-table td {
        text-align: center;
        padding: 15px;
        border: 1px solid #ddd;
        background-color: #f8f9fa;
    }
    .stats-table .value {
        font-size: 24pt;
        font-weight: bold;
        display: block;
        margin-bottom: 5px;
    }
    .stats-table .label {
        font-size: 9pt;
        color: #7f8c8d;
        text-transform: uppercase;
    }
    .stats-table .value.pending { color: #f39c12; }
    .stats-table .value.in-progress { color: #3498db; }
    .stats-table .value.resolved { color: #27ae60; }
    .stats-table .value.invalid { color: #e74c3c; }
    .stats-table .value.total { color: #2c3e50; }
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    th, td {
        border: 1px solid #ddd;
        padding: 10px 8px;
        text-align: left;
        font-size: 10pt;
    }
    th {
        background-color: #2c3e50;
        color: white;
        font-weight: bold;
    }
    tr:nth-child(even) {
        background-color: #f8f9fa;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 3px;
        font-size: 9pt;
        font-weight: bold;
    }
    .status-pending { background-color: #fff3cd; color: #856404; }
    .status-in-progress { background-color: #d1ecf1; color: #0c5460; }
    .status-resolved { background-color: #d4edda; color: #155724; }
    .status-invalid { background-color: #f8d7da; color: #721c24; }
    .footer {
        margin-top: 30px;
        padding-top: 15px;
        border-top: 1px solid #bdc3c7;
        text-align: center;
        font-size: 9pt;
        color: #95a5a6;
    }
    .no-print {
        display: none;
    }
"""
