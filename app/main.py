import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS
import os
import json

#load server secrets
with open("SERVER_SECRET.json", 'r') as f:
    AUTH = json.load(f)

# ./main.py
app = Flask(__name__)
CORS(app)
access = None
vehicle = None
# TODO: Authorization Step 1a: Launch Smartcar authentication dialog
client = smartcar.AuthClient(
    client_id=AUTH["CLIENT_ID"],
    client_secret=AUTH["CLIENT_SECRET"],
    redirect_uri=AUTH["REDIRECT_URI"],
    scope=[
        'read_vehicle_info',
        'read_location',
        'read_odometer',
        'control_security',
        'read_vin',
      ],
    test_mode=True,
)
'''@app.route('usersApp')
def mainPage():
    return render_template()'''
'''def logOut():'''

@app.route('/')
@app.route('/index')
def home():
    return render_template("index.html")


@app.route('/login', methods=['GET'])
def login():
    # TODO: Authorization Step 1b: Launch Smartcar authentication dialog
    auth_url = client.get_auth_url()
    return redirect(auth_url)

@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')

    # access our global variable and store our access tokens
    global access
    # in a production app you'll want to store this in some kind of
    # persistent storage
    access = client.exchange_code(code)
    return redirect("/vehicle")

@app.route('/vehicle', methods=['GET'])
def vehicle():
    # access our global variable to retrieve our access tokens
    global access
    global vehicle
    # the list of vehicle ids
    try:
        vehicle_ids = smartcar.get_vehicle_ids(
            access['access_token'])['vehicles']
        print("access successful")
    except TypeError as ex:
        print(ex)
        return redirect("/login")


    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    # vehicle info: id, make, model, year
    info = vehicle.info()

    # coordinates of current location: lat, long
    coordinates = vehicle.location()
    lat = coordinates['data']['latitude']
    lon = coordinates['data']['longitude']

    # odometer info in kilometers
    distance = vehicle.odometer()
    dist_to_miles = round(0.621371 * distance['data']['distance'], 2)
    oil_change_dist = dist_to_miles + 3000
    miles_until_oil_change = oil_change_dist - dist_to_miles

    # dictionary of stats from car
    stats = {
        'id' : info['id'],
        'make' : info['make'],
        'model' : info['model'],
        'year' : info['year'],
        'total_mileage' : dist_to_miles,
        'oil_miles' : miles_until_oil_change,
        'latitude' : lat,
        'longitude' : lon,
        'vin' : vehicle.vin() # vin number
    }

    print()

    print(info)

    return render_template("controlcenter.html", stats=stats)

@app.route('/logout')
def log_out():
    global vehicle
    if(vehicle is not None):
        vehicle.disconnect()
        vehicle = None
    return redirect("/index")

'''
@app.route('/userApp', methods=['GET'])
def userApp():
    global access
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    coordinates = vehicle.location()
    mileage = vehicle.odometer()
    oilChangemiles = mileage + 1560
    milesUntilOil_Change = oilChangemiles - mileage
    
    isLocked = vehicle.lock()
    
    if isLocked == 'success':
        isLocked = 'Locked'
    else:
        isLocked = 'Unlocked'

    stats = {
        "OilMiles": milesUntilOil_Change,
        "lockStatus":isLocked,
    }
    return 'howdy',200'''

if __name__ == '__main__':
    app.run(port=8000)