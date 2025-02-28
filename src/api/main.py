from fastapi import FastAPI
from routes import router
import uvicorn

# Crear instancia de FASTAPI
app = FastAPI(title="API Documentation Generator")

app.include_router(router)

# ruta base
@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de generación de documentación"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)