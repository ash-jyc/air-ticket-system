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

"""Book a flight

Keyword arguments:
user_id -- user's ID
flight_number -- flight number
customer_email -- customer's email
agent_email -- agent's email
date -- date of booking
"""

@app.route('/search-flights')
def search_flights():
    return render_template('search-flights.html')

# Search flights
@app.route('/api/search-flights', methods=['POST'])
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
    
    user_type = session.get('user_type')

    if user_type == 'Customer':
        flight_number = request.get_json()['flight_number']
        customer_email = session.get('user_id')
        print("customer_email", customer_email)
        
        query = """
            INSERT INTO ticket (flight_num) VALUES (%s)
        """
        cursor.execute(query, (flight_number,))
        
        ticket_id = cursor.lastrowid    
        query = """
            INSERT INTO purchase (ticket_id, customer_email, agent_email, date)
            VALUES (%s, %s, NULL, CURDATE())
        """
        
        cursor.execute(query, (ticket_id, customer_email))
        
    elif user_type == "BookingAgent":
        print("user_type", user_type)
        # check booking agent works for airline
        agent_email = session.get('user_id')
        flight_number = request.get_json()['flight_number']
        
        # get airline name
        query = """
            SELECT f.name_airline
            FROM flight f
            WHERE f.flight_num = %s
        """
        
        cursor.execute(query, (flight_number,))
        airline_name = cursor.fetchone()['name_airline']
        print(airline_name)
        
        query = """
            SELECT b.booking_agent_id
            FROM booking_agent b
            JOIN works_for w ON b.email = w.agent_email
            WHERE b.email = %s AND w.airline_name = %s
        """
        
        cursor.execute(query, (agent_email, airline_name))
        booking_agent_id = cursor.fetchone()
        print(booking_agent_id)
        if not booking_agent_id:
            return jsonify({'error': 'Booking agent does not work for airline'})
                
        return jsonify({'redirect': '/book-with-agent', 'flight_number': flight_number})
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Flight booked successfully!'})

"""Agent booking

Keyword arguments:
user_id -- user's ID
customer_email -- customer's email
flight_number -- flight number
"""

@app.route('/book-with-agent')
def book_with_agent():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    return render_template('book-with-agent.html')

@app.route('/api/book-with-agent', methods=['POST'])
def book_with_agent_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    agent_email = session.get('user_id')
    customer_email = request.get_json()['customer_email']
    flight_number = request.get_json()['flight_number']
    
    query = """
        INSERT INTO ticket (flight_num) VALUES (%s)
    """
    cursor.execute(query, (flight_number,))
    
    ticket_id = cursor.lastrowid
    query = """
        INSERT INTO purchase (ticket_id, customer_email, agent_email, date)
        VALUES (%s, %s, %s, CURDATE())
    """
    cursor.execute(query, (ticket_id, customer_email, agent_email))
    
    print("ticket_id", ticket_id)
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Flight booked successfully!'})

@app.route('/api/booked-flights', methods=['GET'])
def booked_flights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Perform a query to get all flights booked by agent
    agent_email = session.get('user_id')
    query = """
        SELECT f.flight_num, f.status, f.depart_time, f.arrive_time, f.price, b.comission
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        JOIN booking_agent b ON p.agent_email = b.email
        WHERE p.agent_email = %s
    """
    cursor.execute(query, (agent_email,))
    flights = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return jsonify(flights)
    
"""View flight status

Keyword arguments:
flight_number -- flight number
date -- date of departure or arrival
"""

@app.route('/flight-status')
def flight_status():
    return render_template('flight-status.html')

@app.route('/api/flight-status', methods=['POST'])
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

"""Registration and login

Keyword arguments:
type -- user type (Customer, BookingAgent, AirlineStaff)
email -- user's email
password -- user's password
booking_agent_id -- booking agent's ID
other user information...
"""

@app.route('/')
def index():
    return redirect(url_for('select_type'))

@app.route('/select-type')
def select_type():
    return render_template('select-type.html')

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
                email = request.form['email']
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
                'BookingAgent': 'agent_home',
                'AirlineStaff': 'staff_home'
            }.get(user_type, 'home')

            return redirect(url_for(home_page))
        else:
            flash('Login unsuccessful. Please check username and password.')
            return render_template('login.html', type=user_type)

"""User view flights

Keyword arguments:
user_id -- user's ID
"""

@app.route('/api/my-flights', methods=['GET'])
def my_flights_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_name = session.get('user_id')
    
    flights = []
    query = """
        SELECT f.flight_num, f.status, f.depart_time, f.arrive_time, f.price
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s
    """
    
    cursor.execute(query, (user_name,))
    flights = cursor.fetchall()
    print("flights", flights)
    
    return jsonify(flights)

