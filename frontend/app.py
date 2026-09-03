import streamlit as st
import requests

# Reemplaza esta dirección por la URL pública real que te dio Render
BACKEND_URL = "https://generador-contenido-saas.onrender.com"

st.set_page_config(page_title="Generador SaaS", page_icon="⚡")
st.title("⚡ Generador de Contenido IA")

# Menú lateral para capturar el email del usuario
st.sidebar.header("Acceso de Usuario")
email = st.sidebar.text_input("Ingresa tu correo:", placeholder="ejemplo@correo.com")

if not email:
    st.warning("👈 Por favor, ingresa tu correo electrónico en la barra lateral para continuar.")
else:
    st.sidebar.success("Usuario activo")
    
    prompt = st.text_area("¿Qué contenido deseas crear hoy?", placeholder="Ej: Escribe un post para LinkedIn sobre productividad...")
    
    if st.button("Generar Contenido", type="primary"):
        if not prompt.strip():
            st.error("Por favor, escribe una instrucción antes de hacer clic en Generar.")
        else:
            with st.spinner("Procesando con la IA..."):
                try:
                    # Se envía email y prompt al servidor en Render
                    response = requests.post(
                        f"{BACKEND_URL}/generate",
                        json={"email": email, "prompt": prompt}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.success("¡Contenido generado!")
                        st.markdown(data["result"])
                        st.sidebar.info(f"🎁 Créditos restantes: {data['credits_left']}")
                    else:
                        error_detail = response.json().get("detail", "Error en la solicitud.")
                        st.error(f"❌ {error_detail}")
                except Exception as e:
                    st.error(f"Error de conexión con el backend: {e}")
