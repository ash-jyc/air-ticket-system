from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
import mysql.connector as mysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'
bcrypt = Bcrypt(app)

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'port': 3307,
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
@app.route('/search-flights', methods=['POST'])
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
        SELECT f.flight_number, f.status, d.departure_time, a.arrival_time
        FROM flight f
        JOIN depart d ON f.flight_number = d.flight_number
        JOIN arrive a ON f.flight_number = a.flight_number
        WHERE 1=1
    """
    params = []
    if source:
        query += " AND d.name = %s"
        params.append(source)
    if destination:
        query += " AND a.name = %s"
        params.append(destination)
    if date:
        query += " AND DATE(d.departure_time) = %s"
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
@app.route('/flight-status')
def flight_status():
    return render_template('flight-status.html')

@app.route('/flight-status', methods=['POST'])
def flight_status_form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    flight_number = request.form['flight_number']
    date = request.form['date']  # This is either the departure or arrival date.
    
    query = """
        SELECT f.flight_number, f.status, d.departure_time, a.arrival_time
        FROM flight f
        JOIN depart d ON f.flight_number = d.flight_number
        JOIN arrive a ON f.flight_number = a.flight_number
        WHERE 1=1
    """
    
    params = []
    if date:
        query += " AND (DATE(d.departure_time) = %s OR DATE(a.arrival_time) = %s)"
        params.append(date)
    if flight_number:
        query += " AND f.flight_number = %s"
        params.append(flight_number)
    
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
        user_type = request.args.get('type', 'Customer')  # Default to Customer if not specified
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM airline")
        airlines = cursor.fetchall()
        #print(airlines)  # Check what is being returned from the database
        cursor.close()
        conn.close()
        airlines = [{'name': airline[0]} for airline in airlines]
        # Render the registration form with the list of airlines
        return render_template('register.html', type=user_type, airlines=airlines)
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
                email = request.form['email']
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

                try:

                    # Insert new airline staff into the database
                    cursor.execute(
                        "INSERT INTO airline_staff (username, password, first_name, last_name, date_of_birth, name_airline) VALUES (%s, %s, %s, %s, %s, %s)",
                        (username, hashed_password, first_name, last_name, date_of_birth, name_airline)
                    )
                    # Default permission_id for new staff is 1 (where is_operator and is_admin are both set to 0)
                    cursor.execute(
                        "INSERT INTO have_permission (username, permission_id) VALUES (%s, %s)",
                        (username, 1)
                    )

                    # Commit the transaction
                    conn.commit()
                except Exception as e:
                    # Rollback in case of error
                    conn.rollback()

                    flash(f'An error occurred: {str(e)}')

                    return render_template('register.html', type=user_type, form_data=request.form)

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

########################login------------------------------------------
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        user_type = request.args.get('type', 'Customer')  # 默认为 Customer，如果没有提供类型
        return render_template('login.html', type=user_type)
    elif request.method == 'POST':
        user_type = request.form['type']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 根据用户类型选择正确的数据库表，并查询
        if user_type == 'AirlineStaff':
            username = request.form['username']
            cursor.execute("SELECT * FROM airline_staff WHERE username = %s", (username,))
            user = cursor.fetchone()
            user_key = 'username'  # 主键是 username
        else:
            email = request.form['email']
            table = 'booking_agent' if user_type == 'BookingAgent' else 'customer'
            cursor.execute(f"SELECT * FROM {table} WHERE email = %s", (email,))
            user = cursor.fetchone()
            user_key = 'email'  # 主键是 email

        cursor.close()
        conn.close()

        # 检查用户是否存在且密码是否正确
        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = user[user_key]  # 使用数据库中的主键作为用户ID
            session['user_type'] = user_type

            # 根据用户类型重定向到不同的主页
            home_page = {
                'Customer': 'customer_home',
                'BookingAgent': 'bookingagent_home',
                'AirlineStaff': 'airlinestaff_home'
            }.get(user_type, 'home')

            return redirect(url_for(home_page))
        else:
            flash('Login unsuccessful. Please check username and password.')
            return render_template('login.html', type=user_type)


##############------------------------Users
#@app.route('/user_home', methods=['GET'])
@app.route('/customer_home')
def customer_home():
    if 'user_type' in session and session['user_type'] == 'Customer':
        return render_template('customer_home.html')
    return redirect(url_for('login', type='Customer'))

@app.route('/bookingagent_home')
def bookingagent_home():
    if 'user_type' in session and session['user_type'] == 'BookingAgent':
        return render_template('booking_agent_home.html')
    return redirect(url_for('login', type='BookingAgent'))

if __name__ == '__main__':
    app.run(debug=True)
