from pydantic import BaseModel # Pydantic permite definir modelos de datos con validaciones.

# Define los modelos de datos que se usan en la API para validar la información de entrada y salida.

# Modelo para la solicitud (input)
class DocumentationRequest(BaseModel):
    repo_path: str
    
# Modelo para la respuesta (output)
class DocumentationResponse(BaseModel):
    repo_path: str
    generate_docs:str