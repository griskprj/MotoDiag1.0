from flask import Blueprint, render_template, redirect, url_for, jsonify, current_app, request
from flask_login import login_required, current_user
import requests

main_bp = Blueprint('main_bp', __name__)


@main_bp.route('/')
def main():
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.index'))
    else:
        return redirect(url_for('auth_bp.login'))

@main_bp.route('/index')
@login_required
def index():
    user = current_user

    return render_template('dashboard.html', user=user)

@main_bp.route('/get_weather')
def get_weather():
    api_key = current_app.config['WEATHER_API_KEY']
    city = request.args.get('city', 'Sochi')
    
    try:
        url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=ru"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        weather = {
            'temp': data['current']['temp_c'],
            'condition': data['current']['condition']['text'],
            'icon': data['current']['condition']['icon'],
            'humidity': data['current']['humidity'],
            'wind': data['current']['wind_kph'],
            'city': data['location']['name']
        }
        return jsonify(weather)
    except Exception as e:
        return jsonify({'error': str(e)}), 500