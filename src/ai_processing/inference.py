from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

MODELO_HF = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODELO_HF)
modelo = AutoModelForCausalLM.from_pretrained(
    MODELO_HF,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,  # Optimiza RAM
    device_map="auto"  # Carga automática en GPU si está disponible
)

device = "cuda" if torch.cuda.is_available() else "cpu"


def documentation_generator(prompt):

    #prompt = f"<|user|>\nEres una IA que genera la documentacion de codigo en python, explicando que hace\n\nPregunta: Dime que hace este codigo de python {query}\n\n<|assistant|>"
    
    entrada = tokenizer(prompt, return_tensors="pt").to(device)
    print(entrada)
    print(tokenizer.decode(entrada["input_ids"][0]))
    salida = modelo.generate(**entrada, max_new_tokens=180, temperature=0.7, top_p=0.9, do_sample=True)
    respuesta = tokenizer.decode(salida[0], skip_special_tokens=True)

    # Extraer solo la parte después de "Respuesta:"
    if "<|assistant|>" in respuesta:
        respuesta = respuesta.split("<|assistant|>")[-1].strip()

    return respuesta

def prompt_generator(key, code):
    """Genera un string con los imports separados por líneas."""
    documentation = """"""
#    if code.get("imports"):
#        all_imports = "\n".join(code["imports"])
#        prompt = f"""Contexto:\nEres una IA que extrae las herramientas que son importadas en un codigo en python, tu tarea es analizar las siguientes importaciones y listar los nombres de las herramientas importadas.\n\nPregunta: Dime que herramientas importa este codigo de python {all_imports}\n\nRespuesta: """
#        imports_documentation = documentation_generator(prompt)
#        print(type(imports_documentation))
#        documentation += key + "\n" + imports_documentation + "\n\n"
#        print(all_imports)
#    if code.get("classes"):
#        return ""
    if code.get("functions"):
        functions_documentation = """
        FUNCIONES:

        """
        for name, func in code["functions"].items():
            prompt = f"""<|user|>\nEres una IA que genera la documentacion de codigo en python, \n\nPregunta: El siguiente nombre es el nombre de la función: {name}; Y el siguiente código es el cuerpo de una función de Python. Analízalo e infiere qué hace la función, qué parámetros recibe y qué valor retorna: {func}\n\n<|assistant|>"""
            print(prompt)
            function_documentation = documentation_generator(prompt)
            functions_documentation += name + "\n" + function_documentation + "\n"
        documentation += functions_documentation + "\n\n"
        print(functions_documentation)
    return ""  # Retorna string vacío si no hay imports


def file_iterator(diccionario):
    """Itera sobre el diccionario y obtiene los imports de cada archivo."""
    files_documentation = []  

    for filename, contenido in diccionario.items():
        documentation = prompt_generator(filename, contenido)  


    return "hola"



diccionario_codigo = {
        "C:/Users/Solvo/AppData/Local/Temp/tmp9np0ib_k\\gestionDeTareasPython-main\\app.py": {
            "classes": {},
            "functions": {},
            "imports": [
                "import streamlit as st",
                "from db.controllers import addTask, getTasks, markTaskCompleted, deleteCompletedTask, deleteCompletedTasks",
                "from utils.file_io import exportTasks, importTasks",
                "import time"
            ]
        },
        "C:/Users/Solvo/AppData/Local/Temp/tmp9np0ib_k\\gestionDeTareasPython-main\\db\\controllers.py": {
            "classes": {},
            "functions": {
                "addTask": "task = Task(title=title, description=description)\n    session.add(task)\n    session.commit()",
                "getTasks": "return session.query(Task).all()",
                "markTaskCompleted": "task = session.query(Task).get(taskId)\n    if task:\n        task.completed = True\n        session.commit()",
                "deleteCompletedTask": "task = session.query(Task).get(taskId)\n    if task.completed == True:\n        session.delete(task)\n        session.commit()",
                "deleteCompletedTasks": "session.query(Task).filter(Task.completed == True).delete()\n    session.commit()"
            },
            "imports": [
                "from .models import Session, Task"
            ]
        },
        "C:/Users/Solvo/AppData/Local/Temp/tmp9np0ib_k\\gestionDeTareasPython-main\\db\\models.py": {
            "classes": {
                "Task": {
                    "docstring": "No docstring",
                    "methods": {}
                }
            },
            "functions": {},
            "imports": [
                "from sqlalchemy import create_engine, Column, Integer, String, Boolean",
                "from sqlalchemy.ext.declarative import declarative_base",
                "from sqlalchemy.orm import sessionmaker",
                "import os"
            ]
        },
        "C:/Users/Solvo/AppData/Local/Temp/tmp9np0ib_k\\gestionDeTareasPython-main\\utils\\file_io.py": {
            "classes": {},
            "functions": {
                "exportTasks": "session = Session()\n    tasks = session.query(Task).all()\n    with open(filepath, 'w') as file:\n        json.dump([\n            {\"id\": task.id, \"title\": task.title, \"description\": task.description, \"completed\": task.completed}\n            for task in tasks\n        ], file)",
                "importTasks": "session = Session()\n    with open(filepath, 'r') as file:\n        tasks = json.load(file)\n        for task_data in tasks:\n            task = Task(\n                id=task_data[\"id\"],\n                title=task_data[\"title\"],\n                description=task_data[\"description\"],\n                completed=task_data[\"completed\"]\n            )\n            session.merge(task)\n        session.commit()"
            },
            "imports": [
                "import json",
                "from db.models import Task, Session"
            ]
        }
    }



funcion_individual = """
def addTask(title, description):
    task = Task(title=title, description=description)
    session.add(task)
    session.commit()
"""

#print(documentation_generator(funcion_individual))

print(file_iterator(diccionario_codigo))