from langchain_core.tools import tool
import os
import requests
from datetime import date, datetime, timedelta
from typing import Optional, List, Dict
import helpers.hotel_helper as helper

@tool
def get_availability_for_hotels(
    townId: Optional[str] = None,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    infants: Optional[int] = 0,
    ages: Optional[List[int]] = [],
) -> List[Dict]:
    """
    Get availability of hotels in a given town.

    Args:
    townId: The town ID.
    checkin_date (string): The check-in date.
    checkout_date (string): The check-out date.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    infants: The number of infants. Default is 0.
    ages: The ages of the children. Default is [].

    Returns:
    A list of dictionaries containing the availability of
    hotels in the given town.

    Example:
    get_availability(townId='1234', checkin_date='2022-12-01', checkout_date='2022-12-05', adults=2, children=1)
    """
    try:
        url = f'{os.getenv("CTS_API_V1")}/hotel/'

        ctsToken = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {ctsToken}'}
        currency = 1 if os.getenv('CURRENCY') == 'CLP' else 2
        json = {'townId': townId, 'checkin': checkin_date, 'checkout': checkout_date, 'rooms': [{'adults': adults, 'children': children, 'infants': infants, 'ages': ages}], 'currency': currency}
        response = requests.post(url, json=json, headers=headers)
        result = helper.generate_hotels_availability_response(response.json(), json)
        return result
    except Exception as e:
        return f'Error: {e}, in line {e.__traceback__.tb_lineno}'

@tool
def get_hotel_info(
    hotelId: str,
    townId: Optional[str] = None,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    infants: Optional[int] = 0,
    ages: Optional[list[int]] = [],
) -> list[dict]:
    """
    Get general information from a specific hotel.

    Args:
    hotelId: The hotel ID.
    townId: The town ID.
    checkin_date (string): The check-in date.
    checkout_date (string): The check-out date.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    infants: The number of infants. Default is 0.
    ages: The ages of the children. Default is [].

    Use this function when the user wants to know information about a specific hotel.

    Returns:
    A list of dictionaries containing the general information of a specific hotel.
    With the following structure:

    Example:
    get_availability(hotelId = '196', townId='1234', checkin_date='2022-12-01', checkout_date='2022-12-05', adults=2, children=1)
    """
    try:
        url = f'{os.getenv("CTS_API_V1")}/hotel/{hotelId}/'

        ctsToken = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {ctsToken}'}
        currency = 1 if os.getenv('CURRENCY') == 'CLP' else 2
        json = {'townId': townId, 'checkin': checkin_date, 'checkout': checkout_date, 'rooms': [{'adults': adults, 'children': children, 'infants': infants, 'ages': ages}], 'currency': currency}
        response = requests.post(url, json=json, headers=headers).json()
        hotelData = response['data']
        hotelId = hotelData['id']
        hotelName = hotelData['name']
        hotelAdress = hotelData['address']
        hotelCategory = hotelData['category']['name']
        hotelStars = hotelData['category']['rating']
        hotelDescriptionSpanish = hotelData['policies_description']
        hotelDescriptionEnglish = hotelData['policies_description_en']
        hotelAmmenities = ', '.join([amenity['name'] for amenity in hotelData['ammenities']])

        result = f'The hotel {hotelName} has the following information: \n\n'
        result += f'Hotel ID: {hotelId} (Never show this item to the user, keep only for you)\n'
        result += f'Hotel Name: {hotelName}\n'
        result += f'Hotel Address: {hotelAdress}\n'
        result += f'Hotel Category: {hotelCategory}\n'
        result += f'Hotel Stars: {hotelStars}\n'
        result += f'Hotel Description (Spanish): {hotelDescriptionSpanish}\n'
        result += f'Hotel Description (English): {hotelDescriptionEnglish}\n'
        result += f'(Use the hotel description acording to the language used by the user. If you are not sure, just translate to the related language)\n\n'
        result += f'(Also, if necesary, translate the labels to the language used by the user)\n'
        result += f'Hotel Ammenities: {hotelAmmenities}\n\n'

        return result
    except Exception as e:
        return f'Error: {e}, in line {e.__traceback__.tb_lineno}'

