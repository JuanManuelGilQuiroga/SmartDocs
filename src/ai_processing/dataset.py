import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
import os

class CodeDocumentationDataset(Dataset):
    def __init__(self, file_path, tokenizer, max_length=512):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Error: No se encontró el archivo {file_path}")

        self.data = self.load_data(file_path)
        self.tokenizer = tokenizer
        self.max_length = max_length

        print(f"✅ {len(self.data)} ejemplos cargados desde {file_path}")

    def load_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        source = item["code"]
        target = item["doc"]

        tokenized_input = self.tokenizer(source, max_length=self.max_length, truncation=True, padding="max_length", return_tensors="pt")
        tokenized_target = self.tokenizer(target, max_length=self.max_length, truncation=True, padding="max_length", return_tensors="pt")

        return {
            "input_ids": tokenized_input["input_ids"].squeeze(),
            "attention_mask": tokenized_input["attention_mask"].squeeze(),
            "labels": tokenized_target["input_ids"].squeeze()
        }

def get_data_loaders(config):
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    
    print("📂 Cargando datos de entrenamiento...")
    train_dataset = CodeDocumentationDataset(config["train_data_path"], tokenizer, config["max_seq_length"])
    
    print("📂 Cargando datos de prueba...")
    test_dataset = CodeDocumentationDataset(config["test_data_path"], tokenizer, config["max_seq_length"])
    
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config["batch_size"], shuffle=False)

    print(f"📊 Número de ejemplos de entrenamiento: {len(train_dataset)}")
    print(f"📊 Número de ejemplos de prueba: {len(test_dataset)}")

    return train_loader, test_loader, tokenizer

config = {
    "model_name": "Salesforce/codet5-base",
    "epochs": 3,
    "batch_size": 8,
    "learning_rate": 5e-5,
    "max_seq_length": 512,
    "train_data_path": "C:/Users/Solvo/Desktop/SmartDocs/src/ai_processing/data/train.json",
    "test_data_path": "C:/Users/Solvo/Desktop/SmartDocs/src/ai_processing/data/test.json",
    "save_model_path": "saved_models/codet5_finetuned"
}

train_loader, test_loader, tokenizer = get_data_loaders(config)