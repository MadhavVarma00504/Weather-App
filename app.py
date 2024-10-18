from flask import Flask, render_template, request
import requests
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression

app = Flask(__name__)

# OpenWeatherMap API key
API_KEY = "514afbd1e5d3e60fd7f9f922a80a6ca8"

# Load or create the model for predicting future weather (Temperature Prediction)
try:
    model = joblib.load('weather_model.joblib')
except FileNotFoundError:
    # If model doesn't exist, create a dummy model (replace with a real model)
    model = LinearRegression()
    # Example data: [hour of the day, current temp] -> next hour temp
    X = np.array([[1, 15], [2, 16], [3, 14], [4, 13], [5, 13], [6, 14]])  # Dummy input features
    y = np.array([16, 15, 13, 12, 12, 13])  # Dummy target (temperature next hour)
    model.fit(X, y)
    joblib.dump(model, 'weather_model.joblib')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        error_message = "There was an error fetching the data. Please try again."
        return render_template('index.html', error=error_message)
    
    if response.status_code == 200:
        current_temp = data['main']['temp']
        weather = {
            'city': city,
            'temperature': current_temp,
            'description': data['weather'][0]['description'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'icon': data['weather'][0]['icon']
        }
        
        # Predict future temperature using the ML model
        hour_of_day = int(data['dt'] % 86400 // 3600)  # Get the current hour
        future_temp = model.predict([[hour_of_day, current_temp]])[0]  # Predict next hour temperature

        # Pass both current weather and future temperature prediction to the template
        return render_template('weather.html', weather=weather, future_temp=future_temp)
    else:
        error_message = "City not found, please try again."
        return render_template('index.html', error=error_message)

if __name__ == '__main__':
    app.run(debug=True)
