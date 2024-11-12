from typing import Optional
import requests
import os
from langchain_core.tools import tool


@tool
def get_availability_for_transfer_and_excursions(
    townId: int,
    tipos: int,
    fecha: str,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    ) -> list[dict]:
    """
    Get availability of transport or excursions in a given town.

    Args:
    townId: The town ID. (Never ask it to the user, just use the 'get_town_id_for_transport_and_excursions' tool to get it)
    tipos: The type of service. 1 is for transfer, and 2 is for excursions.
    fecha (string): The date (format YYYY-MM-DD).
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.

    Returns:
    A list of dictionaries containing the availability of
    transport or excursions in the given town.

    Example:
    get_availability_for_transport_and_excursions(townId='1234', tipos='1', fecha='2024-12-01', adults=2, children=1, currency=1)
    """

    currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
    url = f'{os.getenv("CTS_API_V2")}/availability/?townId={townId}&tipos={tipos}&fecha={fecha}&adults={adults}&children={children}&currency={currency}'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.get(url, headers=headers)

    if tipos == 1:
        result = generate_transfer_availability_response(response.json())
    if tipos == 2:
        result = generate_excursion_availability_response(response.json())
    return result

@tool
def get_town_id_for_transport_and_excursions(townName: str) -> list[dict]:
    """
    Get the town ID.

    Args:
    townName: The town or city name.

    Returns:
    The Town ID.

    Example:
    get_town_id_for_transport_and_excursions('santiago')
    """
    url = f'{os.getenv("CTS_API_V2")}/city/'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.get(url, headers=headers)

    result = 'We could not find the town you are looking for, but here is a list of towns available. '
    result += 'Select the town you are looking for and use the town ID to search for the availability of transport or excursions.\n\n'
    result += 'Town ID\t|\tTown Name\n'
    for town in response.json():
        result += f"{town['id']}\t|\t{town['name']}\n"
        if town['name'].lower() == townName.lower():
            return town['id']
    return result

@tool
def get_excursion_or_transfer_description(
    serviceNumber: int,
    townId: int,
    tipos: int,
    date: str,
    adults: int,
    children: int,
)->list [dict]:
    """
    Get the information of the excursion or transfer.

    Args:
    serviceNumber: The service number.
    townId: The town ID.
    tipos: The type of service. 1 is for transfer, and 2 is for excursions.
    date (string): The date (format YYYY-MM-DD).
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    """
    currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
    url = f'{os.getenv("CTS_API_V2")}/availability/?townId={townId}&tipos={tipos}&fecha={date}&adults={adults}&children={children}&currency={currency}'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = { 'Authorization': f'token {ctsToken}' }
    response = requests.get(url, headers = headers).json()

    service = 'excursion' if tipos == 2 else 'transfer'
    result = generate_excursion_or_transfer_description_response(response[serviceNumber-1], service)

    return result

@tool
def get_excursion_or_transfer_options_avilable(
    serviceNumber: int,
    townId: int,
    tipos: int,
    date: str,
    adults: int,
    children: int
)->list [dict]:
    """
    Get the options for excursions or transfers.

    Args:
    serviceNumber: The service number.
    townId: The town ID.
    tipos: The type of service. 1 is for transfer, and 2 is for excursions.
    fecha (string): The date (format YYYY-MM-DD).
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.

    Returns:
    A list of dictionaries containing the availability of
    transport or excursions in the given town.

    Example:
    get_excursion_or_transfer_options(townId=1234, tipos=1, fecha='2024-12-01', adults=2, children=1, currency=1)
    """
    currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
    url = f'{os.getenv("CTS_API_V2")}/availability/?townId={townId}&tipos={tipos}&fecha={date}&adults={adults}&children={children}&currency={currency}'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = { 'Authorization': f'token {ctsToken}' }
    response = requests.get(url, headers = headers).json()

    service = 'excursion' if tipos == 2 else 'transfer'
    result = generate_excursion_or_transfer_options_response(response[serviceNumber-1], service)

    return result

