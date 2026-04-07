import json
from pathlib import Path
from datetime import datetime, date

# Carpetas y archivos
DATA_DIR = Path("data")
UPLOADS_DIR = Path("uploads")
TESTS_FILE = DATA_DIR / "tests.json"
MATERIALS_FILE = DATA_DIR / "materials.json"

# Niveles del portal
NIVELES = {
    "5to_basico": {"label": "5° Básico", "emoji": "📚", "color": "#6C63FF"},
    "kinder":     {"label": "Kinder",    "emoji": "🌟", "color": "#FF6B9D"},
}

# Crear carpetas si no existen
def init_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    for nivel in NIVELES:
        (UPLOADS_DIR / nivel).mkdir(parents=True, exist_ok=True)
    if not TESTS_FILE.exists():
        TESTS_FILE.write_text("[]")
    if not MATERIALS_FILE.exists():
        MATERIALS_FILE.write_text("[]")
def init_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    for nivel in NIVELES:
        (UPLOADS_DIR / nivel).mkdir(parents=True, exist_ok=True)
    if not TESTS_FILE.exists():
        TESTS_FILE.write_text("[]")
    if not MATERIALS_FILE.exists():
        MATERIALS_FILE.write_text("[]")
    if not SCHEDULE_FILE.exists():
        load_default_schedule()

# ── PRUEBAS ──────────────────────────────────────────
def get_tests(nivel=None):
    tests = json.loads(TESTS_FILE.read_text())
    if nivel:
        tests = [t for t in tests if t["nivel"] == nivel]
    return sorted(tests, key=lambda x: x["fecha"])

def add_test(nivel, asignatura, fecha, descripcion="", tipo="Prueba"):
    tests = json.loads(TESTS_FILE.read_text())
    tests.append({
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "nivel": nivel,
        "asignatura": asignatura,
        "fecha": fecha,
        "descripcion": descripcion,
        "tipo": tipo
    })
    TESTS_FILE.write_text(json.dumps(tests, indent=2))

def delete_test(test_id):
    tests = json.loads(TESTS_FILE.read_text())
    tests = [t for t in tests if t["id"] != test_id]
    TESTS_FILE.write_text(json.dumps(tests, indent=2))

def get_upcoming_tests(days=30):
    today = date.today()
    result = []
    for t in get_tests():
        test_date = datetime.strptime(t["fecha"], "%Y-%m-%d").date()
        delta = (test_date - today).days
        if 0 <= delta <= days:
            t["days_remaining"] = delta
            result.append(t)
    return sorted(result, key=lambda x: x["fecha"])

# ── MATERIALES ───────────────────────────────────────
def get_materials(nivel=None):
    materials = json.loads(MATERIALS_FILE.read_text())
    if nivel:
        materials = [m for m in materials if m["nivel"] == nivel]
    return sorted(materials, key=lambda x: x["uploaded"], reverse=True)

def add_material(nivel, asignatura, titulo, filename, filepath, descripcion=""):
    materials = json.loads(MATERIALS_FILE.read_text())
    materials.append({
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "nivel": nivel,
        "asignatura": asignatura,
        "titulo": titulo,
        "filename": filename,
        "filepath": filepath,
        "descripcion": descripcion,
        "uploaded": datetime.now().isoformat()
    })
    MATERIALS_FILE.write_text(json.dumps(materials, indent=2))

def delete_material(material_id):
    materials = json.loads(MATERIALS_FILE.read_text())
    materials = [m for m in materials if m["id"] != material_id]
    MATERIALS_FILE.write_text(json.dumps(materials, indent=2))

def save_file(nivel, file_obj, filename):
    path = UPLOADS_DIR / nivel / filename
    path.write_bytes(file_obj.getbuffer())
    return str(path)

def get_asignaturas(nivel):
    return {
        "5to_basico": ["Matemáticas","Lenguaje","Ciencias","Historia","Inglés","Arte","Ed. Física","Otro"],
        "kinder":     ["Matemáticas","Lenguaje","Ciencias","Arte","Ed. Física","Otro"]
    }.get(nivel, ["Otro"])

init_dirs()

SCHEDULE_FILE = DATA_DIR / "schedule.json"

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

def get_schedule(nivel):
    if not SCHEDULE_FILE.exists():
        return {}
    data = json.loads(SCHEDULE_FILE.read_text())
    return data.get(nivel, {})

def save_schedule(nivel, schedule):
    data = {}
    if SCHEDULE_FILE.exists():
        data = json.loads(SCHEDULE_FILE.read_text())
    data[nivel] = schedule
    SCHEDULE_FILE.write_text(json.dumps(data, indent=2))

def load_default_schedule():
    schedule = {
        "5to_basico": {
            "Lunes": {
                "08:00": "Tecnología",
                "08:45": "Religión",
                "09:45": "Idioma Extranjero Inglés",
                "10:30": "Idioma Extranjero Inglés",
                "11:30": "Lenguaje y Comunicación",
                "12:15": "Lenguaje y Comunicación",
                "13:00": "Idioma Extranjero Inglés",
                "14:30": "Música"
            },
            "Martes": {
                "08:00": "Idioma Extranjero Inglés",
                "08:45": "Idioma Extranjero Inglés",
                "09:45": "Historia Geografía y Ciencias Sociales",
                "10:30": "Historia Geografía y Ciencias Sociales",
                "11:30": "Matemática",
                "12:15": "Matemática",
                "13:00": "Lenguaje y Comunicación",
                "14:30": "Lenguaje y Comunicación"
            },
            "Miércoles": {
                "08:00": "Ciencias Naturales",
                "08:45": "Ciencias Naturales",
                "09:45": "Historia Geografía y Ciencias Sociales",
                "10:30": "Historia Geografía y Ciencias Sociales",
                "11:30": "Matemática",
                "12:15": "Matemática",
                "13:00": "Ciencias Naturales",
                "14:30": "Lenguaje y Comunicación",
                "15:15": "Lenguaje y Comunicación"
            },
            "Jueves": {
                "08:00": "Educación Física y Salud",
                "08:45": "Educación Física y Salud",
                "09:45": "Idioma Extranjero Inglés",
                "10:30": "Idioma Extranjero Inglés",
                "11:30": "Artes Visuales",
                "12:15": "Artes Visuales",
                "13:00": "Matemática",
                "14:30": "Matemática"
            },
            "Viernes": {
                "08:00": "Educación Física y Salud",
                "08:45": "Educación Física y Salud",
                "09:45": "Ciencias Naturales",
                "10:30": "Ciencias Naturales",
                "11:30": "Matemática",
                "12:15": "Música",
                "13:00": "Orientación Básica",
                "14:30": ""
            }
        }
    }
    save_schedule("5to_basico", schedule["5to_basico"])
    print("✅ Horario de 5° Básico cargado!")