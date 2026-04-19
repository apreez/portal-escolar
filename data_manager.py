import os
from datetime import datetime, date
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Conexión Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DIAS = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]

NIVELES = {
    "5to_basico": {"label": "5° Básico", "emoji": "📚", "color": "#6C63FF"},
    "kinder":     {"label": "Kinder",    "emoji": "🌟", "color": "#FF6B9D"},
}

# ── PRUEBAS ──────────────────────────────────────────
def get_tests(nivel=None):
    query = supabase.table("tests").select("*")
    if nivel:
        query = query.eq("nivel", nivel)
    result = query.order("fecha").execute()
    return result.data

def add_test(nivel, asignatura, fecha, descripcion="", tipo="Prueba"):
    supabase.table("tests").insert({
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "nivel": nivel,
        "asignatura": asignatura,
        "fecha": fecha,
        "descripcion": descripcion,
        "tipo": tipo
    }).execute()

def delete_test(test_id):
    supabase.table("tests").delete().eq("id", test_id).execute()

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
    query = supabase.table("materials").select("*")
    if nivel:
        query = query.eq("nivel", nivel)
    result = query.order("uploaded", desc=True).execute()
    return result.data

def add_material(nivel, asignatura, titulo, filename, filepath, descripcion=""):
    supabase.table("materials").insert({
        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
        "nivel": nivel,
        "asignatura": asignatura,
        "titulo": titulo,
        "filename": filename,
        "filepath": filepath,
        "descripcion": descripcion,
        "uploaded": datetime.now().isoformat()
    }).execute()

def delete_material(material_id):
    supabase.table("materials").delete().eq("id", material_id).execute()

def save_file(nivel, file_obj, filename):
    from pathlib import Path
    path = Path("uploads") / nivel / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(file_obj.getbuffer())
    return str(path)

def get_asignaturas(nivel):
    return {
        "5to_basico": ["Matemáticas","Lenguaje","Ciencias","Historia","Inglés","Arte","Ed. Física","Otro"],
        "kinder":     ["Matemáticas","Lenguaje","Ciencias","Arte","Ed. Física","Otro"]
    }.get(nivel, ["Otro"])

# ── HORARIO ──────────────────────────────────────────
def get_schedule(nivel):
    result = supabase.table("schedule").select("*").eq("nivel", nivel).execute()
    schedule = {}
    for row in result.data:
        dia = row["dia"]
        hora = row["hora"]
        if dia not in schedule:
            schedule[dia] = {}
        schedule[dia][hora] = row["asignatura"]
    return schedule

def save_schedule(nivel, schedule):
    supabase.table("schedule").delete().eq("nivel", nivel).execute()
    rows = []
    for dia, horas in schedule.items():
        for hora, asignatura in horas.items():
            if asignatura:
                rows.append({
                    "nivel": nivel,
                    "dia": dia,
                    "hora": hora,
                    "asignatura": asignatura
                })
    if rows:
        supabase.table("schedule").insert(rows).execute()

def load_default_schedule():
    schedule = {
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
    save_schedule("5to_basico", schedule)

# Cargar horario por defecto si no existe
existing = get_schedule("5to_basico")
if not existing:
    load_default_schedule()