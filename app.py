import streamlit as st
from pathlib import Path
from datetime import datetime, date
import pandas as pd
from auth import verify_login, add_user, list_users
from data_manager import (
    NIVELES, DIAS, get_tests, get_upcoming_tests,
    get_materials, add_test, delete_test,
    add_material, delete_material,
    save_file, get_asignaturas, init_dirs,
    get_schedule, save_schedule
)

# Configuración de la página
st.set_page_config(
    page_title="Portal Quinto Básico Pascuala",
    page_icon="🏫",
    layout="wide"
)

# Estado de sesión
if "user" not in st.session_state:
    st.session_state.user = None


def show_login():
    st.title("🏫 Portal Escolar")
    st.subheader("Inicia sesión para continuar")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        user = verify_login(username, password)
        if user:
            st.session_state.user = user
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")


def show_header():
    user = st.session_state.user
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🏫 Portal Escolar")
    with col2:
        st.write(f"👤 {user['name']}")
        if st.button("Cerrar sesión"):
            st.session_state.user = None
            st.rerun()


def show_dashboard():
    upcoming = get_upcoming_tests(30)
    materials = get_materials()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📋 Pruebas próximas", len(upcoming))
    with col2:
        st.metric("📁 Materiales", len(materials))
    with col3:
        st.metric("👨‍👩‍👧 Niveles", len(NIVELES))
    st.divider()
    st.subheader("🔔 Próximas pruebas")
    if not upcoming:
        st.info("No hay pruebas en los próximos 30 días")
    else:
        for t in upcoming:
            nivel_info = NIVELES[t["nivel"]]
            days = t["days_remaining"]
            if days == 0:
                label = "🔴 HOY"
            elif days == 1:
                label = "🟠 Mañana"
            elif days <= 7:
                label = f"🟡 En {days} días"
            else:
                label = f"🟢 En {days} días"
            st.write(f"{nivel_info['emoji']} **{t['asignatura']}** — {t['tipo']} · {label}")


def show_nivel(nivel):
    nivel_info = NIVELES[nivel]
    st.header(f"{nivel_info['emoji']} {nivel_info['label']}")
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Pruebas", "📁 Materiales", "🕐 Horario", "➕ Agregar"])
    with tab1:
        show_tests(nivel)
    with tab2:
        show_materials(nivel)
    with tab3:
        show_schedule(nivel)
    with tab4:
        user = st.session_state.user
        if user["role"] in ["admin", "editor"]:
            show_add_content(nivel)
        else:
            st.info("🔒 Solo administradores pueden agregar contenido")


def show_tests(nivel):
    tests = get_tests(nivel)
    today = date.today()
    if not tests:
        st.info("No hay pruebas registradas aún")
        return
    for t in tests:
        test_date = datetime.strptime(t["fecha"], "%Y-%m-%d").date()
        days = (test_date - today).days
        fecha_fmt = test_date.strftime("%d/%m/%Y")
        if days < 0:
            emoji = "✅"
        elif days == 0:
            emoji = "🔴"
        elif days <= 7:
            emoji = "🟡"
        else:
            emoji = "🟢"
        with st.expander(f"{emoji} {t['tipo']}: {t['asignatura']} — {fecha_fmt}"):
            st.write(f"📅 Fecha: {fecha_fmt}")
            st.write(f"📚 Asignatura: {t['asignatura']}")
            if t.get("descripcion"):
                st.write(f"💬 {t['descripcion']}")
            user = st.session_state.user
            if user["role"] in ["admin", "editor"]:
                if st.button("🗑️ Eliminar", key=f"del_{t['id']}"):
                    delete_test(t["id"])
                    st.rerun()