@tool
def get_hotel_rooms_available(
    hotelId: str,
    townId: Optional[str] = None,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    infants: Optional[int] = 0,
    ages: Optional[list[int]] = [],
) -> list[dict]:
    """
    Get the rooms available in a given hotel.

    Args:
    hotelId: The hotel ID.
    townId: The town ID.
    checkin_date (string): The check-in date.
    checkout_date (string): The check-out date.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    infants: The number of infants. Default is 0.
    ages: The ages of the children. Default is [].

    Use this function when the user wants already has selected a hotel and wants to reserve a room.
    You have to show the rooms available with the format below.

    Returns:
    A list of dictionaries containing the rooms available in
    one hotel in the given hotel id, with the following format:

    ROOM {NUMBER}:
    Room Id
    Room type or name
    Price
    Rate plan
    Cancellation policy
    Cancellation time
    Meal plan
    Adults
    Bed options

    Example:
    get_availability(hotelId = '196', townId='1234', checkin_date='2022-12-01', checkout_date='2022-12-05', adults=2, children=1)
    """
    try:
        url = f'{os.getenv("CTS_API_V1")}/hotel/{hotelId}/'

        ctsToken = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {ctsToken}'}
        currency = 1 if os.getenv('CURRENCY') == 'CLP' else 2
        json = {'townId': townId, 'checkin': checkin_date, 'checkout': checkout_date, 'rooms': [{'adults': adults, 'children': children, 'infants': infants, 'ages': ages}], 'currency': currency}
        response = requests.post(url, json=json, headers=headers).json()
        hotelName = response['data']['name']
        availability = response['data']['availability']
        result = f'The rooms available in {hotelName} from {checkin_date} to {checkout_date} are: \n\n'
        roomsList = []
        i = 1
        for available in availability:
            currency = 'CLP' if available['currency_id'] == 1 else 'USD'
            for room in available['rooms']:
                if room['roomtype_id'] in roomsList:
                    continue
                result += f'ROOM {i}: \n'
                roomId = room['roomtype_id']
                result += f'Room Id: {roomId}\n'
                roomType = room['roomtype']
                result += f'Room type or name: {roomType}\n'
                price = available['price_value_with_tax']
                if currency == 'CLP':
                    result += f'Price: ${price} {currency}, tax included.\n'
                else:
                    result += f'Price: ${price} {currency}.\n'
                ratePlan = room['rateplan_name']
                result += f'Rate plan: {ratePlan}\n'
                cancellation = room['cancellation_type']
                result += f'Cancellation policy: {cancellation}\n'
                cancellationTime = datetime.strptime(checkin_date, '%Y-%m-%d') - timedelta(hours=response['data']['cancellation'])
                result += f'Cancellation time: {cancellationTime.strftime("%d de %B de %Y")}\n'
                mealPlan = room['mealplan']
                result += f'Meal plan: {mealPlan}\n'
                adults = room['adults']
                result += f'Adults: {adults}\n'
                bedOptions = room['bed_options']
                size = room['size']
                result += f'Bed options: {bedOptions} ({size})\n\n'
                roomsList.append(roomId)
                i += 1

        return result
    except Exception as e:
        return f'Error: {e}, in line {e.__traceback__.tb_lineno}'

@tool
def get_town_id_for_hotels(townName: str) -> List[Dict]:
    """
    Get the town ID.

    Args:
    townName: The town or city name.

    Returns:
    The Town ID.

    Example:
    get_city_id('santiago')
    """

    # Set townName to uppercase and replace written accents
    townName = townName.upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    
    url = f'https://apibooking.ctsturismo.com/api/city/dtt/?q='
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    response = requests.get(url, headers=headers)

    result = 'We could not find the town you are looking for, but here is a list of towns available. '
    result += 'Select the town you are looking for and use the town ID to search for hotels availability.\n\n'
    result += 'Town ID\t|\tTown Name\n'
    for town in response.json():
        result += f"{town['dtt_id']}\t|\t{town['display_name']}\n"
        dttTownName = town['display_name'].upper().replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        if dttTownName == townName:
            return town['dtt_id']
    return result

