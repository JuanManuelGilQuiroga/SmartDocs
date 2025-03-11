# ESTE ARCHIVO SE USA PARA CREAR EL DATASET PARA PRACTICAR FINE-TUNING PERO EN ESTA PRIMER VERSION NO SE NECESITA
import json
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import AutoTokenizer
import os

class CodeDocumentationDataset(Dataset):
    # Inicializa la clase con:
    # - file_path: Ruta del archivo JSON con ejemplos de código y documentación.
    # - tokenizer: Tokenizador del modelo para procesar los textos.
    # - max_tokens: Número máximo de tokens permitidos en cada muestra (input + output).
    # - input_ratio: Proporción de tokens asignados al código (el resto será para la documentación).
    def __init__(self, file_path, tokenizer, max_tokens=2048, input_ratio=0.7):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"❌ Error: No se encontró el archivo {file_path}")

        self.data = self.load_data(file_path)
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.input_ratio = input_ratio 

        # Dividimos los tokens disponibles entre input (código) y output (documentación)
        self.max_code_tokens = int(self.max_tokens * self.input_ratio)
        self.max_doc_tokens = self.max_tokens - self.max_code_tokens

        print(f"✅ {len(self.data)} ejemplos cargados desde {file_path}")

    # Usa el archivo json cargado en la instancia para obtener los datos
    def load_data(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def __len__(self):
        return len(self.data)

    # Tokeniza el codigo y la documentacion usada para entrenar el modelo, asigna padding para que no hayan errores con los tensores, y devuelve tensores para pytorch
    def __getitem__(self, idx):
        item = self.data[idx]

        all_imports = []
        all_functions = []
        all_classes = []
        
        for file_path, file_content in item["input"].items():
            all_imports.extend(file_content.get("imports", []))
            all_functions.extend(file_content["functions"].values())
            all_classes.extend(file_content["classes"].values())
        
        imports = "\n".join(all_imports)
        functions = "\n".join(all_functions)
        classes = "\n".join(all_classes)
        source = (
            f"<IMPORTS>\n{imports}\n\n"
            f"<FUNCTIONS>\n{functions}\n\n"
            f"<CLASSES>\n{classes}"
        )

        print(source)

        target = item["output"]

        tokenized_input = self.tokenizer(source, max_length=self.max_code_tokens, truncation=True, padding="max_length", return_tensors="pt")
        tokenized_target = self.tokenizer(target, max_length=self.max_doc_tokens, truncation=True, padding="max_length", return_tensors="pt")

        labels = tokenized_input["input_ids"].clone()
        labels[:, :-1] = tokenized_input["input_ids"][:, 1:]
        labels[:, -1] = -100
        # Este return es fundamental para entrenar el modelo porque le proporciona: ✔ Entrada (input_ids): Código tokenizado.
        # ✔ Máscara (attention_mask): Indica tokens válidos.
        # ✔ Salida esperada (labels): Documentación tokenizada.
        return {
            "input_ids": tokenized_input["input_ids"].squeeze(),
            "attention_mask": tokenized_input["attention_mask"].squeeze(),
            "labels": labels.squeeze()
        }

# Esta funcion es la que se invoca pra poder usar la clase, se importa el modelo, se crea el tokenizer y se crea la instancia de la clase para tokenizar tanto el train data como el test data
# Se crea un dataloader para poder entrenar el modelo
def get_data_loaders(config):
    tokenizer = AutoTokenizer.from_pretrained(config["model_name"])
    tokenizer.pad_token = tokenizer.eos_token
    print("📂 Cargando datos de entrenamiento...")
    train_dataset = CodeDocumentationDataset(config["train_data_path"], tokenizer, config["max_seq_length"])
    
    print("📂 Cargando datos de prueba...")
    test_dataset = CodeDocumentationDataset(config["test_data_path"], tokenizer, config["max_seq_length"])
    
    # DataLoader convierte los datasets en batches para que el modelo los procese de manera eficiente.
    # Parámetros:
    # batch_size=config["batch_size"]: Número de ejemplos por batch.
    # shuffle=True para entrenamiento: Mezcla los datos aleatoriamente en cada época.
    # shuffle=False para prueba: Mantiene el orden de los datos.
    train_loader = DataLoader(train_dataset, batch_size=config["batch_size"], shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=config["batch_size"], shuffle=False)

    print(f"📊 Número de ejemplos de entrenamiento: {len(train_dataset)}")
    print(f"📊 Número de ejemplos de prueba: {len(test_dataset)}")

    return train_loader, test_loader, tokenizer

"""config = {
    "model_name": "Salesforce/codet5-base",
    "epochs": 3,
    "batch_size": 8,
    "learning_rate": 5e-5,
    "max_seq_length": 512,
    "train_data_path": "C:/Users/Solvo/Desktop/SmartDocs/src/ai_processing/data/train.json",
    "test_data_path": "C:/Users/Solvo/Desktop/SmartDocs/src/ai_processing/data/test.json",
    "save_model_path": "saved_models/codet5_finetuned"
}

train_loader, test_loader, tokenizer = get_data_loaders(config)"""