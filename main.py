from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

client = MongoClient('mongodb+srv://<username>:<password><cluster>.hgdvwnw.mongodb.net/?retryWrites=true&w=majority')

db = client["mydatabase"]
doctors_collection = db["doctors"]
appointments_collection = db["appointments"]

# Endpoint to create a new doctor
@app.route('/doctors', methods=['POST'])
def create_doctor():
    data = request.get_json()
    doctor = {
        "name": data['name'],
        "location": data['location'],
        "max_patients": data['max_patients']
    }
    doctors_collection.insert_one(doctor)
    return jsonify({"message": "Doctor created successfully"}), 201

# Endpoint to create a new appointment
# Endpoint to create a new appointment
# Endpoint to create a new appointment
@app.route('/appointments', methods=['POST'])
def create_appointment():
    data = request.get_json()
    doctor_name = data.get('doctor_name')

    # Find the doctor by name
    doctor = doctors_collection.find_one({"name": doctor_name})

    if not doctor:
        return jsonify({"error": "Doctor not found"}), 404

    # Check if the maximum appointments for this time slot have been reached
    max_patients = doctor['max_patients']
    existing_appointments = appointments_collection.count_documents({
        "doctor_id": doctor['_id'],
        "day": data['day'],
        "time": data['time']
    })

    if existing_appointments >= max_patients:
        # Suggest an alternative date and time
        return jsonify({"error": "Appointment slot is full. Please choose another date and time."}), 400

    # If not full, create the appointment
    appointments_collection.insert_one({
        "doctor_id": doctor['_id'],
        "day": data['day'],
        "time": data['time']
    })

    return jsonify({"message": "Appointment created successfully"}), 201


# Endpoint to find available doctors
@app.route('/available_doctors', methods=['POST'])
def find_available_doctors():
    data = request.get_json()
    location = data['location']
    day = data['day']
    time = data['time']

    available_doctors = doctors_collection.find({
        "location": location,
        "max_patients": {"$gt": appointments_collection.count_documents({"day": day, "time": time})}
    })

    return jsonify({
        "available_doctors": [doctor['name'] for doctor in available_doctors]
    })

if __name__ == '__main__':
    app.run(debug=True)
