# Usa una imagen base de Python 3.11 slim
FROM python:3.11-slim

# Instala Poetry
RUN pip install poetry

# Configura el directorio de trabajo
WORKDIR /app

# Copia los archivos de configuración de Poetry
COPY pyproject.toml poetry.lock /app/

# Instala las dependencias sin crear un entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copia el resto de la aplicación al contenedor
COPY . /app

# Copia el archivo .env
#COPY .env /app/.env

# Expone el puerto que usará la aplicación
EXPOSE 8100

# Configura la variable de entorno PORT
ENV PORT=8100

# Comando para iniciar la aplicación
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8100"]



