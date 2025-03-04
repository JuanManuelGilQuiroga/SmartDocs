from fastapi import APIRouter
import os
import sys
from models import DocumentationRequest, DocumentationResponse
from src.code_parser.extract_code import extract_code
from src.code_parser.parse_ast import ast_analysis
from src.code_parser.preprocess import clean_code
from ai_processing.inferences import generate_doccumentation


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
# Se crea un router para agrupar las rutas
router = APIRouter() 

@router.post("/documentation")
async def generate_docs(request: DocumentationRequest):
    extracted_code = extract_code(request.repo_path)
    cleaned_code = clean_code(extracted_code)
    code = ast_analysis(cleaned_code)
    documentation = generate_doccumentation(code)
    return DocumentationResponse(repo_path = request.repo_path, generate_docs=documentation)