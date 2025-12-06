from flask import Flask, render_template, request
import pickle
import pandas as pd
import numpy as np

app = Flask(__name__)

with open('models/model.pkl', 'rb') as f:
    model = pickle.load(f)

with open('models/encoders.pkl', 'rb') as f:
    encoders = pickle.load(f)

with open('models/features.pkl', 'rb') as f:
    features = pickle.load(f)

with open('models/info.pkl', 'rb') as f:
    info = pickle.load(f)

@app.route('/')
def home():
    manufacturers = list(encoders['Manufacturer'].classes_)
    models_list = list(encoders['Model'].classes_)
    fuel_types = list(encoders['Fuel type'].classes_)
    
    return render_template('index.html', 
                         manufacturers=manufacturers,
                         models=models_list,
                         fuel_types=fuel_types,
                         r2_score=info['r2_score'],
                         mae=info['mae'])

@app.route('/predict', methods=['POST'])
def predict():
    try:
        manufacturer = request.form['manufacturer']
        car_model = request.form['model']
        engine_size = float(request.form['engine_size'])
        fuel_type = request.form['fuel_type']
        year = int(request.form['year'])
        mileage = int(request.form['mileage'])
        
        # Encode categorical features
        manufacturer_encoded = encoders['Manufacturer'].transform([manufacturer])[0]
        model_encoded = encoders['Model'].transform([car_model])[0]
        fuel_encoded = encoders['Fuel type'].transform([fuel_type])[0]
        
        # Engineer features
        current_year = 2025
        vehicle_age = current_year - year
        mileage_per_year = mileage / (vehicle_age + 1) if vehicle_age >= 0 else 0
        
        # Create input data with all features (must match training order)
        input_data = pd.DataFrame([[manufacturer_encoded, model_encoded, engine_size, 
                                   fuel_encoded, year, mileage, vehicle_age, mileage_per_year]], 
                                 columns=features)
        
        prediction = model.predict(input_data)[0]
        
        return render_template('index.html',
                             manufacturers=list(encoders['Manufacturer'].classes_),
                             models=list(encoders['Model'].classes_),
                             fuel_types=list(encoders['Fuel type'].classes_),
                             r2_score=info['r2_score'],
                             mae=info['mae'],
                             prediction=f"${prediction:,.2f}",
                             input_data={
                                 'manufacturer': manufacturer,
                                 'model': car_model,
                                 'engine_size': engine_size,
                                 'fuel_type': fuel_type,
                                 'year': year,
                                 'mileage': mileage
                             })
    except Exception as e:
        return render_template('index.html',
                             manufacturers=list(encoders['Manufacturer'].classes_),
                             models=list(encoders['Model'].classes_),
                             fuel_types=list(encoders['Fuel type'].classes_),
                             r2_score=info['r2_score'],
                             mae=info['mae'],
                             error=str(e))

if __name__ == '__main__':
    app.run(debug=True)
