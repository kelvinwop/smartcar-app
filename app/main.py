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
# TODO: Authorization Step 1a: Launch Smartcar authentication dialog
client = smartcar.AuthClient(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    redirect_uri=os.environ.get('REDIRECT_URI'),
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
    return 'Hello', 200

@app.route('/vehicle', methods=['GET'])
def vehicle():
    # access our global variable to retrieve our access tokens
    global access
    # the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    info = vehicle.info()
    #coordinates of current location
    coordinates = vehicle.location()
    lat = coordinates['data']['latitude']
    lon = coordinates['data']['longitude']

    #odometer on kilometers
    mileage = vehicle.odometer()
    oilChangemiles = mileage['data']['distance'] + 3000
    miles_UntilOil_Change = 0.621*(oilChangemiles - mileage['data']['distance'])
    mileageOriginal = mileage['data']['distance']*0.621
    

    #dictionary with stats from car
    stats = {
        "id":info['id'],
        "Make":info['make'],
        "Model":info['model'],
        "Year":info['year'],
        "Mileage":mileageOriginal,
        "OilMiles": miles_UntilOil_Change,
        "latitude":lat,
        "longitude":lon,
    }


    print(info)

    return 'succesfully completed'
    return render_template("controlcenter.html", stats=stats)

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