def show_materials(nivel):
    materials = get_materials(nivel)
    if not materials:
        st.info("No hay materiales subidos aún")
        return
    for m in materials:
        fp = Path(m["filepath"])
        col1, col2, col3 = st.columns([5, 1, 1])
        with col1:
            st.write(f"📄 **{m['titulo']}** — {m['asignatura']}")
            if m.get("descripcion"):
                st.caption(m["descripcion"])
        with col2:
            if fp.exists():
                with open(fp, "rb") as f:
                    st.download_button(
                        "⬇️",
                        data=f.read(),
                        file_name=m["filename"],
                        key=f"dl_{m['id']}"
                    )
        with col3:
            user = st.session_state.user
            if user["role"] in ["admin", "editor"]:
                if st.button("🗑️", key=f"delm_{m['id']}"):
                    delete_material(m["id"])
                    st.rerun()


def show_add_content(nivel):
    asignaturas = get_asignaturas(nivel)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📅 Agregar Prueba")
        asig = st.selectbox("Asignatura", asignaturas, key=f"asig_{nivel}")
        tipo = st.selectbox("Tipo", ["Prueba", "Control", "Tarea", "Disertación"], key=f"tipo_{nivel}")
        fecha = st.date_input("Fecha", key=f"fecha_{nivel}")
        desc = st.text_area("Descripción", key=f"desc_{nivel}")
        if st.button("✅ Agregar", key=f"add_test_{nivel}"):
            add_test(nivel, asig, fecha.strftime("%Y-%m-%d"), desc, tipo)
            st.success("Prueba agregada!")
            st.rerun()
    with col2:
        st.subheader("📁 Subir Material")
        asig_m = st.selectbox("Asignatura", asignaturas, key=f"asigm_{nivel}")
        titulo = st.text_input("Título", key=f"tit_{nivel}")
        desc_m = st.text_input("Descripción", key=f"descm_{nivel}")
        archivo = st.file_uploader("Archivo", key=f"file_{nivel}")
        if st.button("📤 Subir", key=f"upload_{nivel}"):
            if titulo and archivo:
                filepath = save_file(nivel, archivo, archivo.name)
                add_material(nivel, asig_m, titulo, archivo.name, filepath, desc_m)
                st.success("Material subido!")
                st.rerun()
            else:
                st.error("Título y archivo son obligatorios")


def show_schedule(nivel):
    asignaturas = get_asignaturas(nivel)
    schedule = get_schedule(nivel)
    user = st.session_state.user

    horas = ["08:00", "08:45", "09:45", "10:30", "11:30", "12:15", "13:00", "14:30", "15:15"]

    if user["role"] in ["admin", "editor"]:
        st.subheader("✏️ Editar Horario")
        nuevo_horario = {}
        for dia in DIAS:
            st.markdown(f"**{dia}**")
            nuevo_horario[dia] = {}
            cols = st.columns(len(horas))
            for i, hora in enumerate(horas):
                with cols[i]:
                    actual = schedule.get(dia, {}).get(hora, "")
                    nuevo_horario[dia][hora] = st.selectbox(
                        hora,
                        [""] + asignaturas,
                        index=([""] + asignaturas).index(actual) if actual in asignaturas else 0,
                        key=f"sch_{nivel}_{dia}_{hora}"
                    )
        if st.button("💾 Guardar horario", key=f"save_sch_{nivel}"):
            save_schedule(nivel, nuevo_horario)
            st.success("Horario guardado!")
            st.rerun()
        st.divider()

    st.subheader("📅 Horario de clases")
    if not schedule:
        st.info("No hay horario cargado aún")
        return

    tabla = {}
    for dia in DIAS:
        tabla[dia] = [schedule.get(dia, {}).get(hora, "—") for hora in horas]

    df = pd.DataFrame(tabla, index=horas)
    st.dataframe(df, use_container_width=True)


def main():
    if not st.session_state.user:
        show_login()
        return
    show_header()
    st.divider()
    nav = st.radio(
        "",
        ["🏠 Inicio", "📚 5° Básico", "🌟 Kinder"],
        horizontal=True
    )
    st.divider()
    if nav == "🏠 Inicio":
        show_dashboard()
    elif nav == "📚 5° Básico":
        show_nivel("5to_basico")
    elif nav == "🌟 Kinder":
        show_nivel("kinder")


if __name__ == "__main__":
    main()