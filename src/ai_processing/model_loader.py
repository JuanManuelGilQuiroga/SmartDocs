import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import json
import os

# Cargar configuración
config_path = os.path.join(os.path.dirname(__file__), "config.json")

with open(config_path, "r") as f:
    config = json.load(f)

# Verificar dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def load_model():
    model = AutoModelForSeq2SeqLM.from_pretrained(config["save_model_path"]).to(device)
    tokenizer = AutoTokenizer.from_pretrained(config["save_model_path"])
    return model, tokenizer

model, tokenizer = load_model()
print("Modelo cargado exitosamente.")