@tool
def create_hotel_booking(
    hotelId: int,
    townId: Optional[str] = None,
    checkin_date: Optional[str] = None,
    checkout_date: Optional[str] = None,
    adults: Optional[int] = 1,
    children: Optional[int] = 0,
    infants: Optional[int] = 0,
    ages: Optional[list[int]] = [],
    roomId: int = None,
    name: Optional[str] = '',
    lastName: Optional[str] = '',
    email: Optional[str] = '',
    phone: Optional[str] = '',
    passportOrDni: Optional[str] = '',
    country: Optional[str] = None,
    referenceNumber: Optional[str] = '',
    notes: Optional[str] = '',
) -> dict:
    """
    Create a hotel booking.

    Args:
    hotelId: The hotel ID.
    townId: The town ID.
    checkin_date (string): The check-in date, in 'YYYY-mm-dd' format.
    checkout_date (string): The check-out date, in 'YYYY-mm-dd' format.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    infants: The number of infants. Default is 0.
    ages: The ages of the children. Default is [].
    roomId: The room ID.
    name: The name of the guest.
    lastName: The last name of the guest.
    email: The email of the guest.
    phone: The phone number of the guest.
    passportOrDni: The passport or DNI of the guest.
    country: The country of the guest.
    referenceNumber: The reference number.
    notes: The notes.

    Returns:
    The booking response as a string with the booking ID and
    a link to the booking detail.
    """
    try:
        currency = 1 if os.getenv('CURRENCY') == 'CLP' else 2
        hotelAvailability = helper.get_data_for_booking(hotelId=hotelId, townId=townId, checkin_date=checkin_date, checkout_date=checkout_date, adults=adults, children=children, infants=infants, ages=ages)
        if not hotelAvailability:
            raise ValueError("No availabilty found for this hotel.")
        hotelData = hotelAvailability['data']
        townName = hotelData['town']['name']
        hotelName = hotelData['name']
        ammenities = hotelData['ammenities']
        concepts = ', '.join([amenity['name'] for amenity in ammenities])
        user = 1
        currency = 'CLP' if currency == 1 else 'USD'
        avail = hotelData['availability']
        availability = None
        for dispo in avail:
            for room in dispo['rooms']:
                if room['roomtype_id'] == roomId:
                    availability = dispo
        if not availability:
            raise ValueError("Room with the specified roomId not found in availability data.")
        markup = availability['markup'][0]
        bookingAvailabilityList = []
        availabilityDetails = availability['details']
        primary_image_url = next((image["url"] for image in hotelData["images"] if image["is_primary"]), None)
        rooms = availability['rooms']
        #convert checkin_date and checkout_date from 'YYY-mm-dd' to 'dd-mm-YYY'
        checkin_date_inv = datetime.strptime(checkin_date, '%Y-%m-%d').strftime('%d-%m-%Y')
        checkout_date_inv = datetime.strptime(checkout_date, '%Y-%m-%d').strftime('%d-%m-%Y')

        # Collecting booking information
        for room in rooms:
            inventory_ids = []
            for detail in room['details']:
                inventory_id = detail['inventory_id']
                rate_id = detail['rate_id']
                room_name = room['roomtype']
                inventory_ids.append({
                    'inventoryId': inventory_id,
                    'roomName': room_name,
                    'rateIds': [rate_id],
                    'adults': [room['adults']],
                    'amount': 1  # Assuming one room per inventory
                })

            bookingAvailabilityList.append({
                'hotelId': hotelData['id'],
                'hotelName': hotelData['name'],
                'inventoryIds': inventory_ids
            })

        # Extracting pricing and guest details
        priceBase = availability['price_base']
        priceValue = availability['price_value']
        priceValueWithTax = availability['price_value_with_tax']
        additionalBase = availability['additional_base']
        additionalTotalBase = availability['additional_total_base']
        additionalValueWithTax = availability['additional_value_with_tax']
        
        # Defining payload details
        payload_detail = [
            {
                "date": detail['date'],
                "total": detail['total'],
                "total_base": detail['total_base'],
                "total_with_tax": detail['total_with_tax'],
                "additional_base": detail['additional_base'],
                "additional_total_base": detail['additional_total_base'],
                "additional_total_with_tax": detail['additional_total_with_tax'],
                "rooms": detail['rooms']
            } for detail in availabilityDetails
        ]

        payload = {
            "name": name,
            "last_name": lastName,
            "passport_or_dni": passportOrDni,
            "email": email,
            "phone": phone,
            "country": country,
            "notes": notes,
            "currency": currency,
            "adults": adults,
            "children": children,
            "infants": infants,
            "total_amount": priceValueWithTax,
            "total_net_amount": priceValue,
            "total_collect_amount": priceValueWithTax,
            "reference_number": referenceNumber,
            "user": user,
            "booking_availability": bookingAvailabilityList,
            "cart_items": {
                "count": 1,
                "hotels": [
                    {
                        "dtt_hotel_code": hotelId,
                        "dtt_hotel_markup": markup,
                        "glosa_visualizer": hotelName,
                        "glosa_soptur": hotelName,
                        "provider": "DTT",
                        "city": townName,
                        "concepts": concepts,
                        "country": townName,
                        "service_type": "hotel",
                        "adults": adults,
                        "children": children,
                        "infants": infants,
                        "adult_total_amount": priceValueWithTax,
                        "children_total_amount": additionalValueWithTax,
                        "amount": priceValueWithTax,
                        "net_amount": priceValue,
                        "pull_inventory": "false",
                        "hotel_additional_total": additionalTotalBase,
                        "hotel_additional_base": additionalBase,
                        "hotel_total": priceBase,
                        "travel_date": checkin_date_inv,
                        "checkout": checkout_date_inv,
                        "cover_image": primary_image_url,
                        "payload_detail": payload_detail,
                        "dtt_fee_percent": 0,
                        "dtt_fee_value": 0,
                        "total_dtt": 0,
                        "rooms": rooms,
                        "id": 3,
                        "nights": 2,
                        "hotelName": hotelName,
                        "roomType": room_name,
                        "subTotalPrice": priceValue,
                        "taxPrice": priceValueWithTax - priceValue,
                        "totalPrice": priceValueWithTax,
                        "serviceUrl": f"/results/hotels/{hotelId}?townId=51&checkin={checkin_date}&checkout={checkout_date}&rooms=[{{%22adults%22:{adults},%22children%22:{children},%22infants%22:{infants},%22ages%22:[]}}]#rooms",
                        "item_extras": {
                            "address": hotelData['address'],
                            "description": hotelData['policies_description'],
                            "checkinHour": hotelData['checkin'],
                            "checkoutHour": hotelData['checkout'],
                            "hotelPhone": hotelData['phone']
                        },
                        "cancellationTime": hotelData['cancellation'],
                        "additional_information": notes
                    }
                ],
                "services": [],
                "packages": [],
                "createdAt": datetime.now().isoformat(),
                "discount": {}
            },
            "language": "es",
            "company": None
        }

        url = f'{os.getenv("CTS_API_V1")}/booking/'
        cts_token = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {cts_token}', 'origin': 'localhost'}

        response = requests.post(url, headers=headers, json=payload).json()

        if response:
            if response.get("errors"):
                return f'Error: {response["errors"]}'
            booking_id = response['file_number']
            slug = response['slug']
            booking_link = os.getenv("FRONT_HOST") + f'/bookings/{slug}'
            return f'The booking has been successfully created. The booking number is {booking_id}. You can view the booking details at the following link: {booking_link}'
        else:
            print("Empty response received")
            return "Error: Empty response received from the server"

    except Exception as e:
        print(f"Error: {e}")
        return f"Error: {e}"

