import streamlit as st
import requests

BACKEND_URL = "https://generador-contenido-saas.onrender.com"

# Enlace a tu pasarela de pagos (reemplazar con tu link real cuando lo crees)
PAYMENT_LINK = "https://lemon-squeezy.com" 

st.set_page_config(page_title="Generador Viral SaaS", page_icon="⚡", layout="centered")
st.title("⚡ Generador de Contenido & Guiones Virales")

# Barra lateral
st.sidebar.header("Acceso de Usuario")
email = st.sidebar.text_input("Ingresa tu correo:", placeholder="ejemplo@correo.com")

if not email:
    st.warning("👈 Por favor, ingresa tu correo en la barra lateral para comenzar.")
else:
    st.sidebar.success("Sesión activa")
    
    # Sección comercial
    st.sidebar.markdown("---")
    st.sidebar.subheader("💳 Planes y Créditos")
    st.sidebar.link_button("🚀 Comprar Más Créditos", PAYMENT_LINK, use_container_width=True)
    st.sidebar.markdown("---")
    
    prompt = st.text_area("¿Qué contenido deseas crear?", placeholder="Ej: Escribe un guion viral para un video corto sobre las pirámides...")
    
    if st.button("Generar Contenido", type="primary"):
        if not prompt.strip():
            st.error("Escribe una instrucción antes de generar.")
        else:
            with st.spinner("Procesando tu contenido..."):
                try:
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/generar",
                        json={"email": email, "prompt": prompt}
                    )
                    
                    try: data = response.json()
                    except Exception: data = None

                    if response.status_code == 200 and data:
                        st.success("¡Contenido generado!")
                        st.markdown(data.get("result", ""))
                        st.sidebar.info(f"🎁 Créditos restantes: {data.get('credits_left', 0)}")
                    elif data and "detail" in data:
                        st.error(f"❌ {data['detail']}")
                    else:
                        st.error(f"❌ Error del servidor ({response.status_code})")

                except Exception as e:
                    st.error(f"Error de conexión: {e}")
