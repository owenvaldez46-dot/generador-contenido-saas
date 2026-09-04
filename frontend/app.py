import streamlit as st
import requests

st.set_page_config(page_title="Generador de Contenido", page_icon="⚡")

st.title("⚡ Generador de Contenido & Guiones Virales")

# URL de tu backend en Render
BACKEND_URL = "https://tu-backend-en-render.onrender.com/api/v1/generar"  # <-- Reemplaza con tu URL real
PAYMENT_LINK = "https://stripe.com"  # <-- Tu enlace de pago

with st.form("formulario_generacion"):
    email = st.text_input("Tu Correo Electrónico", placeholder="ejemplo@correo.com")
    prompt = st.text_area("¿Qué contenido deseas crear?", placeholder="Ejemplo: Haz un guion de Alejandro Magno...")
    submitted = st.form_submit_button("Generar Contenido", type="primary")

if submitted:
    if not email:
        st.warning("Por favor, ingresa tu correo electrónico.")
    elif not prompt:
        st.warning("Por favor, ingresa la idea para tu contenido.")
    else:
        with st.spinner("Conectando con el servidor e IA..."):
            try:
                response = requests.post(
                    BACKEND_URL,
                    json={"email": email.strip().lower(), "prompt": prompt},
                    timeout=60
                )
                
                # Intentar interpretar la respuesta como JSON
                try:
                    data = response.json()
                except Exception:
                    st.error(f"❌ El servidor devolvió una respuesta no válida (Código HTTP {response.status_code}). Verifica si el servicio en Render está iniciando.")
                    st.stop()

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

            except requests.exceptions.Timeout:
                st.error("⏰ El servidor tardó demasiado en responder (despertando de inactividad). Intenta nuevamente en 10 segundos.")
            except Exception as e:
                st.error(f"Error de conexión con el servidor: {e}")
