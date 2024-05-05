from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
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

# # Home page route
# @app.route('/')
# def home():
#     return render_template('search-flights.html')

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
    
    cursor.execute(query, params)
    flight_details = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(flight_details)

# Here is for register selection choose your type
@app.route('/select_type')
def select_type():
    return render_template('select_type.html')

#Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # 从 select type 里取得
        user_type = request.args.get('type')
        # 根据用户类型渲染注册表单
        return render_template('register.html', type=user_type)
    elif request.method == 'POST':
        # 从表单数据中获取注册信息
        user_type = request.form['type']
        password = request.form['password']
        # 对密码进行加密处理
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # 获取数据库连接
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
        # 根据用户类型，插入相应的数据到数据库
            if user_type == 'BookingAgent':
                email = request.form['email']
                # 先检查数据库里存不存在已注册
                cursor.execute("SELECT * FROM booking_agent WHERE email = %s", (email,))
                #如果已经存在就报错然后闪回原页面，这里做了一个回滚，你可以不用重复输入你已经输入的信息
                if cursor.fetchone() is not None:
                    flash('Email already registered.')
                    return render_template('register.html', type=user_type, form_data=request.form)
                # 输入其他信息
                booking_agent_id = request.form['booking_agent_id']

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO booking_agent (email, password, booking_agent_id) VALUES (%s, %s, %s)",
                    (email, hashed_password, booking_agent_id)
                )

            elif user_type == 'Customer':
                #先检查数据库里存不存在已注册
                cursor.execute("SELECT * FROM customer WHERE email = %s", (email,))
                if cursor.fetchone() is not None:
                    flash('Email already registered.')
                    return render_template('register.html', type=user_type, form_data=request.form)
                #输入其他信息
                email = request.form['email']
                name = request.form['name']
                building_number = request.form['building_number']
                street = request.form['street']
                city = request.form['city']
                state = request.form['state']
                phone_number = request.form['phone_number']
                passport_number = request.form['passport_number']
                passport_expiration = request.form['passport_expiration']
                passport_country = request.form['passport_country']
                date_of_birth = request.form['date_of_birth']

                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO customer (email, name, password, building_number, street, city, state, phone_number, passport_number, passport_expiration, passport_country, date_of_birth) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (email, name, hashed_password, building_number, street, city, state, phone_number, passport_number,
                     passport_expiration, passport_country, date_of_birth)
                )

            elif user_type == 'AirlineStaff':
                username = request.form['username']

                cursor.execute("SELECT * FROM airline_staff WHERE username = %s", (username,))
                if cursor.fetchone() is not None:
                    flash('Username already taken.')
                    return render_template('register.html', type=user_type, form_data=request.form)

                first_name = request.form['first_name']
                last_name = request.form['last_name']
                date_of_birth = request.form['date_of_birth']
                name_airline = request.form['name_airline']
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, name_airline) VALUES (%s, %s, %s, %s, %s, %s)",
                    (username, hashed_password, first_name, last_name, date_of_birth, name_airline)
                )
            # 提交数据库事务
            conn.commit()
        except Exception as e:
            #防止数据库出错
            conn.rollback()
            flash(f'An error occurred: {str(e)}')
            return render_template('register.html', type=user_type, form_data=request.form)

        finally:
            # 关闭数据库连接
            cursor.close()
            conn.close()

        return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def get_db_connection():
    conn = mysql.connect(**db_config)
    return conn
########################login------------------------------------------
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM person WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and bcrypt.check_password_hash(user['password'], password):
            session['username'] = username
            session['user_type'] = user['user_type']
            return redirect(url_for('user_home'))
        else:
            flash('Login Unsuccessful. Please check username and password')
            return redirect(url_for('login'))

    return render_template('login.html')

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

@app.route('/home')
def user_home():
    if 'username' in session:
        user_type = session.get('user_type')
        if user_type == 'Customer':
            return render_template('customer_home.html', username=session['username'])
        elif user_type == 'BookingAgent':
            return render_template('agent_home.html', username=session['username'])
        elif user_type == 'AirlineStaff':
            return render_template('staff_home.html', username=session['username'])
        else:
            return 'User type is unknown.'
    else:
        return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
