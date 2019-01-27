import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS

import os

app = Flask(__name__)
CORS(app)

# global variable to save our access_token
access = None

client = smartcar.AuthClient(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    redirect_uri=os.environ.get('REDIRECT_URI'),
    scope=['read_vehicle_info'],
    test_mode=True
)


#home page
@app.route('/')
@app.route('/index')
def home():
    return render_template('index.html')


#Authorization Step 1b: Launch Smartcar authorization dialog
@app.route('/login', methods=['GET'])
def login():
    auth_url = client.get_auth_url()
    return redirect(auth_url)


#Authorization Step 3: Handle Smartcar response
#Request Step 1: Obtain an access token
#
@app.route('/exchange', methods=['GET'])
def exchange():
    code = request.args.get('code')

    # access our global variable and store our access tokens
    global access
    # in a production app you'll want to store this in some kind of
    # persistent storage
    access = client.exchange_code(code)
    return '', 200



#Request Step 2: Get vehicle ids
#Request Step 3: Create a vehicle
#Request Step 4: Make a request to Smartcar API
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
    print(info)

    return jsonify(info)


if __name__ == '__main__':
    app.run(port=8000)
