import requests
import os
from typing import Optional

def generate_hotels_availability_response(json_response, payload):
    result = f'The hotels available are the following: \n\n'
    for data in json_response['data']:
        hotelId = data['id']
        hotelName = data['name']
        townId = data['town_id']
        rating = data['category']['rating']
        stars = ''
        for i in range(rating):
            stars += '★'
        hotelAddress = data['address']
        priceList = map(lambda x: x['price_value_with_tax'], data['availability'])
        priceFrom = min(priceList)
        currency = 'CLP' if payload['currency'] == 1 else 'USD'
        ammenities = ', '.join([amenity['name'] for amenity in data['ammenities']])
        link = f'{os.getenv("FRONT_HOST")}/travel-assistant/hotels/{hotelId}?townId={townId}&checkin={payload["checkin"]}&checkout={payload["checkout"]}&rooms=[{{"adults":{payload["rooms"][0]["adults"]},"children":{payload["rooms"][0]["children"]},"infants":{payload["rooms"][0]["infants"]},"ages":{payload["rooms"][0]["ages"]}}}]'
        result += f'Hotel ID: {hotelId}\n'
        result += f'Hotel Name: {hotelName}\n'
        result += f'Hotel Stars: {stars}\n'
        result += f'Hotel Address: {hotelAddress}\n'
        result += f'Price: From ${priceFrom} {currency}\n'
        result += f'Click here to see details: {link}\n'
        result += f'(The following information do not show to the user, keep only for you and use it to filter according to users needs)\n'
        result += f'Hotel Category: {data["category"]["name"]}\n'
        result += f'Hotel Ammenities: {ammenities}\n\n'
    return result

def get_data_for_booking(
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
    Get availability of hotels in a given town.

    Args:
    hotelId: The hotel ID.
    townId: The town ID.
    checkin_date (string): The check-in date.
    checkout_date (string): The check-out date.
    adults: The number of adults. Default is 1.
    children: The number of children. Default is 0.
    infants: The number of infants. Default is 0.
    ages: The ages of the children. Default is [].

    Use this function when the user wants to know more information of the hotel
    or has already selected a hotel.

    Returns:
    A list of dictionaries containing the availability of
    one hotel in the given hotel id.

    Example:
    get_availability(hotelId = '196', townId='1234', checkin_date='2022-12-01', checkout_date='2022-12-05', adults=2, children=1)
    """
    url = f'{os.getenv("CTS_API_V1")}/hotel/{hotelId}/'

    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}'}
    currency = 1 if os.getenv('CURRENCY') == 'CLP' else 2
    json = {'townId': townId, 'checkin': checkin_date, 'checkout': checkout_date, 'rooms': [{'adults': adults, 'children': children, 'infants': infants, 'ages': ages}], 'currency': currency}
    response = requests.post(url, json=json, headers=headers)
    result = response.json()
    return result

def get_booking_details(bookingId) -> list[dict]:
    url = f'{os.getenv("CTS_API_V1")}/booking/?showOnlyMyBookings=true'
    ctsToken = os.getenv("CTS_TOKEN")
    headers = {'Authorization': f'token {ctsToken}', 'origin': 'localhost'}
    response = requests.get(url, headers=headers).json()
    response = response['results']
    for booking in response:
        if booking['file_number'] == bookingId:
            result = booking
    return result