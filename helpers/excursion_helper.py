import requests
import os

def generate_excursion_availability_response(excursions, date, adults, children, townId, infants=0):
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
            result += f"Type of service: {'Shared' if isRegular[0] else 'Private'}\n"
        else:
            result += f"Type of service: Shared and Private\n"
        result += f"See details: {os.getenv('FRONT_HOST')}/travel-assistant/services/{excursion['id']}?desde={date}&hasta={date}&adults={adults}&children={children}&infants={infants}&pax={adults}&townName={excursion['city'].title()}&townId={townId}&serviceType=2\n\n"
        i += 1
    return result


def generate_transfer_availability_response(transfers, date, adults, children, townId, infants=0):
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
            result += f"Type of service: {'Shared' if isRegular[0] else 'Private'}\n"
        else:
            result += f"Type of service: Shared and Private\n"
        result += f"See details: {os.getenv('FRONT_HOST')}/travel-assistant/transfer/{transfer['id']}?desde={date}&hasta={date}&adults={adults}&children={children}&infants={infants}&pax={adults}&townName={transfer['city'].title()}&townId={townId}&serviceType=1\n\n"
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
    serviceId: int,
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
    serviceId: The service Id.
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
    for services in response:
        if services['id'] == serviceId:
            services = services
            break
    result = next((service for service in services['services'] if service['service_code'] == serviceCode), None)
    return result