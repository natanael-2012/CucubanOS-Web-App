from flask import Flask, jsonify, request, send_from_directory, render_template
from flask_cors import CORS, cross_origin
import os
from mqtt import *
from dotenv import load_dotenv
from handler.users import *
from handler.buoys import *
from handler.messages import *
import jwt
from handler.users import UserHandler
from hashlib import sha256
from dao.users import UsersDAO



secret_key = os.environ.get('SECRET_KEY')
# Create the application instance
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "https://boyaslacatalana.azurewebsites.net"}})
user_handler = UserHandler()
#user_dao = UsersDAO()

load_dotenv()

port = int(os.environ.get("PORT", 5000))

# Create a URL route in our application for "/"
# @app.route('/')
# def index():
#     return jsonify({"message": "Hello, Personas!"})


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    return response

for key, value in os.environ.items():
    print(f"{key}: {value}")
    

@app.route("/publish", methods=["POST"])
def publish():
    # Retrieve message data from user input
    message = request.form["message"]
    publish_message(message)
    # Display confirmation or handle errors
    return jsonify({"message": "Message sent"}, 200)


@app.route("/subscribe", methods=["GET"])
def subscribe():
    # Retrieve message data from user input
    message = subscribe_message()
    # Display confirmation or handle errors
    return jsonify({"message": message},200)

@app.route("/add-user", methods=["POST"])
@app.route("/add-user/", methods=["POST"])
def add_user():
    user = UserHandler()
    return user.create_user()
    # return create_user()

@app.route("/remove-user/", methods=["DELETE"])
@app.route("/remove-user", methods=["DELETE"])
def remove_user():
    user = UserHandler()
    return user.delete_user()

@app.route("/update-user", methods=["PUT"])
@app.route("/update-user/", methods=["PUT"])
def update_user():
    user = UserHandler()
    return user.update_user()

@app.route("/get-user", methods=["GET"])
@app.route("/get-user/", methods=["GET"])
def get_user():
    user = UserHandler()
    return user.get_user()

@app.route("/get-all-users", methods=["GET"])
@app.route("/get-all-users/", methods=["GET"])
def get_all_users():
    user = UserHandler()
    return user.get_all_users()

@app.route("/forgot-password/", methods=["POST"])
def forgot_password(username):
    
    pass

@app.route("/reset-password", methods=["POST"])
@app.route("/reset-password/", methods=["POST"])
def reset_password():
    pass
    

@app.route("/add-buoy", methods=["POST"])
@app.route("/add-buoy/", methods=["POST"])
def add_buoy():
    buoy = BuoyHandler()
    return buoy.create_buoy()
    
@app.route("/get-one-buoy", methods=["GET"])
@app.route("/get-one-buoy/", methods=["GET"])
def get_one_buoy():
    buoy = BuoyHandler()
    return buoy.get_buoy()

@app.route("/get-buoys/", methods=["GET"])
@app.route("/get-buoys", methods=["GET"])
def get_buoys():
    buoy = BuoyHandler()
    return buoy.get_buoys()


@app.route("/delete-buoy/<string:bname>", methods=["DELETE"])
@app.route("/delete-buoy/<string:bname>/", methods=["DELETE"])
def delete_buoy(bname):
    buoy = BuoyHandler()
    return buoy.delete_buoy(bname)


@app.route("/update-buoy/", methods=["PUT"])
@app.route("/update-buoy", methods=["PUT"])
def update_buoy():
    buoy = BuoyHandler()
    return buoy.update_buoy()


@app.route("/chirpstack-updates", methods=["POST"])
@app.route("/chirpstack-updates/", methods=["POST"])
def chirpstack_updates():
    update = MessageHandler()
    return update.chirpstack_updates()


@app.route("/send-all-buoys-data/", methods=["POST"])
@app.route("/send-all-buoys-data", methods=["POST"])
def send_buoy_data():
    # https://loraserver.tetaneutral.net/api#!/DeviceQueueService/Enqueue
    message = MessageHandler()
    return message.multicast()
    
@app.route("/send-one-buoy-data/", methods=["POST"])
@app.route("/send-one-buoy-data", methods=["POST"])
def send_one_buoy_data():
    message = MessageHandler()
    return message.send_one_buoy_data()

@app.route("/see-multimessage", methods=["GET"])
def see_multimessage():
    message = MessageHandler()
    return message.see_multimessage()

@app.route("/delete-multicast-queue", methods=["DELETE"])
def delete_multicast():
    message = MessageHandler()
    return message.delete_multicast_queue()


# Route to serve index.html
@app.route('/')
def serve_index():
    return send_from_directory('build', 'index.html')

# Route to serve static files
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('build', path)