@tool
def create_transport_or_excursion_booking(
    serviceNumber: int,
    serviceCode: int,
    townId: int,
    tipos: int,
    language: str,
    travelDate: str,
    firstName: str,
    lastName: str,
    email: str,
    phone: str,
    passportOrDni: str,
    country: str,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    referenceNumber: Optional[str] = 'N/A',
    notes: Optional[str] = 'N/A',
    flightNumber: Optional[str] = 'N/A',
    ) -> dict:
    """
    Create a transport or excursion booking.

    Args:
    serviceNumber: The service number.
    serviceCode: The service code.
    townId: The town ID.
    tipos: The type of service. 1 is for transfer, and 2 is for excursions.
    travelDate (string): The date (format YYYY-MM-DD).
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    firstName: The first name of the passenger.
    lastName: The last name of the passenger.
    email: The email of the passenger.
    phone: The phone number of the passenger.
    passportOrDni: The passport or DNI of the passenger.
    country: The country of the passenger.
    referenceNumber: The reference number.
    notes: The notes.
    flightNumber: The flight number.
    language: The language of the service. There are only three options: 'Español', 'Inglés' and 'Portuguese'.

    Returns:
    The booking ID.

    Example:
    create_transport_or_excursion_booking()
    """

    currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
    serviceAvailability = get_data_for_excursion_or_transfer_booking(serviceNumber=serviceNumber, serviceCode=serviceCode, townId=townId, tipos=tipos, travelDate=travelDate, adults=adults, children=children)
    serviceCode = serviceAvailability['service_code']
    adults = serviceAvailability['adults']
    children = serviceAvailability['children']
    salePrice = serviceAvailability['sale_price']
    # Get the language from serviceAvailability['language'] (array) where equals to language
    for serviceLanguage in serviceAvailability['language']:
        if serviceLanguage == language:
            language = serviceLanguage
            break
    travelDate = serviceAvailability['travel_date']

    payload = {
        "passenger": {
            "name": firstName,
            "last_name": lastName,
            "country": country,
            "email": email,
            "passport_or_dni": passportOrDni,
            "phone": phone
        },
        "notes": notes,
        "reference_number": referenceNumber,
        "currency": currency,
        "services": [
            {
                "service_code": serviceCode,
                "adults": adults,
                "children": children,
                "sale_price": salePrice,
                "language": language,
                "travel_date": travelDate,
                "flight_number": flightNumber,
                "notes": notes
            }
        ],
    }
    url = f'{os.getenv("CTS_API_V2")}/booking/'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.post(url, json=payload, headers=headers).json()
    bookingId = response['booking_id']
    return f"Se ha realizado la reserva con éxito. El número de reserva es {bookingId}"

#TODO
@tool
def update_transport_or_excursion_booking() -> list[dict]:
    """
    Update a transport or excursion booking.

    Returns:
    The booking ID.

    Example:
    update_transport_or_excursion_booking()
    """
    url = f'{os.getenv("CTS_API_V2")}/booking/'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.put(url, headers=headers)
    return response.json()

@tool
def cancel_transport_or_excursion_booking(bookingId: str) -> list[dict]:
    """
    Cancel a transport or excursion booking.

    Args:
    bookingId: The booking ID.
    
    Returns:
    The booking ID.
    
    Example:
    cancel_transport_or_excursion_booking('1234')
    """
    url = f'{os.getenv("CTS_API_V2")}/booking/{bookingId}/'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.delete(url, headers=headers).json()
    if response['is_active'] == False:
        return f'La reserva con el número {bookingId} ha sido cancelada con éxito.'
    return 'No se ha podido cancelar la reserva.'




# Helpers

def generate_excursion_availability_response(excursions):
    result = 'The excursions available are the following:\n\n'
    i = 1
    for excursion in excursions:
        isRegular = []
        result += f"EXCURSION SERVICE {i}:\n"
        result += f"Name (Spanish): {excursion['glosas']['g_text_es']}\n"
        result += f"Name (English): {excursion['glosas']['g_text_en']}\n"
        result += f'(Use the exursion name acording to the language used by the user. If you are not sure, just translate to the related language)\n'
        result += f'(Also, if necesary, translate the labels to the language used by the user)\n'
        result += f"Price: From ${excursion['services'][0]['sale_price']} {excursion['services'][0]['currency']}\n"
        result += f"Service duration: {excursion['services'][0]['service_duration']}\n"
        result += f"Pickup from: {excursion['services'][0]['meeting_point']}, {excursion['services'][0]['city'].title()}\n"
        result += f"Children allowed: {'Yes' if excursion['services'][0]['allow_childs'] else 'No'}\n"
        result += f"Includes: {', '.join(excursion['concepts'])}\n"
        for service in excursion['services']:
            isRegular.append(service['is_regular'])
        isRegular = list(set(isRegular))
        if len(isRegular) == 1:
            result += f"Type of service: {'Shared' if isRegular[0] else 'Private'}\n\n"
        else:
            result += f"Type of service: Shared and Private\n\n"
        i += 1
    return result


