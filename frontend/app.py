import streamlit as st
import requests

BACKEND_URL = "https://generador-contenido-saas.onrender.com"

st.set_page_config(page_title="Generador SaaS", page_icon="⚡")
st.title("⚡ Generador de Contenido IA")

st.sidebar.header("Acceso de Usuario")
email = st.sidebar.text_input("Ingresa tu correo:", placeholder="ejemplo@correo.com")

if not email:
    st.warning("👈 Por favor, ingresa tu correo electrónico en la barra lateral para continuar.")
else:
    st.sidebar.success("Usuario activo")
    
    prompt = st.text_area("¿Qué contenido deseas crear hoy?", placeholder="Ej: Escribe un post para LinkedIn...")
    
    if st.button("Generar Contenido", type="primary"):
        if not prompt.strip():
            st.error("Por favor, escribe una instrucción antes de hacer clic en Generar.")
        else:
            with st.spinner("Procesando con la IA..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/generar",
                        json={"email": email, "prompt": prompt}
                    )
                    
                    # Intentar leer JSON, si falla captura el texto crudo del error
                    try:
                        data = response.json()
                    except Exception:
                        data = None

                    if response.status_code == 200 and data:
                        st.success("¡Contenido generado!")
                        st.markdown(data.get("result", ""))
                        if "credits_left" in data:
                            st.sidebar.info(f"🎁 Créditos restantes: {data['credits_left']}")
                    elif data and "detail" in data:
                        st.error(f"❌ Error ({response.status_code}): {data['detail']}")
                    else:
                        st.error(f"❌ Error del servidor ({response.status_code}): {response.text}")

                except Exception as e:
                    st.error(f"Error de conexión con el backend: {e}")
