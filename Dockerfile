# Usa una imagen base de Python 3.11
FROM python:3.11-slim

# Instala Poetry y python-dotenv
RUN pip install poetry python-dotenv

# Configura el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de configuración de Poetry
COPY pyproject.toml poetry.lock /app/

# Instala las dependencias sin crear un entorno virtual dentro del contenedor
RUN poetry config virtualenvs.create false && poetry install --no-root

# Copia el resto de la aplicación
COPY . /app

# Copia el archivo .env al contenedor
COPY .env /app/.env

# Expone el puerto que usará la aplicación (8100 en este caso)
EXPOSE 8100

# Configura la variable de entorno PORT
ENV PORT=8100

# Comando para iniciar la aplicación
CMD ["python", "main.py"]


