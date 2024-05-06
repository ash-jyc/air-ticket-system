from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
from flask_bcrypt import Bcrypt
import mysql.connector as mysql
from datetime import datetime, timedelta

### SETUP ###
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

### LOGIN AND REGISTRATION ###
## Index
@app.route('/')
def index():
    return redirect(url_for('search_flights'))

## Select user type
@app.route('/select-type')
def select_type():
    return render_template('select-type.html')

## Registration
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

## Login
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
                'AirlineStaff': 'airlinestaff_home'
            }.get(user_type, 'home')

            return redirect(url_for(home_page))
        else:
            flash('Login unsuccessful. Please check username and password.')
            return render_template('login.html', type=user_type)

## Logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_type', None)
    return redirect(url_for('index'))

## Choose home page based on user type
@app.route('/home')
def home():
    user_type = session.get('user_type')
    if user_type == 'Customer':
        return redirect(url_for('customer_home'))
    elif user_type == 'BookingAgent':
        return redirect(url_for('agent_home'))
    else:
        return redirect(url_for('airlinestaff_home'))

### PUBLIC ROUTES ###
## Search flights
@app.route('/search-flights')
def search_flights():
    return render_template('search-flights.html')

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

## Book flight
@app.route('/api/book-flight', methods=['POST'])
def book_flight():
    user_id = session.get('user_id')
    print(user_id)
    if not user_id:
        return jsonify({'redirect': '/select-type', 'message': 'Please log in to book a flight'})
    
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
                
        return jsonify({'redirect': '/book-with-agent?flight_number=' + flight_number})
    
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'message': 'Flight booked successfully!'})

## Flight status
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

### CUSTOMER ROUTES ###
## CUSTOMER - home
@app.route('/customer-home')
def customer_home():
    if 'user_type' in session and session['user_type'] == 'Customer':
        return render_template('customer-home.html')
    return redirect(url_for('login', type='Customer'))

## CUSTOMER - view my flights
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

## CUSTOMER - track my spending
@app.route('/api/track-spending', methods=['GET'])
def track_spending():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='Customer'))
    
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

### AGENT ROUTES ###
## AGENT - home
@app.route('/agent-home')
def agent_home():
    if 'user_type' in session and session['user_type'] == 'BookingAgent':
        return render_template('agent-home.html')
    return redirect(url_for('login', type='BookingAgent'))

## AGENT - track my commission
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

## AGENT - top customers
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

## AGENT - book flight
@app.route('/book-with-agent')
def book_with_agent():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='BookingAgent'))
    
    return render_template('book-with-agent.html')

@app.route('/api/book-with-agent', methods=['POST'])
def book_with_agent_form():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='BookingAgent'))
    
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

## AGENT - view booked flights
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

### STAFF ROUTES ###
## STAFF - home
# @app.route('/staff-home')
# def staff_home():
#     if 'user_type' in session and session['user_type'] == 'AirlineStaff':
#         return render_template('staff-home.html')
#     return redirect(url_for('login', type='AirlineStaff'))

#===================Airline Staff，绝妙是不仅在homepage把不属于你权限的botton unavailable了
# ，为了防止你直接跳过这个输入网址进入后面的功能，我还对每个功能的page做了warning

def user_has_admin_permission(username):
    """这个验证是否具有admin权限"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查找用户的权限ID
    cursor.execute("SELECT permission_id FROM have_permission WHERE username = %s", (username,))
    permission_id = cursor.fetchone()

    if permission_id:
        # 检查权限ID是否对应于Admin
        cursor.execute("SELECT is_admin FROM permission WHERE permission_id = %s", (permission_id[0],))
        is_admin = cursor.fetchone()

        cursor.close()
        conn.close()

        return is_admin[0] == 1

    cursor.close()
    conn.close()
    return False

def user_has_operator_permission(username):
    """这个验证是否具有operate权限"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 查找用户的权限ID
    cursor.execute("SELECT permission_id FROM have_permission WHERE username = %s", (username,))
    permission_id = cursor.fetchone()

    if permission_id:
        # 检查权限ID是否对应operator
        cursor.execute("SELECT is_operator FROM permission WHERE permission_id = %s", (permission_id[0],))
        is_operator = cursor.fetchone()

        cursor.close()
        conn.close()

        return is_operator[0] == 1

    cursor.close()
    conn.close()
    return False

