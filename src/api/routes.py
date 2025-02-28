from fastapi import APIRouter
from models import DocumentationRequest, DocumentationResponse
from code_parser.parse_ast import ast_analysis
from ai_processing.inferences import generate_doccumentation

# Se crea un router para agrupar las rutas
router = APIRouter() 

@router.post("/documentation")
async def generate_docs(request: DocumentationRequest):
    extracted_code = ast_analysis(request.repo_path)
    documentation = generate_doccumentation(extracted_code)
    return DocumentationResponse(repo_path = request.repo_path, generate_docs=documentation)