"""User track spending"""
@app.route('/api/track-spending', methods=['GET'])
def track_spending():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_name = session.get('user_id')
    
    query = """
        SELECT SUM(f.price) AS total_spent, MONTH(p.date) AS month, YEAR(p.date) AS year
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.customer_email = %s AND p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        GROUP BY month, year
        ORDER BY year DESC, month DESC
    """
    
    cursor.execute(query, (user_name,))
    spending = cursor.fetchall()
    print("spending", spending)
    formatted_data = [
        {"total_spent": spend['total_spent'], "month": f"{spend['year']}-{spend['month']:02d}"}
        for spend in spending
    ]
    
    return jsonify(formatted_data)

@app.route('/api/track-commission', methods=['POST'])
def track_commission_form():
    
    print(request.form)
    agent_email = session.get('user_id')
    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # commission should be commission * price of tickets sold
    query = """
        SELECT SUM(b.comission * f.price) AS total_commission, COUNT(*) AS total_tickets
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        JOIN booking_agent b ON p.agent_email = b.email
        WHERE p.agent_email = %s AND p.date >= %s AND p.date <= %s
    """
    
    cursor.execute(query, (agent_email, start_date, end_date))
    commission = cursor.fetchone() or {'total_commission': 0, 'total_tickets': 0}
    
    cursor.close()
    conn.close()
    print(commission)
    
    return jsonify(commission)

@app.route('/api/top-customers', methods=['GET'])
def get_top_customers():

    agent_email = session.get('user_id')
    if not agent_email:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()

    # Top 5 customers by tickets purchased
    cursor.execute("""
        SELECT c.email, c.name, COUNT(*) AS tickets_purchased
        FROM customer c
        JOIN purchase p ON c.email = p.customer_email
        WHERE p.agent_email = %s
        GROUP BY c.email
        ORDER BY tickets_purchased DESC
        LIMIT 5
    """, (agent_email,))
    top_tickets = cursor.fetchall()

    # Top 5 customers by commission earned
    cursor.execute("""
        SELECT c.email, c.name, SUM(f.price * b.comission) AS commission_earned
        FROM customer c
        JOIN purchase p ON c.email = p.customer_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num
        JOIN booking_agent b ON p.agent_email = b.email
        WHERE p.agent_email = %s
    """, (agent_email,))
    top_commissions = cursor.fetchall()

    cursor.close()
    conn.close()
    
    print(top_tickets)
    print(top_commissions)

    return jsonify({
        'top_tickets': top_tickets,
        'top_commissions': top_commissions
    })

"""Choose home page

Keyword arguments:
user_type -- user type (Customer, BookingAgent, AirlineStaff)
"""

@app.route('/home')
def home():
    user_type = session.get('user_type')
    if user_type == 'Customer':
        return redirect(url_for('customer_home'))
    elif user_type == 'BookingAgent':
        return redirect(url_for('agent_home'))
    else:
        return redirect(url_for('staff_home'))

@app.route('/customer-home')
def customer_home():
    if 'user_type' in session and session['user_type'] == 'Customer':
        return render_template('customer-home.html')
    return redirect(url_for('login', type='Customer'))

@app.route('/agent-home')
def agent_home():
    if 'user_type' in session and session['user_type'] == 'BookingAgent':
        return render_template('agent-home.html')
    return redirect(url_for('login', type='BookingAgent'))

"""Airline staff

Keyword arguments:
user_id -- user's ID
"""

@app.route('/staff-home')
def staff_home():
    if 'user_type' in session and session['user_type'] == 'AirlineStaff':
        return render_template('staff-home.html')
    return redirect(url_for('login', type='AirlineStaff'))

@app.route('/api/staff-flights', methods=['GET', 'POST'])
def staff_flights():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'GET':
        
        today = 'CURDATE()'
        end_date = 'DATE_ADD(CURDATE(), INTERVAL 30 DAY)' 
        
        query = f"""
            SELECT f.flight_num, f.status, f.depart_time, f.arrive_time, f.price
            FROM flight f
            WHERE f.depart_time >= {today} AND f.depart_time <= {end_date} AND f.name_airline = (
                SELECT name_airline FROM airline_staff WHERE username = %s
            )
        """
        cursor.execute(query, (user_id,))
        flights = cursor.fetchall()
        print(flights)
        return jsonify(flights)
    
    else: 
        start_date = request.get_json()['start_date']
        end_date = request.get_json()['end_date']

        """View My flights: Defaults will be showing all the upcoming flights operated by the airline he/she works for
    the next 30 days. He/she will be able to see all the current/future/past flights operated by the airline he/she
    works for based range of dates, source/destination airports/city etc. He/she will be able to see all the
    customers of a particular flight.
        """
        
        query = """
            SELECT f.flight_num, f.status, f.depart_time, f.arrive_time, f.price
            FROM flight f
            WHERE f.depart_time >= %s AND f.depart_time <= %s AND f.name_airline = (
                SELECT name_airline FROM airline_staff WHERE username = %s
            )
        """
        cursor.execute(query, (start_date, end_date, user_id))
        flights = cursor.fetchall()
        print(flights)

        cursor.close()
        conn.close()
        return jsonify(flights)

if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