def generate_transfer_availability_response(transfers):
    result = 'The excursions available are the following:\n\n'
    i = 1
    for transfer in transfers:
        isRegular = []
        result += f"TRANSFER SERVICE {i}:\n"
        result += f"Name (Spanish): {transfer['glosas']['g_text_es']}\n"
        result += f"Name (English): {transfer['glosas']['g_text_en']}\n"
        result += f'(Use the transfer name acording to the language used by the user. If you are not sure, just translate to the related language)\n'
        result += f'(Also, if necesary, translate the labels to the language used by the user)\n'
        result += f"Price: From ${transfer['services'][0]['sale_price']} {transfer['services'][0]['currency']}\n"
        result += f"Pickup from: {transfer['services'][0]['meeting_point']}, {transfer['services'][0]['city'].title()}\n"
        result += f"Free cancelation: {'Yes' if transfer['services'][0]['cancellation_date'] else 'No'}\n"
        for service in transfer['services']:
            isRegular.append(service['is_regular'])
        isRegular = list(set(isRegular))
        if len(isRegular) == 1:
            result += f"Type of service: {'Shared' if isRegular[0] else 'Private'}\n\n"
        else:
            result += f"Type of service: Shared and Private\n\n"
        i += 1
    return result

def generate_excursion_or_transfer_options_response(options, service):
    result = f"The options available for this {service} are the following:\n\n"
    i = 1
    for option in options['services']:
        result += f"OPTION {i}:\n"
        result += f"Service code: {option['service_code']} (Never show this item to the user, keep only for you)\n"
        result += f"Travel date: {option['travel_date']}\n"
        result += f"Cancelation date: Until {option['cancellation_date']}\n"
        result += f"Language: {', '.join(option['language'])}\n"
        result += f"Price: ${option['sale_price']} {option['currency']}\n"
        result += f"Service duration: {option['service_duration']}\n"
        result += f"Pickup from: {option['meeting_point']}, {option['city'].title()}\n"
        result += f"Type of service: {'Shared' if option['is_regular'] else 'Private'}\n"
        result += f"Guide: {option['guide']}\n\n"
        i += 1
    return result

def generate_excursion_or_transfer_description_response(description, service):
    result = f"The {service} information is the following:\n\n"
    result += f"Name (Spanish): {description['glosas']['g_text_es']}\n"
    result += f"Name (English): {description['glosas']['g_text_en']}\n"
    result += f"Description (Spanish): {description['descriptions']['d_text_es']}\n"
    result += f"Description (English): {description['descriptions']['d_text_en']}\n"
    result += f'(Use the description name and description acording to the language used by the user. If you are not sure, just translate to the related language)\n'
    result += f"Includes: {', '.join(description['concepts'])}\n"
    result += f"City: {description['city']}\n"
    result += f'(Also, if necesary, translate the labels to the language used by the user)\n\n'
    return result

def get_data_for_excursion_or_transfer_booking(
    serviceNumber: int,
    serviceCode: int,
    townId: str,
    tipos: int,
    travelDate: str,
    adults: int,
    children: int
    ) -> dict:
    """
    Get the data for a transport or excursion booking.

    Args:
    serviceNumber: The service number.
    serviceCode: The service code.
    townId: The town ID.
    tipos: The type of service. 1 is for transfer, and 2 is for excursions.
    travelDate (string): The travel date.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.

    Returns:
    The booking response as a string with the booking ID and
    a link to the booking detail.
    """
    currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
    url = f'{os.getenv("CTS_API_V2")}/availability/?townId={townId}&tipos={tipos}&fecha={travelDate}&adults={adults}&children={children}&currency={currency}'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.get(url, headers=headers).json()
    services = response[serviceNumber-1]
    result = next((service for service in services['services'] if service['service_code'] == serviceCode), None)
    return result