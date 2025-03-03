import streamlit as st
import tempfile
import zipfile
import os
import shutil
import requests
from dotenv import load_dotenv

load_dotenv()

st.title("📄 SmartDocs")

repo = st.file_uploader("📂  Upload your ZIP folder here", type=["zip"])

if repo is not None:
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(repo, "r") as zip_repo:
        zip_repo.extractall(temp_dir) # Extraer todo el contenido al directorio temporal
        
    path = temp_dir.replace(os.sep, "/")
    
    api_url = os.getenv("API_URL")
    payload = {"repo_path": path}
    
    try:
        response = requests.post(api_url, json=payload)
        response.raise_for_status()  # Verificar si hubo errores en la solicitud
        result = response.json()
        st.success("✅ Respuesta de la API:")
        st.write(result["generate_docs"])
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error al llamar a la API: {e}")

    
    shutil.rmtree(temp_dir)  