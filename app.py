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

# Search flights
@app.route('/search-flights', methods=['POST'])
def search_flights():
    # Connect to the database
    conn =get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Retrieve form data
    source = request.form['source']
    destination = request.form['destination']
    date = request.form['date']

    # Build the SQL query dynamically based on input
    # Build the SQL query dynamically based on input
    query = """
        SELECT flight.flight_number, flight.status, depart.departure_time, arrive.arrival_time
        FROM flight
        JOIN depart ON flight.flight_number = depart.flight_number
        JOIN arrive ON flight.flight_number = arrive.flight_number
        WHERE 1=1
    """
    params = []
    if source:
        query += " AND depart.name = %s"
        params.append(source)
    if destination:
        query += " AND arrive.name = %s"
        params.append(destination)
    if date:
        query += " AND DATE(depart.departure_time) = %s"
        params.append(date)

    # Execute the query
    cursor.execute(query, params)
    flights = cursor.fetchall()

    # Close database connection
    cursor.close()
    conn.close()

    # Respond with JSON
    return jsonify(flights)




# Flight status
@app.route('/flight-status', methods=['POST'])
def flight_status():
    flight_number = request.form['flight_number']
    date = request.form['date']  # This is either the departure or arrival date.
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT flight.flight_number, flight.status, depart.departure_time, arrive.arrival_time
        FROM flight
        JOIN depart ON flight.flight_number = depart.flight_number
        JOIN arrive ON flight.flight_number = arrive.flight_number
        WHERE flight.flight_number = %s AND DATE(depart.departure_time) = %s
    """
    cursor.execute(query, (flight_number, date))
    flight_details = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('flight-status.html', flight_details=flight_details)

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
    if request.method == 'POST':
        # Implement login logic
        pass
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)
