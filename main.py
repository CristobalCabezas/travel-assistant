from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from langgraph.graph import StateGraph
from graph import part_4_graph
import uuid
import json
import os
from state import State
from langchain_core.messages import ToolMessage, AIMessage
from utilities import _print_event
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


# Cargar las variables desde el archivo .env
load_dotenv()

# Ahora puedes acceder a las variables de entorno
openai_api_key = os.getenv("OPENAI_API_KEY")

# Usa la API key en tu aplicación


# Crear la aplicación FastAPI
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas las fuentes
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)

# Inicializar el grafo de estados y otros recursos necesarios
conversation_history = []
sessions = {}

class Message(BaseModel):
    content: str

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    # Crear un identificador único para cada sesión
    thread_id = str(uuid.uuid4())
    # Inicializar la configuración del grafo para esta sesión
    last_message = []

    try:
        while True:
            # Recibir el mensaje del usuario a través del WebSocket
            data = await websocket.receive_text()
            json_data = json.loads(data)
            message = json_data.get("message")
            currency = json_data.get("currency")
            os.environ["CURRENCY"] = currency
            language = json_data.get("language")
            os.environ["LANGUAGE"] = language
            token = json_data.get("token")
            os.environ["CTS_TOKEN"] = token
            config = {"configurable": {"thread_id": thread_id, "language": language, "currency": currency}}
            _printed = set()
            try:
                events = part_4_graph.stream(
                    {"messages": [{"role": "user", "type": "text", "content": message}]}, config, stream_mode="values"
                )
                for event in events:
                    _print_event(event, _printed)
                    for message in event.get('messages', []):
                        if isinstance(message, AIMessage) and message.content:
                            if message.content not in last_message:
                                await websocket.send_json(message.content)
                                last_message.append(message.content)
                #snapshot = part_4_graph.get_state(config)
            except Exception as e:
                await websocket.send_text(f"Error: {str(e)}")
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8100)