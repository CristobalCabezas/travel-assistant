from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from datetime import datetime
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
from google.cloud import storage
from dotenv import load_dotenv


# Load the variables from the .env file
load_dotenv()

# Now you can access the environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Use the API key in your application


# Create the FastAPI application
app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Initialize the state graph and other necessary resources
conversation_history = []
sessions = {}

# Configure the Google Cloud Storage client
storage_client = storage.Client() if os.getenv("ENABLE_STORAGE_LOGS") == "True" else None
bucket_name = "travel-assistant-logs"

class Message(BaseModel):
    content: str

@app.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    # Create a unique identifier for each session
    thread_id = str(uuid.uuid4())
    # Initialize the graph configuration for this session
    last_message = []

    # Create log conversation log file
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"logs/{current_time}_conversation_{thread_id}.log"
    log_path = os.path.join(os.getcwd(), log_filename)

    try:
        with open(log_path, "a") as log_file:
            while True:
                # Receive the user's message through the WebSocket
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
                        print_event = _print_event(event, _printed)
                        log_file.write(f"{print_event}\n\n")
                        log_file.flush()
                        for message in event.get('messages', []):
                            if isinstance(message, AIMessage) and message.content:
                                if message.content not in last_message:
                                    await websocket.send_json(message.content)
                                    last_message.append(message.content)
                    #snapshot = part_4_graph.get_state(config)
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    await websocket.send_text(error_message)
                    log_file.write(f"{error_message}\n\n")
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {thread_id}")
    except Exception as e:
        await websocket.close()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if storage_client:
                bucket = storage_client.bucket(bucket_name)
                blob = bucket.blob(log_filename)
                blob.upload_from_filename(log_path)

                # Delete the local file after uploading it to the bucket
                if os.path.exists(log_path):
                    os.remove(log_path)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error uploading log to Cloud Storage: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8100)