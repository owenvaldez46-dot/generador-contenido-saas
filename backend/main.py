import os
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from supabase import create_client, Client

app = FastAPI(title="API Generador de Contenido SaaS")

# Inicializar clientes
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

class GenerateRequest(BaseModel):
    email: str
    prompt: str

@app.get("/")
def home():
    return {"message": "Backend activo"}

@app.post("/api/v1/generar")
def generar_contenido(req: GenerateRequest):
    email = req.email.strip().lower()
    
    if not email:
        raise HTTPException(status_code=400, detail="El correo electrónico es obligatorio.")

    # 1. Buscar usuario en Supabase
    res = supabase.table("profiles").select("*").eq("email", email).execute()
    user_data = res.data

    # Parsear respuesta si viene en formato texto JSON
    if isinstance(user_data, str):
        try:
            user_data = json.loads(user_data)
        except Exception:
            user_data = []

    # 2. Determinar o asignar créditos
    if not user_data:
        # Registrar nuevo usuario con 3 créditos
        new_user = {"email": email, "credits": 3}
        supabase.table("profiles").insert(new_user).execute()
        credits_left = 3
    else:
        # Extraer el registro de forma segura
        row = user_data[0] if isinstance(user_data, list) and len(user_data) > 0 else user_data
        
        if isinstance(row, dict):
            credits_left = row.get("credits", 3)
        else:
            credits_left = 3

    # 3. Validar créditos disponibles
    if credits_left <= 0:
        raise HTTPException(
            status_code=400, 
            detail="Has agotado tus 3 créditos gratuitos."
        )

    # 4. Generar respuesta con OpenAI
    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en redacción de contenido SaaS y copywriter profesional."},
                {"role": "user", "content": req.prompt}
            ],
            max_tokens=500
        )
        generated_text = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al conectar con OpenAI: {str(e)}")

    # 5. Descontar 1 crédito
    new_credits = credits_left - 1
    supabase.table("profiles").update({"credits": new_credits}).eq("email", email).execute()

    return {
        "result": generated_text,
        "credits_left": new_credits
    }
