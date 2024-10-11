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
        schema_extra = {
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
        schema_extra = {
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
            "The services they offer are the following: hotels, excursions, transfers and tour packages. "
            "Hotels: Hotel reservations throughout Chile. "
            "Excursions: Tours and activities in different cities and locations in Chile. "
            "Transfers: Transportation from one point to another, such as to and from the airport or the bus terminal, or to and from the snow or the beach, etc. "
            "Tour packages: Combination of hotels, excursions and transfers at a single price. "
            "Your goal is to help users find the services described above and all other relevant information. "
            "By default, you must give your answers in Spanish. However, if the user writes to you in a different language, your answers should be in that language. "
            "Use the tools provided to search for hotels, excursions, transfers and packages and other information that will help in the user's queries. "
            "If a customer requests to create, update or cancel a hotel, transfer or excursion reservation; or, when searching for a hotel, excursion or transfer, needs specialized recommendations, "
            "delegate the task to the appropriate specialized assistant by invoking the corresponding tool. You are not able to make these types of changes yourself. "
            "The user is not aware of the different specialized assistants, so do not mention them; just quietly delegate through function calls. "
            "Provide detailed information to the customer, and always double-check the database before concluding that information is unavailable. "
            "When searching, be persistent. Expand your query bounds if the first search returns no results. "
            "If a search comes up empty, expand your search before giving up."
            #"\n\nCurrent user flight information:\n<Flights>\n{user_info}\n</Flights>"
            "\nCurrent time: {time}.",
        ),
        ("placeholder", "{messages}"),
    ]
).partial(time=datetime.now())

primary_assistant_tools = [
    TavilySearchResults(max_results=1)
]
assistant_runnable = primary_assistant_prompt | llm.bind_tools(
    primary_assistant_tools
    + [
        ToHotelBookingAssistant,
        ToBookExcursion,
    ]
)