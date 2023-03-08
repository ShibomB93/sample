import random
import string
import time
import redis
from flask import Flask, jsonify, request

app = Flask(__name__)
cache = redis.Redis(host='localhost', port=6379)

# Generate a random string of characters for OTP
def generate_otp(length):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# Generate and store OTP in cache for validation
@app.route('/generate_otp', methods=['POST'])
def generate_and_store_otp():
    try:
        # Get request data
        data = request.get_json()
        user_id = data['user_id']
        
        # Generate OTP and store in cache for 5 minutes
        otp = generate_otp(6)
        cache.set(user_id, otp, ex=300)
        
        # Return response with OTP
        return jsonify({'status': 'success', 'otp': otp})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

# Validate OTP from cache
@app.route('/validate_otp', methods=['POST'])
def validate_otp():
    try:
        # Get request data
        data = request.get_json()
        user_id = data['user_id']
        otp = data['otp']
        
        # Get OTP from cache
        stored_otp = cache.get(user_id)
        if stored_otp is None:
            return jsonify({'status': 'error', 'message': 'OTP not found'})
        
        # Compare OTPs
        if otp != stored_otp.decode('utf-8'):
            return jsonify({'status': 'error', 'message': 'OTP does not match'})
        
        # Delete OTP from cache
        cache.delete(user_id)
        
        # Return response with success status
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    
if __name__ == '__main__':
    app.run(debug=True)
