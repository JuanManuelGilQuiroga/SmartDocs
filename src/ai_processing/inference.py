import torch
import json
from model_loader import load_model
import os

# Cargar modelo entrenado
model, tokenizer = load_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def generate_documentation(code_snippet):
    model.eval()
    code_json = json.dumps(code_snippet, indent=4) 
    inputs = tokenizer(code_json, return_tensors="pt", truncation=True, padding="max_length", max_length=8192).to(device)
    output = model.generate(**inputs, max_length=8192, num_beams=5, early_stopping=True)
    return tokenizer.decode(output[0], skip_special_tokens=True)

def documentation_controller(code):
    documentation_array = []
    for route, code_snippet in code:
        documentation = generate_documentation(code_snippet)
        documentation_index = {
            "ruta": route,
            "documentacion": documentation
        }
        documentation_array.append(documentation_index)
    return documentation_array

def generate(code_snippet):
    code_json = json.dumps(code_snippet, indent=4)
    return code_json
# Ejemplo de uso
if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "data/creation_testing.json")

    with open(config_path, "r") as f:
        config = json.load(f)

    test_documentation = generate_documentation(config)
    print(test_documentation)