@app.route('/show_message_before_redirect')
def show_message_before_redirect():
    return render_template('message_before_redirect.html')

#==================任务1 and homepage
@app.route('/airlinestaff_home', methods=['GET', 'POST'])
def airlinestaff_home():

    if 'user_type' in session and session['user_type'] == 'AirlineStaff':
        if request.method == 'POST' and request.form.get('logout_button'):
            logout()  # 调用注销函数执行注销操作


        username = session['user_id']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        can_create_flight = user_has_admin_permission(username)
        can_add_airplane = user_has_admin_permission(username)
        can_add_airport = user_has_admin_permission(username)
        can_grant_permissions = user_has_admin_permission(username)
        can_add_booking_agent = user_has_admin_permission(username)
        can_change_status = user_has_operator_permission(username)

        # 提供默认日期或从表单接收
        start_date = request.args.get('start_date', datetime.now().strftime('%Y-%m-%d'))
        end_date = request.args.get('end_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
        source_airport = request.args.get('source_airport', '%')
        destination_airport = request.args.get('destination_airport', '%')

        # SQL 查询以获取航班信息
        cursor.execute("""
            SELECT f.flight_num, f.depart_time, f.arrive_time, f.depart_airport, f.arrive_airport, f.status
            FROM flight f
            JOIN airline_staff s ON f.name_airline = s.name_airline
            WHERE s.username = %s AND 
                  f.depart_time BETWEEN %s AND %s AND 
                  f.depart_airport LIKE %s AND 
                  f.arrive_airport LIKE %s
            ORDER BY f.depart_time
        """, (username, start_date, end_date, source_airport, destination_airport))
        flights = cursor.fetchall()

        # 检查是否请求查看特定航班的乘客
        flight_num = request.args.get('flight_num')
        customers = []
        if flight_num:
            cursor.execute("""
                SELECT p.customer_email, p.ticket_id
                FROM purchase p
                JOIN ticket t ON p.ticket_id = t.ticket_id
                WHERE t.flight_num = %s
            """, (flight_num,))
            customers = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('airline_staff_home.html', flights=flights, customers=customers,
                               can_create_flight=can_create_flight, can_add_airplane=can_add_airplane,
                               can_add_airport=can_add_airport, can_grant_permissions=can_grant_permissions,
                               can_add_booking_agent=can_add_booking_agent, can_change_status=can_change_status,
                               selected_flight=flight_num, start_date=start_date, end_date=end_date,
                               source_airport=source_airport, destination_airport=destination_airport)
    else:
        return redirect(url_for('login', type='AirlineStaff'))



#这里开始任务2

@app.route('/airlinestaff_home/create_flight', methods=['GET', 'POST'])
def create_flight():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))

    username = session['user_id']
    if not user_has_admin_permission(username):
        flash("You do not have the necessary permissions to perform this action.", 'error')
        return redirect(url_for('airlinestaff_home'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the airline name for the logged-in user
        cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (username,))
        user_airline = cursor.fetchone()['name_airline']

        if request.method == 'GET':
            # Fetch airports data
            cursor.execute("SELECT name FROM airport")
            airports = cursor.fetchall()
            # Fetch airplanes only from the user's airline
            cursor.execute("SELECT id, name_airline FROM airplane WHERE name_airline = %s", (user_airline,))
            airplanes = cursor.fetchall()
            # Fetch statuses for dropdown
            cursor.execute("SELECT DISTINCT status FROM flight")
            statuses = cursor.fetchall()

            return render_template('create_flight.html', user_airline=user_airline, airports=airports, airplanes=airplanes, statuses=statuses)

        elif request.method == 'POST':
            flight_num = request.form['flight_num']
            depart_time = request.form['depart_time']
            arrive_time = request.form['arrive_time']
            depart_airport = request.form['depart_airport']
            arrive_airport = request.form['arrive_airport']
            plane_id = request.form['plane_id']
            price = request.form['price']
            status = request.form['status']

            # Fetch the airline owning the airplane
            cursor.execute("SELECT name_airline FROM airplane WHERE id = %s", (plane_id,))
            name_airplane_airline = cursor.fetchone()['name_airline']

            # Insert the new flight, using the user's airline for the airline operating the flight
            cursor.execute("""
                INSERT INTO flight (flight_num, name_airline, depart_time, arrive_time, depart_airport, arrive_airport, plane_id, name_airplane_airline, price, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (flight_num, user_airline, depart_time, arrive_time, depart_airport, arrive_airport, plane_id, name_airplane_airline, price, status))
            conn.commit()
            flash("Flight created successfully!", 'success')
            return redirect(url_for('show_message_before_redirect'))

    finally:
        cursor.close()
        conn.close()



#=========================================================

#============================任务3
@app.route('/airlinestaff_home/change_flight_status', methods=['GET', 'POST'])
def change_flight_status():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))

    username = session['user_id']
    if not user_has_operator_permission(username):
        flash("You do not have the necessary permissions to perform this action.", 'error')
        return redirect(url_for('show_message_before_redirect'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch the airline name for the logged-in user
        cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (username,))
        user_airline = cursor.fetchone()['name_airline']

        if request.method == 'GET':
            # Fetch only the flights of the user's airline
            cursor.execute("SELECT flight_num, status FROM flight WHERE name_airline = %s", (user_airline,))
            flights = cursor.fetchall()
            return render_template('change_flight_status.html', flights=flights)

        elif request.method == 'POST':
            flight_num = request.form['flight_num']
            new_status = request.form['status']

            # Verify that the flight to update is from the user's airline before updating
            cursor.execute("SELECT name_airline FROM flight WHERE flight_num = %s", (flight_num,))
            flight = cursor.fetchone()
            if flight and flight['name_airline'] == user_airline:
                cursor.execute("UPDATE flight SET status = %s WHERE flight_num = %s", (new_status, flight_num))
                conn.commit()
                flash("Flight status updated successfully!", 'success')
            else:
                flash("You can only update flights from your own airline.", 'error')

            return redirect(url_for('show_message_before_redirect'))

    finally:
        cursor.close()
        conn.close()


#+==================================任务4
from flask import flash, redirect, url_for, render_template, request

@app.route('/airlinestaff_home/add_airplane', methods=['GET', 'POST'])
def add_airplane():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))

    username = session['user_id']
    if not user_has_admin_permission(username):
        flash("You do not have the necessary permissions to perform this action.", 'error')
        return redirect(url_for('show_message_before_redirect'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (username,))
        user_airline = cursor.fetchone()['name_airline']

        if request.method == 'GET':
            return render_template('add_airplane.html', user_airline=user_airline)

        elif request.method == 'POST':
            airplane_id = request.form['airplane_id']

            # Check if airplane ID already exists in the database
            cursor.execute("SELECT id FROM airplane WHERE id = %s", (airplane_id,))
            if cursor.fetchone():
                flash("This airplane ID already exists!", 'error')
                return render_template('add_airplane.html', user_airline=user_airline)

            cursor.execute("INSERT INTO airplane (id, name_airline) VALUES (%s, %s)", (airplane_id, user_airline))
            conn.commit()
            flash("Airplane added successfully!", 'success')
            return redirect(url_for('confirm_airplanes', user_airline=user_airline))

    finally:
        cursor.close()
        conn.close()



@app.route('/airlinestaff_home/confirm_airplanes')
def confirm_airplanes():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))

    username = session['user_id']
    if not user_has_admin_permission(username):
        flash("You do not have the necessary permissions to perform this action.", 'error')
        return redirect(url_for('show_message_before_redirect'))

    user_airline = request.args.get('user_airline')
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name_airline FROM airplane WHERE name_airline = %s", (user_airline,))
        airplanes = cursor.fetchall()
        return render_template('confirm_airplanes.html', airplanes=airplanes, user_airline=user_airline)
    finally:
        cursor.close()
        conn.close()



@app.route('/airlinestaff_home/add_airport', methods=['GET', 'POST'])
def add_airport():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))
    username = session['user_id']

    if not user_has_admin_permission(username):
        error_message = "You do not have the necessary permissions to perform this action."
        return render_template('show_message_before_redirect.html', error_message=error_message)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        if request.method == 'GET':
            # Render empty form for adding a new airport
            return render_template('add_airport.html', error_message=None)

        elif request.method == 'POST':
            airport_name = request.form['airport_name']
            city = request.form['city']

            # Check if the airport already exists
            cursor.execute("SELECT name FROM airport WHERE name = %s", (airport_name,))
            if cursor.fetchone():
                error_message = "An airport with this name already exists!"
                return render_template('add_airport.html', error_message=error_message)

            # Insert the new airport
            cursor.execute("INSERT INTO airport (name, city) VALUES (%s, %s)", (airport_name, city))
            conn.commit()
            flash("Airport added successfully!", 'success')
            return redirect(url_for('show_message_before_redirect'))

    finally:
        cursor.close()
        conn.close()


@app.route('/airlinestaff_home/view_booking_agents')
def view_booking_agents():
    return redirect(url_for('view_top_agents'))

@app.route('/airlinestaff_home/view_frequent_customers')
def view_frequent_customers():
    return redirect(url_for('view_top_customers'))

@app.route('/airlinestaff_home/revenue_comparison')
def revenue_comparison():
    return redirect(url_for('view_reports'))

@app.route('/airlinestaff_home/view_top_destinations')
def view_top_destinations():
    return render_template('view_top_destinations.html')


@app.route('/airlinestaff_home/grant_permissions', methods=['GET', 'POST'])
def grant_permissions():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        return redirect(url_for('login', type='AirlineStaff'))
    username = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (username,))
        user_airline = cursor.fetchone()['name_airline']

        if not user_has_admin_permission(username):
            flash("You do not have the necessary permissions to perform this action.", 'error')
            return redirect(url_for('show_message_before_redirect'))

        if request.method == 'GET':
            cursor.execute("""
                SELECT username, first_name, last_name 
                FROM airline_staff 
                WHERE name_airline = %s AND username <> %s
            """, (user_airline, username))
            staff_members = cursor.fetchall()

            cursor.execute("SELECT permission_id, is_operator, is_admin FROM permission")
            permissions = cursor.fetchall()

            return render_template('grant_permission.html', staff_members=staff_members, permissions=permissions,
                                   user_airline=user_airline)

        elif request.method == 'POST':
            selected_staff = request.form['selected_staff']
            new_permission_id = request.form['new_permission_id']

            cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (selected_staff,))
            staff_airline = cursor.fetchone()
            if staff_airline['name_airline'] != user_airline:
                flash("Operation failed. You can only modify permissions for staff in your own airline.", 'error')
                return redirect(url_for('show_message_before_redirect'))

            cursor.execute("""
                UPDATE have_permission 
                SET permission_id = %s 
                WHERE username = %s
            """, (new_permission_id, selected_staff))
            conn.commit()
            flash("Permissions updated successfully!", 'success')
            return redirect(url_for('show_message_before_redirect'))

    finally:
        cursor.close()
        conn.close()


@app.route('/airlinestaff_home/add_booking_agent', methods=['GET', 'POST'])
def add_booking_agent():
    if 'user_type' not in session or session['user_type'] != 'AirlineStaff':
        # Redirect if not logged in or not an airline staff
        return redirect(url_for('login', type='AirlineStaff'))

    username = session['user_id']

    # Verify if the logged-in staff has admin permissions
    if not user_has_admin_permission(username):
        flash("You do not have the necessary permissions to perform this action.", 'error')
        return redirect(url_for('show_message_before_redirect'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Fetch the airline name for the logged-in user
        cursor.execute("SELECT name_airline FROM airline_staff WHERE username = %s", (username,))
        user_airline = cursor.fetchone()['name_airline']

        if request.method == 'POST':
            agent_email = request.form['agent_email']

            # Insert into works_for table if the agent exists in the booking_agent table
            cursor.execute("SELECT * FROM booking_agent WHERE email = %s", (agent_email,))
            if cursor.fetchone():
                cursor.execute("INSERT INTO works_for (agent_email, airline_name) VALUES (%s, %s)",
                               (agent_email, user_airline))
                conn.commit()
                flash("Booking agent added successfully!", 'success')
            else:
                flash("No such agent exists.", 'error')

            return redirect(url_for('show_message_before_redirect'))

        return render_template('add_booking_agent.html', user_airline=user_airline)

    finally:
        cursor.close()
        conn.close()


### STAFF - home page view
## STAFF - view flights
@app.route('/api/staff-flights', methods=['GET', 'POST'])
def staff_flights():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))

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

## STAFF - view airline info
@app.route('/view-top-agents')
def view_top_agents():
    return render_template('view-top-agents.html')

## STAFF - view top booking agents
@app.route('/api/top-agents-month', methods=['GET'])
def top_agents_month():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))
    
    # top 5 agents for the past month based off commission
    query = """
        SELECT b.booking_agent_id, b.email, SUM(f.price * b.comission) AS commission_earned
        FROM booking_agent b
        JOIN purchase p ON b.email = p.agent_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND p.date <= CURDATE()
        GROUP BY b.booking_agent_id
        ORDER BY commission_earned DESC
        LIMIT 5
    """
    
    cursor.execute(query)
    top_agents = cursor.fetchall()
    print(top_agents)
    
    cursor.close()
    conn.close()
    return jsonify(top_agents)

@app.route('/api/top-agents-year', methods=['GET'])
def top_agents_year():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))
    
    # top 5 agents for the past month
    query = """
        SELECT b.booking_agent_id, b.email, SUM(f.price * b.comission) AS commission_earned
        FROM booking_agent b
        JOIN purchase p ON b.email = p.agent_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND p.date <= CURDATE()
        GROUP BY b.booking_agent_id
        ORDER BY commission_earned DESC
        LIMIT 5
    """
    
    cursor.execute(query)
    top_agents = cursor.fetchall()
    print(top_agents)
    
    cursor.close()
    conn.close()
    return jsonify(top_agents)

@app.route('/api/top-agents-spec', methods=['POST'])
def top_agents_spec():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))
    
    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    
    print(start_date, end_date)
    # top 5 agents for the past month
    query = """
        SELECT b.booking_agent_id, b.email, SUM(f.price * b.comission) AS commission_earned
        FROM booking_agent b
        JOIN purchase p ON b.email = p.agent_email
        JOIN ticket t ON p.ticket_id = t.ticket_id
        JOIN flight f ON t.flight_num = f.flight_num
        WHERE p.date >= %s AND p.date <= %s
        GROUP BY b.booking_agent_id
        ORDER BY commission_earned DESC
        LIMIT 5
    """
    
    cursor.execute(query, (start_date, end_date))
    top_agents = cursor.fetchall()
    print(top_agents)
    
    cursor.close()
    conn.close()
    return jsonify(top_agents)

## STAFF - view top customers for airline in last year
@app.route('/view-top-customers')
def view_top_customers():
    return render_template('view-top-customers.html')

@app.route('/api/top-customers-year', methods=['GET'])
def top_customers_year():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))
    
    # get airline
    query = """
        SELECT name_airline
        FROM airline_staff
        WHERE username = %s
    """
    
    cursor.execute(query, (user_id,))
    airline_name = cursor.fetchone()['name_airline']
    print(airline_name)
    
    # top 5 customers for the past year
    query = """
        SELECT c.email, c.name, COUNT(*) AS tickets_purchased
        FROM customer c
        JOIN purchase p ON c.email = p.customer_email
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND p.date <= CURDATE() AND p.agent_email IN (
            SELECT email FROM booking_agent WHERE email IN (
                SELECT agent_email FROM works_for WHERE airline_name = %s
            )
        )
        GROUP BY c.email
        ORDER BY tickets_purchased DESC
        LIMIT 5
    """
    
    cursor.execute(query, (airline_name,))
    top_customers = cursor.fetchall()
    print(top_customers)
    
    cursor.close()
    conn.close()
    return jsonify(top_customers)

@app.route('/view-reports')
def view_reports():
    return render_template('view-reports.html')

@app.route('/api/view-reports', methods=['POST'])
def view_reports_form():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login', type='AirlineStaff'))
    
    start_date = request.get_json()['start_date']
    end_date = request.get_json()['end_date']
    
    # get airline
    query = """
        SELECT name_airline
        FROM airline_staff
        WHERE username = %s
    """
    
    cursor.execute(query, (user_id,))
    airline_name = cursor.fetchone()['name_airline']
    print(airline_name)
    
    return_data = {}
    
    data = request.get_json()
    predet_range = data['range']
    start_date = data['start_date']
    end_date = data['end_date']
    
    if predet_range == "year":
        query = """
            SELECT COUNT(*) AS tickets_sold, SUM(f.price) AS total_revenue
            FROM flight f
            JOIN ticket t ON f.flight_num = t.flight_num
            JOIN purchase p ON t.ticket_id = p.ticket_id
            WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND p.date <= CURDATE() AND f.name_airline = %s
        """
    elif predet_range == "month":
        query = """
            SELECT COUNT(*) AS tickets_sold, SUM(f.price) AS total_revenue
            FROM flight f
            JOIN ticket t ON f.flight_num = t.flight_num
            JOIN purchase p ON t.ticket_id = p.ticket_id
            WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND p.date <= CURDATE() AND f.name_airline = %s
        """
    elif predet_range == "week":
        query = """
            SELECT COUNT(*) AS tickets_sold, SUM(f.price) AS total_revenue
            FROM flight f
            JOIN ticket t ON f.flight_num = t.flight_num
            JOIN purchase p ON t.ticket_id = p.ticket_id
            WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 WEEK) AND p.date <= CURDATE() AND f.name_airline = %s
        """
    else:
        start_date = data['start_date']
        end_date = data['end_date']
    
        query = """
            SELECT COUNT(*) AS tickets_sold, SUM(f.price) AS total_revenue
            FROM flight f
            JOIN ticket t ON f.flight_num = t.flight_num
            JOIN purchase p ON t.ticket_id = p.ticket_id
            WHERE p.date >= %s AND p.date <= %s AND f.name_airline = %s
        """
    
    if not predet_range:
        cursor.execute(query, (start_date, end_date, airline_name))
    else:
        cursor.execute(query, (airline_name,))
        
    tickets_sold = cursor.fetchone()
    print(tickets_sold)
    if not tickets_sold['tickets_sold']:
        tickets_sold['tickets_sold'] = 0
        tickets_sold['total_revenue'] = 0
    return_data['tickets_sold'] = tickets_sold
    
    # direct sales 1 month
    query = """
        SELECT SUM(f.price) AS total_revenue
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND p.date <= CURDATE() AND p.agent_email IS NULL AND f.name_airline = %s
    """
    
    cursor.execute(query, (airline_name,))
    direct_sales_month = cursor.fetchone()
    print(direct_sales_month)
    if not direct_sales_month['total_revenue']:
        direct_sales_month['total_revenue'] = 0
    return_data['direct_sales_month'] = direct_sales_month
    
    # indirect sales month
    query = """
        SELECT SUM(f.price) AS total_revenue
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND p.date <= CURDATE() AND p.agent_email IS NOT NULL AND f.name_airline = %s
    """
    
    cursor.execute(query, (airline_name,))
    indirect_sales_month = cursor.fetchone()
    print(indirect_sales_month)
    if not indirect_sales_month['total_revenue']:
        indirect_sales_month['total_revenue'] = 0
    return_data['indirect_sales_month'] = indirect_sales_month
    
    # direct sales year
    query = """
        SELECT SUM(f.price) AS total_revenue
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND p.date <= CURDATE() AND p.agent_email IS NULL AND f.name_airline = %s
    """
    
    cursor.execute(query, (airline_name,))
    direct_sales_year = cursor.fetchone()
    print(direct_sales_year)
    if not direct_sales_year['total_revenue']:
        direct_sales_year['total_revenue'] = 0
    return_data['direct_sales_year'] = direct_sales_year
    
    # indirect sales year
    query = """
        SELECT SUM(f.price) AS total_revenue
        FROM flight f
        JOIN ticket t ON f.flight_num = t.flight_num
        JOIN purchase p ON t.ticket_id = p.ticket_id
        WHERE p.date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR) AND p.date <= CURDATE() AND p.agent_email IS NOT NULL AND f.name_airline = %s
    """
    
    cursor.execute(query, (airline_name,))
    indirect_sales_year = cursor.fetchone()
    print(indirect_sales_year)
    if not indirect_sales_year['total_revenue']:
        indirect_sales_year['total_revenue'] = 0
    return_data['indirect_sales_year'] = indirect_sales_year
    
    cursor.close()
    conn.close()
    
    print("return_data", return_data)
    return jsonify(return_data)
if __name__ == '__main__':
    app.run(debug=True, port=5001, host='127.0.0.1')
