import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from smartcar.exceptions import AuthenticationException
from flask_cors import CORS
import os
import json
import sqlite3

#load server secrets
with open("SERVER_SECRET.json", 'r') as f:
    AUTH = json.load(f)

conn = sqlite3.connect("db.sqlite")

# ./main.py
app = Flask(__name__)
CORS(app)
access = None
vehicle = []
current = 0
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
def meth_vehicle():
    # access our global variable to retrieve our access tokens
    global access
    global vehicle
    # the list of vehicle ids

    if access is None:
        return redirect("/login")

    try:
        vehicle_ids = smartcar.get_vehicle_ids(
            access['access_token'])['vehicles']
    except AuthenticationException:
        access = None
        vehicle = []
        return redirect("/login")
        

    info = []
    vehicle_description_tuple = []
    vnum = request.args.get('vehicle_number', default = 0, type = int)
    global current
    current = vnum

    k = 0
    for i in vehicle_ids:
        # instantiate the first vehicle in the vehicle id list
        cur_v = smartcar.Vehicle(i, access['access_token'])
        vehicle.append(cur_v)
        # vehicle info: id, make, model, year
        v_in=vehicle[len(vehicle)-1].info()
        info.append(v_in)
        vehicle_description_tuple.append((k,str(v_in['year'])+" "+v_in['make']+" "+v_in['model']+" ("+cur_v.vin()[-5:]+")"))
        k+=1

    #print(info)
    
    #print("current vehicle = ",vnum)
    # coordinates of current location: lat, long
    coordinates = vehicle[vnum].location()
    lat = coordinates['data']['latitude']
    lon = coordinates['data']['longitude']


    # odometer info in kilometers
    distance = vehicle[vnum].odometer()
    dist_to_miles = round(0.621371 * distance['data']['distance'], 2)
    oil_change_dist = dist_to_miles + 3000
    miles_until_oil_change = oil_change_dist - dist_to_miles

    
    # dictionary of stats from car
    stats = {
        'id' : info[vnum]['id'],
        'make' : info[vnum]['make'],
        'model' : info[vnum]['model'],
        'year' : info[vnum]['year'],
        'total_mileage' : dist_to_miles,
        'oil_miles' : miles_until_oil_change,
        'latitude' : lat,
        'longitude' : lon,
        'vin' : vehicle[vnum].vin(), # vin number
        'vehicle_description_tuple' : vehicle_description_tuple
    }
    #print(stats)

    return render_template("controlcenter.html", stats=stats)

@app.route('/logout')
def log_out():
    global access
    global vehicle
    if(access is not None):
        vehicle[0].disconnect()
        vehicle = []
        access = None
    return redirect("/index")

@app.route('/lockcurvehicle')
def lock_current_vehicle():
    global access
    global vehicle
    global current
    if access is not None and len(vehicle) > 0:
        vehicle[current].lock()
    return redirect('/vehicle')

@app.route('/unlockcurvehicle')
def unlock():
    global access
    global vehicle
    global current
    if access is not None and len(vehicle) > 0:
        vehicle[current].unlock()
    return redirect('/vehicle')


if __name__ == '__main__':
    app.run(port=8000)