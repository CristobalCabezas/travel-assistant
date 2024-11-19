from typing import Optional
import requests
import os
from langchain_core.tools import tool
import helpers.excursion_helper as helper

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
        result = helper.generate_transfer_availability_response(response.json(), fecha, adults, children, townId)
    if tipos == 2:
        result = helper.generate_excursion_availability_response(response.json(), fecha, adults, children, townId)
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
    serviceId: int,
    townId: int,
    tipos: int,
    date: str,
    adults: int,
    children: int,
)->list [dict]:
    """
    Get the information of the excursion or transfer.

    Args:
    serviceId: The service Id.
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

    for service in response:
        if service['id'] == serviceId:
            serviceOptions = service
            break
    service = 'excursion' if tipos == 2 else 'transfer'
    result = helper.generate_excursion_or_transfer_description_response(serviceOptions, service)

    return result

@tool
def get_excursion_or_transfer_options_avilable(
    serviceId: int,
    townId: int,
    tipos: int,
    date: str,
    adults: int,
    children: int = 0
)->list [dict]:
    """
    Get the options for excursions or transfers.

    Args:
    serviceId: The service Id. It does not correspond to the service code, so do not confuse them.
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
    # extract the service object from response['id']
    for service in response:
        if service['id'] == serviceId:
            serviceOptions = service
            break
    service = 'excursion' if tipos == 2 else 'transfer'
    result = helper.generate_excursion_or_transfer_options_response(serviceOptions, service)

    return result

@tool
def create_transport_or_excursion_booking(
    serviceId: int,
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
    serviceId: The service Id.
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
    try:
        currency = 1 if os.getenv("CURRENCY") == 'CLP' else 2
        serviceAvailability = helper.get_data_for_excursion_or_transfer_booking(serviceId=serviceId, serviceCode=serviceCode, townId=townId, tipos=tipos, travelDate=travelDate, adults=adults, children=children)
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
    except Exception as e:
        return f"No se ha podido realizar la reserva. {e}"

#TODO
# @tool
# def update_transport_or_excursion_booking() -> list[dict]:
#     """
#     Update a transport or excursion booking.

#     Returns:
#     The booking ID.

#     Example:
#     update_transport_or_excursion_booking()
#     """
#     url = f'{os.getenv("CTS_API_V2")}/booking/'
#     ctsToken = os.getenv("CTS_TOKEN")
#     headers = {'Authorization': f'token {ctsToken}'}
#     response = requests.put(url, headers=headers)
#     return response.json()

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