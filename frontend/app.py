import streamlit as st
import requests

st.set_page_config(
    page_title="CopyAI Express - SaaS",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ CopyAI Express")
st.markdown("Genera copys de alta conversión para **Instagram, TikTok y tu Tienda Online** en segundos.")
st.divider()

col_formulario, col_resultados = st.columns([1, 1], gap="large")

with col_formulario:
    st.subheader("📝 Datos del Producto")
    
    nombre_producto = st.text_input(
        "Nombre del producto o servicio*",
        placeholder="Ej. Termo Inteligente con Pantalla LED"
    )
    
    descripcion = st.text_area(
        "Características principales*",
        placeholder="Ej. Mantiene bebidas frías por 24 horas, muestra la temperatura exacta en la tapa, libre de BPA.",
        height=120
    )

    tono = st.selectbox(
        "Tono del copy",
        ["Persuasivo y directo", "Entusiasta y divertido", "Urgencia y oferta", "Profesional y elegante"]
    )

    audiencia = st.text_input(
        "Público objetivo",
        placeholder="Ej. Deportistas, universitarios, ejecutivos de oficina"
    )

    btn_generar = st.button("🚀 Generar Contenido", type="primary", use_container_width=True)

with col_resultados:
    st.subheader("✨ Resultados Generados")

    if btn_generar:
        if not nombre_producto or not descripcion:
            st.warning("⚠️ Por favor completa el nombre y la descripción para continuar.")
        else:
            with st.spinner("Procesando propuesta comercial..."):
                try:
                    payload = {
                        "nombre_producto": nombre_producto,
                        "descripcion": descripcion,
                        "tono": tono,
                        "audiencia": audiencia or "Público general"
                    }
                    
                    res = requests.post("http://localhost:8000/api/v1/generar", json=payload)
                    
                    if res.status_code == 200:
                        data = res.json()

                        if data.get("status") == "demo":
                            st.info("💡 **Modo Demostración:** Configura tu `OPENAI_API_KEY` en el archivo `.env` para obtener respuestas en tiempo real con GPT.")

                        tab_ig, tab_tt, tab_seo = st.tabs(["📸 Instagram Caption", "🎵 Script TikTok / Reels", "📌 Título SEO"])

                        with tab_ig:
                            st.text_area("Copia y pega en tu publicación:", value=data.get("instagram_caption", ""), height=200)

                        with tab_tt:
                            st.text_area("Guion de video:", value=data.get("script_tiktok", ""), height=200)

                        with tab_seo:
                            st.text_input("Título para tu web:", value=data.get("titulo_seo", ""))

                        st.success("¡Contenido generado con éxito!")
                    else:
                        st.error("Error al procesar la solicitud con el servidor.")

                except requests.exceptions.ConnectionError:
                    st.error("❌ No se pudo conectar con el Backend. Asegúrate de ejecutar uvicorn en la terminal.")
    else:
        st.info("Completa los campos a la izquierda y presiona **Generar Contenido**.")
