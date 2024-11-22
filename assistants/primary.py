import os
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model="gpt-4o", temperature=0)

class ToHotelBookingAssistant(BaseModel):
    """Transfer work to a specialized assistant to handle hotel bookings."""

    location: str = Field(
        description="The location where the user wants to book a hotel."
    )
    checkin_date: str = Field(description="The check-in date for the hotel.")
    checkout_date: str = Field(description="The check-out date for the hotel.")
    request: str = Field(
        description="Any additional information or requests from the user regarding the hotel booking."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Zurich",
                "checkin_date": "2023-08-15",
                "checkout_date": "2023-08-20",
                "request": "I prefer a hotel near the city center with a room that has a view.",
            }
        }


class ToBookExcursion(BaseModel):
    """Transfers work to a specialized assistant to handle trip recommendation and other excursion bookings."""

    location: str = Field(
        description="The location where the user wants to book a recommended trip."
    )
    request: str = Field(
        description="Any additional information or requests from the user regarding the trip recommendation."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "location": "Lucerne",
                "request": "The user is interested in outdoor activities and scenic views.",
            }
        }


primary_assistant_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Your name is CTS Travel Assistant."
            "You are a customer service assistant for CTS Turismo (Chilean Travel Services). "
            "CTS Turismo is a tourism company that offers varied tourism services in Chile. "
            "The services they offer are the following: hotels, excursions and transferss. "
            "Hotels: Hotel reservations throughout Chile. "
            "Excursions: Tours and activities in different cities and locations in Chile. "
            "Transfers: Transportation from one point to another, such as to and from the airport or the bus terminal, or to and from the snow or the beach, etc. "
            "You will recive a message from the user indicating wich service the user needs. "
            "Your goal is to delegate the task to the appropriate specialized assistant. "
            "You have two specialized assistants available to help you:\n"
            "1. Hotel Booking Assistant: Specialized in handling hotel bookings.\n"
            "2. Excursion and Transfers Booking Assistant: Specialized in handling trip recommendations/excursion bookings, and transfer services.\n"
            "The user may also ask you to modify (update) or cancel a reservation. In this case, you must find out to which service the reservation corresponds: "
            "If the user needs to modify (update)/cancel a hotel reservation, you should delegate or escalate to assistant 1; "
            "the user needs to modify (update)/cancel an excursion or transfer reservation, you should delegate or escalate to assistant 2, just described.\n"
            "By default, you must give your answers in {language}. However, if the user writes to you in a different language, your answers should be in that language. "
            "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If a search comes up empty, expand your search before giving up. "
            "When you return an answer, use the markdown format to make it more readable."
            "\nCurrent time: {time}. "
            "\nCurrency: {currency}. "
            "If user doesn't provide a year, always assume is a future date. Never use past dates to search availability. ",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now(), language=os.getenv("LANGUAGE"), currency=os.getenv("CURRENCY"))

primary_assistant_tools = [
    #TavilySearchResults(max_results=1)
]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToHotelBookingAssistant,
        ToBookExcursion,
    ]
)