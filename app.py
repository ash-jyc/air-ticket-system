from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_bcrypt import Bcrypt
import mysql.connector as mysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'airline',
    'raise_on_warnings': True
}

def get_db_connection():
    conn = mysql.connect(**db_config)
    return conn

# Home page route
@app.route('/')
def home():
    return render_template('search-flights.html')

@app.route('/search-flights')
def search_flights():
    return render_template('search-flights.html')

# Search flights
@app.route('/api-search-flights', methods=['POST'])
def search_flights_form():
    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve form data
    source = request.form['source']
    destination = request.form['destination']
    date = request.form['date']

    # Build the SQL query dynamically based on input
    query = """
        SELECT f.flight_num, f.status, f.depart_time, f.arrive_time
        FROM flight f
        WHERE 1=1
    """
    params = []
    if source:
        query += " AND f.depart_airport = %s"
        params.append(source)
    if destination:
        query += " AND f.arrive_airport = %s"
        params.append(destination)
    if date:
        query += " AND DATE(f.depart_time) = %s"
        params.append(date)

    # Execute the query
    cursor.execute(query, params)
    flights = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Respond with JSON
    print(flights)
    return jsonify(flights)

@app.route('/book-flight', methods=['POST'])
def book_flight():
    user_id = session.get('user_id')
    if not user_id:  
        return redirect(url_for('login'))
    
    print("user_id", user_id)
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    flight_number = request.get_json()['flight_number']
    query = """
        INSERT INTO ticket (ticket_id, flight_num)
        VALUES (%s, %s)
    """
    
    cursor.execute(query, (5, flight_number))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Flight booked successfully!'})

# Flight status
@app.route('/flight-status')
def flight_status():
    return render_template('flight-status.html')

@app.route('/api-flight-status', methods=['POST'])
def flight_status_form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    flight_number = request.form['flight_number']
    date = request.form['date']  # This is either the departure or arrival date.
    
    query = """
        SELECT f.flight_num, f.status, f.depart_time, f.arrive_time
        FROM flight f
        WHERE f.flight_num = %s AND (DATE(f.depart_time) = %s)
    """
    
    cursor.execute(query, (flight_number, date))
    flight_details = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(flight_details)

# Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Implement registration logic
        pass
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    # default allow for book flight testing
    session['user_id'] = '001'
    return redirect(url_for('home'))

# View user's flights
@app.route('/my-flights')
def my_flights():
    return render_template('my-flights.html')

@app.route('/api-my-flights', methods=['GET'])
def my_flights_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    flights = []
    query = """
        SELECT f.flight_num, f.status, f.depart_time, f.arrive_time
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        WHERE t.ticket_id = %s
    """
    
    cursor.execute(query, (user_id,))
    flights = cursor.fetchall()
    print("flights", flights)
    
    return jsonify(flights)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
