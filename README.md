# CopyAI Express - SaaS MVP

Este es el prototipo inicial (MVP) para una plataforma de generación de contenido automatizada con FastAPI y Streamlit.

## Estructura del Proyecto

```text
generador-contenido-saas/
├── .env.example
├── requirements.txt
├── README.md
├── backend/
│   └── main.py
└── frontend/
    └── app.py
```

## Instrucciones de Instalación y Uso

1. **Crear entorno virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar Backend (Terminal 1):**
   ```bash
   uvicorn backend.main:app --reload
   ```

4. **Ejecutar Frontend (Terminal 2):**
   ```bash
   streamlit run frontend/app.py
   ```
