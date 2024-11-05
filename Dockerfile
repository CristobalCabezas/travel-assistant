# Usa una imagen base de Python 3.11
FROM python:3.11-slim

# Instala Poetry
RUN pip install poetry

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de configuración de Poetry
COPY pyproject.toml poetry.lock /app/

# Instala las dependencias sin crear un entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copia el resto de la aplicación
COPY . /app

# Expone el puerto que usará la aplicación (8080 es el puerto predeterminado en Google Cloud Run)
EXPOSE 8100

# Configura la variable de entorno PORT
ENV PORT=8100

# Comando para iniciar la aplicación
CMD ["python", "main.py"]

