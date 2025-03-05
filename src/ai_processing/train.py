import json
import torch
import os
from transformers import AutoModelForCausalLM
from dataset import get_data_loaders

# Obtener la ruta absoluta del directorio donde está este script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta absoluta a config.json
config_path = os.path.join(current_dir, "config.json")

# Cargar configuración
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# Verificar dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Cargar datos
train_loader, test_loader, tokenizer = get_data_loaders(config)

# Cargar modelo
model = AutoModelForCausalLM.from_pretrained(config["model_name"]).to(device)

# AdamW es un optimizador basado en Adam, pero con decay de pesos (mejor para transformers).
# model.parameters() pasa los parámetros del modelo al optimizador.
# lr=config["learning_rate"] establece la tasa de aprendizaje.
optimizer = torch.optim.AdamW(model.parameters(), lr=config["learning_rate"])

# Entrenamiento
# Cambia el modelo a un modo de entrenamiento donde se activan ciertas capas que mejoran este proceso como dropout y batch normalization
model.train()

# Define cuantas veces iterara por completo el modelo sobre el dataset para entrenarse, esto son epochs.
for epoch in range(config["epochs"]):
    total_loss = 0
    # Itera por cada batch de la train data, esta se divide en batchs (lotes) porque asi le resulta mas sencillo al modelo
    for batch in train_loader:
        #En PyTorch, los gradientes se acumulan después de cada backward(), así que hay que reiniciarlos en cada iteración. Si no se hace, los gradientes de los batches anteriores afectarían el entrenamiento.
        optimizer.zero_grad()
        # Se extraen los tensores de entrada, mascara y etiquetas y se mueven al cuda o CPU 
        input_ids, attention_mask, labels = batch["input_ids"].to(device), batch["attention_mask"].to(device), batch["labels"].to(device)
        # Se le pasa lo anterior al modelo, genera una predicción y devuelve outputs, que contiene la pérdida (loss) y las salidas generadas.
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        # Es la perdida calculada por el modelo, define que tan bien esta generando 
        loss = outputs.loss
        # Calcula los gradientes de la pérdida con respecto a los pesos del modelo. Este paso es fundamental para que el modelo aprenda de los errores y mejore en cada iteración
        loss.backward()
        # Optimiza los pesos del modelo con ayuda de los gradientes 
        optimizer.step()
        # Se usa para calcular el promedio de perdida de las epochs
        total_loss += loss.item()
    # Muestra el promedio de loss en cada epoch, si el loss disminuye es que el modelo esta mejorando
    print(f"Epoch {epoch + 1}, Loss: {total_loss / len(train_loader)}")

# Guardar modelo entrenado
os.makedirs(config["save_model_path"], exist_ok=True)
model.save_pretrained(config["save_model_path"])
tokenizer.save_pretrained(config["save_model_path"])
print("Modelo guardado exitosamente.")
