import streamlit as st
import requests

st.set_page_config(page_title="Generador de Contenido", page_icon="⚡")

st.title("⚡ Generador de Contenido & Guiones Virales")

# URL de tu backend en Render
BACKEND_URL = "https://tu-backend-en-render.onrender.com/api/v1/generar"  # <-- Reemplaza con tu URL real
PAYMENT_LINK = "https://stripe.com"  # <-- Tu enlace de pago

# Usamos st.form para asegurar que Streamlit tome el correo nuevo al hacer clic
with st.form("formulario_generacion"):
    email = st.text_input("Tu Correo Electrónico", placeholder="ejemplo@correo.com")
    prompt = st.text_area("¿Qué contenido deseas crear?", placeholder="Ejemplo: Escribe un guion para un Short...")
    submitted = st.form_submit_button("Generar Contenido", type="primary")

if submitted:
    if not email:
        st.warning("Por favor, ingresa tu correo electrónico.")
    elif not prompt:
        st.warning("Por favor, ingresa la idea para tu contenido.")
    else:
        with st.spinner("Generando contenido con IA..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"email": email.strip().lower(), "prompt": prompt}
                )
                data = response.json()

                if response.status_code == 200:
                    st.success("¡Contenido generado!")
                    st.markdown(data.get("result"))
                    
                    credits = data.get("credits_left", 0)
                    email_proc = data.get("email", email)
                    st.info(f"💳 Créditos restantes para {email_proc}: {credits}")
                else:
                    error_msg = data.get("detail", "Error al procesar la solicitud.")
                    st.error(f"❌ {error_msg}")
                    if "agotado" in error_msg.lower():
                        st.link_button("🛒 Comprar más créditos", PAYMENT_LINK)
            except Exception as e:
                st.error(f"Error de conexión con el servidor: {e}")
