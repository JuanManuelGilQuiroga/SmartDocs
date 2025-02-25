# Usa una imagen oficial de Python como base
FROM python:3.10-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de dependencias y las instala
COPY requirements.txt ./
RUN pip install --upgrade pip
RUN pip install --default-timeout=300 --no-cache-dir -r requirements.txt

# Copia el código fuente al contenedor
COPY . .

# Expone el puerto si la aplicación tiene una API
EXPOSE 8000

# Comando de inicio del contenedor
CMD ["python", "main.py"]
