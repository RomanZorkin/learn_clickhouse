import requests
from service.config import config


def find_location(ip_address: str) -> str:
    response = requests.get(f"https://api.ipregistry.co/{ip_address}?key={config['API_IP_KEY']}")
    if response.status_code == 404:
        return 'Not found'
    result = response.json()
    if not result.get('ip'):
        return 'Not found'
    return result['location']['country']['name']


def find_location_2(ip_address: str) -> str:
    response = requests.get(f'http://ip-api.com/json/{ip_address}?lang=en')
    if response.status_code == 404:
        return 'Not found'
    try:
        result = response.json()
    except: # JSONDecodeError
        return 'Not found'
    if result['status'] == 'fail':
        return 'Not found'
    return result['country']