@tool
def update_hotel_booking(
        bookingId: str, 
        additionalInformation: Optional[str] = '',
        notes: Optional[str] = '',
        referenceNumber: Optional[str] = ''
        ) -> list[dict]:
    """
    Update a hotel booking.

    Returns:
    The booking ID.

    Args:
    bookingId: The booking ID.
    additionalInformation: Any comments or remarks addressed to the hotel.
    notes: Any comments or remarks addressed to the booking customer or CTS Turismo itself.
    referenceNumber: The reference number.

    Example:
    update_hotel_booking('1234', additionalInformation='Room with a view', flightNumber='1234', notes='Late check-in', referenceNumber='1234')
    """
    try:
        bookingDetails = helper.get_booking_details(bookingId)
        if bookingId not in bookingDetails['file_number']:
            return "No se ha encontrado la reserva."
        bookingSlug = bookingDetails['slug']
        bookingUpdate = {}
        ctsToken = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {ctsToken}', 'origin': 'localhost'}
        if additionalInformation != "":
            url = f'{os.getenv("CTS_API_V1")}/booking/item/{bookingDetails["items"][0]["id"]}/'
            bookingUpdate['additional_information'] = additionalInformation
            bookingUpdate['flight_number'] = ''
        if notes != "" or referenceNumber != '':
            url = f'{os.getenv("CTS_API_V1")}/booking/{bookingSlug}/'
            bookingUpdate['notes'] = notes
            bookingUpdate['reference_number'] = referenceNumber

        response = requests.put(url, json=bookingUpdate, headers=headers).json()
        if response['file_number']:
            return f'La reserva con el número {bookingId} ha sido actualizada con éxito. Puede ver los detalles de la reserva en el siguiente enlace: {os.getenv("FRONT_HOST")}/bookings/{bookingSlug}'
        else:
            return 'No se ha podido actualizar la reserva.'
    except Exception as e:
        return f'Error: {e}'

@tool
def cancel_hotel_booking(bookingId: str) -> List[Dict]:
    """
    Cancel a hotel booking.

    Args:
    bookingId: The booking ID.

    Returns:
    The booking ID.

    Example:
    cancel_hotel_booking('1234')
    """
    try:
        url = f'{os.getenv("CTS_API_V1")}/booking/cancel/'
        ctsToken = os.getenv("CTS_TOKEN")
        headers = {'Authorization': f'token {ctsToken}'}
        json = {'file_number': bookingId}
        response = requests.post(url, json=json, headers=headers).json()
        if response:
            slug = response['slug']
            return f'La reserva con el número {bookingId} ha sido cancelada con éxito. Puede consultar el estado de la reserva en el siguiente enlace: {os.getenv("FRONT_HOST")}/bookings/{slug}'
        else:
            return 'No se ha podido cancelar la reserva.'
    except Exception as e:
        return f'Error: {e}'