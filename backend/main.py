from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="API Generador de Contenido SaaS",
    description="Backend para generación automatizada de copys y scripts de venta",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProductInput(BaseModel):
    nombre_producto: str
    descripcion: str
    tono: str = "Persuasivo y directo"
    audiencia: str = "Público general"

@app.get("/")
def home():
    return {"status": "ok", "message": "API de Generación de Contenido Activa"}

@app.post("/api/v1/generar")
def generar_contenido(data: ProductInput):
    api_key = os.getenv("OPENAI_API_KEY")
    
    # MODO DEMO: Si no hay clave de OpenAI configurada
    if not api_key or api_key == "tu_api_key_aqui_opcional":
        return {
            "status": "demo",
            "titulo_seo": f"¡Descubre {data.nombre_producto}! La mejor opción para ti",
            "instagram_caption": f"✨ ¿Buscabas la solución ideal? Conoce {data.nombre_producto}.\n\n📌 {data.descripcion}\n\n👉 ¡Haz clic en el enlace de nuestra bio y pide el tuyo hoy mismo!\n\n#Ecommerce #{data.nombre_producto.replace(' ', '')} #Oferta",
            "script_tiktok": f"🔴 HOOK (0-3s):\n'¡Si estás buscando {data.nombre_producto}, no compres nada sin ver esto primero!'\n\n🟢 CUERPO (3-15s):\n'Te presento {data.nombre_producto}. {data.descripcion}. Diseñado específicamente para {data.audiencia}.'\n\n🔵 CTA (15-20s):\n'Consíguelo con envío directo haciendo clic en la tienda aquí abajo.'"
        }

    # MODO PRODUCCIÓN: OpenAI real
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        prompt = f'''
        Eres un experto Copywriter Senior especializado en E-commerce.
        Crea contenido comercial para el siguiente producto:
        - Producto: {data.nombre_producto}
        - Descripción/Características: {data.descripcion}
        - Tono: {data.tono}
        - Público Objetivo: {data.audiencia}

        Responde ÚNICAMENTE en formato JSON válido con las siguientes claves:
        {{
            "titulo_seo": "Título llamativo para tienda online (máx 60 caracteres)",
            "instagram_caption": "Texto para post de Instagram con emojis, estructura y hashtags",
            "script_tiktok": "Guion estructurado con HOOK (gancho), CUERPO y Call To Action (CTA)"
        }}
        '''

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente de marketing que solo responde con JSON estructurado."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        contenido = json.loads(response.choices[0].message.content)
        return {"status": "success", **contenido}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
