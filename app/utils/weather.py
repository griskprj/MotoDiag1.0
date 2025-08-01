import requests
from app.config import WEATHER_API_KEY, WEATHER_API_URL

def get_current_weather(location='auto:ip'):
    try:
        params = {
            'key': WEATHER_API_KEY,
            'q': location,
            'lang': 'ru'
        }
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        return {
            'temp': f"{data['current']['temp_c']}°C",
            'condition': data['current']['condition']['text'],
            'icon': data['current']['condition']['icon'],
            'advice': get_weather_advice(data['current']['temp_c'], data['current']['condition']['code'])
        }
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None
    
def get_weather_advice(temp, condition_code):
    if temp < 5:
        return "Очень холодно, оденьтесь потеплее"
    elif temp < 15:
        return "Прохладно, возьмите ветровку"
    elif temp < 25:
        return "Отличная погода для поездки"
    else:
        return "Жарко, не забудьте воду"