@app.route("/update-marker-ids", methods=["POST"])
def update_marker_ids():
    try:
        # Extract marker IDs and DevEUIs from the request data
        marker_ids_devEUIs = request.get_json()
        print("Data Recieved:", marker_ids_devEUIs)
        # Check if request data is None or empty
        if marker_ids_devEUIs is None:
            return jsonify({"error": "No JSON data received"}), 400

        # Check if 'markers' key exists and it's a list
        markers_list = marker_ids_devEUIs.get("markers")
        if not isinstance(markers_list, list):
            return jsonify({"error": "Invalid 'markers' format or missing 'markers' key"}), 400
        
        # Process the received marker IDs and DevEUIs
        for marker in markers_list:
            marker_id = marker.get("markerId")
            devEUI = marker.get("devEUI")
            if marker_id is None or devEUI is None:
                return jsonify({"error": "Missing 'markerId' or 'devEUI' in marker data"}), 400
            # Your code to handle the marker ID and DevEUI goes here
            print("Marker ID:", marker_id)
            print("DevEUI:", devEUI)
            
            # Example: Store marker ID and DevEUI in a database

        # Optionally, return a success response
        return jsonify({"message": "Marker IDs received successfully"}), 200

    except ValueError as ve:
        # JSON decoding error
        return jsonify({"error": "Invalid JSON data in the request: " + str(ve)}), 400

    except Exception as e:
        # Return an error response if something goes wrong
        return jsonify({"error": "An unexpected error occurred: " + str(e)}), 500

@app.route('/deploy', methods=['POST'])
def deploy():
    print("Deploy function called")

    message = MessageHandler()
    return message.deploy_buoy()

    # data = request.json
    
    # # Define the desired order of keys
    # ordered_keys = ['selectedColorNum', 'selectedPatternNum', 'brightnessLevel', 'selectedFrequencyNum']

    # # Create a new dictionary with keys in the desired order
    # ordered_data = {key: data.get(key) for key in ordered_keys}

    # # Process the received data
    # selectedColorNum = ordered_data.get('selectedColorNum')
    # selectedPatternNum = ordered_data.get('selectedPatternNum')
    # brightnessLevel = ordered_data.get('brightnessLevel')
    # selectedFrequencyNum = ordered_data.get('selectedFrequencyNum')

    # # Here you can process the received data further

    # # Return the processed data
    # response_data = {
    #     'selectedColorNum': selectedColorNum,
    #     'selectedPatternNum': selectedPatternNum,
    #     'brightnessLevel': brightnessLevel,
    #     'selectedFrequencyNum': selectedFrequencyNum,
    # }

    # return jsonify(response_data), 200

@app.route("/verify-password", methods=["GET"])
def verify_password():
    return user_handler.verify_password()


@app.route("/update-password", methods=["PUT"])
def update_password():
    data = request.get_json()
    email = data.get('email')
    current_password = data.get('currentPassword')
    new_password = data.get('newPassword')
    
    # Check if new_password is not null
    if new_password is None:
        return jsonify({"error": "New password cannot be null"}), 400
    
    # Initialize UsersDAO within the route function
    user_dao = UsersDAO()
    
    try:
        # Assuming user_dao.update_password returns True on success and False on failure
        success = user_dao.update_password(email, new_password)
        
        if success:
            return jsonify({"message": "Password updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update password"}), 500
    finally:
        # Close the database connection after using it
        user_dao.close_connection()

    
failed_login_attempts = {}



@app.route('/login', methods=['POST'])
def login():
    try:
        # Define MAX_LOGIN_ATTEMPTS here
        MAX_LOGIN_ATTEMPTS = 10
        
        # Get the email and password from the request body
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Check if email and password are provided
        if not email or not password:
            return jsonify({'message': 'Email and password are required.'}), 400

        # Connect to the PostgreSQL database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Execute a SQL query to authenticate the user
        cursor.execute("SELECT * FROM users WHERE email = %s AND password = %s", (email, password))
        user = cursor.fetchone()

        if user:
            # Reset failed login attempts for this user
            failed_login_attempts.pop(email, None)

            # Generate JWT token
            token = jwt.encode({'email': email}, secret_key, algorithm='HS256')

            print("Generated Token:", token)
            return jsonify({'token': token}), 200
        else:
            # Increment failed login attempts counter for this user
            failed_attempts = failed_login_attempts.get(email, 0) + 1
            failed_login_attempts[email] = failed_attempts

            # Log the number of failed login attempts for this user
            print(f"Failed login attempts for {email}: {failed_attempts}")

            # Check if the user has exceeded the maximum attempts
            if failed_attempts >= MAX_LOGIN_ATTEMPTS:
                return jsonify({'message': 'You have been locked due to failed login attempts. Please try again in 5 minutes.'}), 401
            else:
                return jsonify({'message': 'Invalid email or password.'}), 401
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

if __name__ == '__main__':
    if debugging:
        #connect_mqtt()
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port = port)
        