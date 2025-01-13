from flask import Blueprint, request, redirect, url_for,render_template, flash,session, current_app,jsonify,abort
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import create_connection, insert_user, close_connection, update_user, get_user_update_details,get_initial_user_details,get_books_by_category, get_cart_items, create_order,move_to_cart_items,delete_cart, get_order_details, view_orders_from_db,view_cart_items, get_user_id, get_book_id,add_to_cart_db,remove_from_cart_db,get_least_stock_books, update_cart_db, subscribe_db,search_books_db, get_book_details_db, get_seasonal_books_db, get_author_of_the_month_db
from datetime import datetime
import hashlib
import re 
import urllib.parse 


auth = Blueprint('auth', __name__)

#landing Page 
@auth.route("/")
def login():
	return render_template('login.html')

@auth.route('/login', methods = ['POST'])
def login_post():
 
		email = request.form['email']
		password =request.form['password']

		conn = create_connection(current_app.config["DATABASE"])
		cur = conn.cursor()

		cur.execute("SELECT * FROM Users WHERE email = ?",(email,))
		user = cur.fetchone()
		close_connection(conn)
	
		if user and check_password_hash(user[4], password):
			session["email"] = email
			return redirect(url_for('auth.home'))
		else:
			flash('Login failed. check your email and/or password.')
			return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET','POST'])
def register():

	if request.method == 'POST':
		
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		email= request.form.get('email')
		password = request.form.get('password')
        
		print(f"Firstname: {firstname}, Lastname: {lastname}, Email: {email}")

		#hash password
		hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
	    
		conn = create_connection(current_app.config["DATABASE"])
		insert_user(conn, firstname, lastname,email,hashed_password)
		close_connection(conn)

		flash('Registration successful! Please log in with your username and password.', category ='success')
		return redirect(url_for('auth.login'))
	
	return render_template('registration.html')

@auth.route("/home")
def home():
    if "email" not in session:
        return redirect(url_for('auth.login'))

    conn = create_connection(current_app.config["DATABASE"])
    least_stock_books = get_least_stock_books(conn)

    season = "Winter" #Replace with the desired season
    seasonal_books = get_seasonal_books_db(conn,season) 

    author ='Amina Diallo' #Replace with the desired author
    author_of_the_month = get_author_of_the_month_db(conn, author)
    return render_template('homepage.html', 
        least_stock_books = least_stock_books, 
        seasonal_books = seasonal_books, 
        season = season,
        author_of_the_month = author_of_the_month)

@auth.route('/account')
def account():

    email = session.get('email')
    
    if email is None:
        return redirect(url_for('auth.login'))

    conn = create_connection(current_app.config["DATABASE"])
    update = get_user_update_details(conn, email)
    initial_details = get_initial_user_details(conn, email)
    close_connection(conn)

    # Initialize variables
    phone = ''
    full_address = ''
    fullname = ''

    if initial_details:
        firstname, lastname = initial_details
        fullname = f"{firstname} {lastname}"
        print("Initial user data retrieved successfully")

    if update:
        phone, street_address, city, province, zip_code = update
        full_address = f"{street_address}, {city}, {province}, {zip_code}"
        print("Updated User data retrieved successfully")
    else:
        phone = street_address = city = province = zip_code = ''

    return render_template('account.html', 
        phone=phone,
        full_address=full_address,
        fullname=fullname,
        email=email)


@auth.route('/update', methods=['GET','POST'])
def update():
	email=  session.get('email')

	if email is None:
			flash('User not logged in')
			return redirect(url_for('auth.login'))

	if request.method=='POST':
		phone = request.form.get('phone')
		street_address = request.form.get('street_address')
		city = request.form.get('city')
		province = request.form.get('province')
		zip_code = request.form.get('zipcode')
		print(f"Phone:{phone}, Street address:{street_address}, city:{city}, province: {province}, zipcode:{zip_code}")


		conn = create_connection(current_app.config["DATABASE"])
		update_user(conn,email, phone, street_address,city,province,zip_code)
		close_connection(conn)
		flash('Update successful!', category ='success')
		return redirect(url_for('auth.account'))


@auth.route("/logout")
def logout():
    session.pop("email", None)
    flash("You have been logged out")
    return redirect(url_for("auth.login"))


@auth.route('/category/<category_name>')
def category(category_name):
    valid_categories = [
        'New Books',
        'Dark Fantasy', 'Low Fantasy', 'High Fantasy', 'Urban Fantasy', 'Sword and Sorcery',
        'Fairy Tale Fantasy', 'Mythic Fantasy', 'Steampunk Fantasy', 'Comic Fantasy',
        'Magical Realism', 'Contemporary Fantasy', 'Grimdark Fantasy', 'Heroic Fantasy',
        'Fairy Tale Retellings', 'Portal Fantasy', 'Sword and Planet'
    ]

    print(f"Received category_name: {category_name}")

    if category_name not in valid_categories:
        print("Category not in valid categories", category_name)
        abort(404)
    
    conn = create_connection(current_app.config["DATABASE"])
    books = get_books_by_category(conn, category_name)
    print(f"Books retrieved for {category_name}: {books}")
    close_connection(conn)
    return render_template('category.html', category_name=category_name, books=books)

@auth.route('/categories')
def categories():
	return render_template('categories.html')

@auth.route('/aboutus')
def aboutus():
	return render_template('aboutUs.html')

@auth.route('/subscribe', methods=['GET', 'POST'])
def subscribe():

    if request.method == 'POST':

        name = request.form.get('name')
        email = request.form.get('email')

        if not name or not email:
            flash("name and email required.", "error")

        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if email is None or not re.match(email_regex, email):
            flash("Please enter a valid email address", "error")

        try:
            conn = create_connection(current_app.config["DATABASE"])
            subscribe_db(conn, name, email)
            flash("Subscription successful", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")

    return redirect(request.referrer or url_for('auth.subscribe')+"#subscribe")

@auth.route('/search', methods=['GET'])
def search():
    query = request.args.get('query','').strip()
    print(f"Received query: '{query}'")

    if query:
        results = search_books(query)
        print(f" Search results: {results}")
        return jsonify(results=results)

    print("No query provided.")
    return jsonify(results=[])

def search_books(query):
    conn = create_connection(current_app.config["DATABASE"])
    results = search_books_db(conn, query)
    return results

@auth.route('/book/<int:book_id>', methods=['GET'])
def get_book_details(book_id):
    conn = create_connection(current_app.config["DATABASE"])
    book = get_book_details_db(conn, book_id)

    if not book:
        return "Book not found", 404
    if book: 
        book_details={

        "title": book[0],
        "author": book[1],
        "genre": book[2],
        "isbn": book[3],
        "price": book[4],
        "stock_quantity": book[5],
        "description": book[6],
        "cover_img_url": book[7],

        }
        return render_template('book.html', book=book)

@auth.route('/cart')
def view_cart():
    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))

    conn = create_connection(current_app.config["DATABASE"])
    customer_id_tuple = get_user_id(conn, email)
    customer_id = customer_id_tuple[0]

    cart_items = view_cart_items(conn, customer_id)
    if not cart_items:
        cart_items = []

    cart_items = [
        {   'cart_id': item[0],
            'book_id': item[1],
            'title': item[2],
            'price': float(item[3]),
            'quantity': item[4],
            'cover_img_url': item[5]
        }
        for item in cart_items
    ]

    total_items = sum(item['quantity'] for item in cart_items)
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)

    conn.close()

    return render_template('cart.html',
                           cart_items=cart_items,
                           total_items=total_items,
                           total_price=total_price)


@auth.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))

    book_title = request.form.get('title') 
    quantity = int(request.form.get('quantity', 1))  
    date_added = datetime.now().isoformat()

    conn = create_connection(current_app.config["DATABASE"])
    customer_id_tuple = get_user_id(conn, email)
    customer_id = customer_id_tuple[0]

    book_id_tuple = get_book_id(conn, book_title)
    book_id = book_id_tuple[0]

    add_to_cart_db(conn, customer_id, book_id, quantity, date_added)
    conn.commit()
    conn.close()

    return redirect(url_for('auth.view_cart'))


@auth.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():

    book_id = request.form.get('book_id')

    if not book_id:
        return jsonify({'error': 'No book ID provided'}), 400

    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))

    conn = create_connection(current_app.config["DATABASE"])

    customer_id_tuple = get_user_id(conn, email)
    customer_id = customer_id_tuple[0]
    print(f"In routes method, {customer_id}, {book_id}")

    remove_from_cart_db(conn, customer_id, book_id)
    cart_items = view_cart_items(conn, customer_id)
    total_items= sum(item[4] for item in cart_items)
    total_price= sum(item[3] * item[4] for item in cart_items)
    conn.close()

    return jsonify({
        'status': 'success',
        'total_items': total_items,
        'total_price': total_price})


@auth.route('/update_cart', methods=['POST'])
def update_cart():
    cart_id = request.form.get('cart_id')
    quantity = request.form.get('quantity')
    conn = create_connection(current_app.config["DATABASE"])

    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))
    
    update_cart_db(conn, quantity, cart_id)
    customer_id_tuple = get_user_id(conn, email)
    customer_id = customer_id_tuple[0]
    cart_items = view_cart_items(conn, customer_id)  
    
    total_items = sum(item[4] for item in cart_items)  
    total_price = sum(item[3] * item[4] for item in cart_items)  
    conn.close()

    # Return the updated cart summary to the front-end
    return jsonify({
        'status': 'success',
        'total_items': total_items,
        'total_price': total_price
    })

def place_order():
    print(f"Session at place_order: {session}")
    email = session.get('email')
    customer_id = session.get('customer_id')

    if not customer_id and email:
        conn = create_connection(current_app.config["DATABASE"])
        customer_id_tuple = get_user_id(conn, email)
        customer_id = customer_id_tuple[0] if customer_id_tuple else None

    shipping_address = session.get('shipping_address')
    order_date = datetime.now().isoformat()
    total_amount = session.get('total_amount')

    print(f"Customer Id:{customer_id}, Shipping Address:{shipping_address}, Order Date:{order_date}, Total Amount:{total_amount}")

    if not customer_id or not shipping_address or not total_amount:
        return jsonify({'status': 'error', 'message': 'Missing required order data'}), 400

    conn = create_connection(current_app.config["DATABASE"])

    cart_items = get_cart_items(conn, customer_id)
    if not cart_items:
        return jsonify({'status': 'error', 'message': 'Your cart is empty'}), 400

    order_id = create_order(conn, customer_id, order_date, total_amount, shipping_address,cart_items)
    print(f"in place_order, order_id :{order_id}")
    if not order_id:
        return jsonify({'status': 'error', 'message': 'Error creating order'}), 500

    delete_cart(conn, customer_id)

    session.pop('customer_id', None)
    session.pop('shipping_address', None)
    session.pop('total_amount', None)

    return order_id

@auth.route('/checkout', methods=['GET', 'POST'])
def checkout():
    email = session.get('email')
    if email is None:
        return redirect(url_for('auth.login'))

    conn = create_connection(current_app.config["DATABASE"])
    customer_id_tuple = get_user_id(conn, email)
    customer_id = customer_id_tuple[0]

    if request.method == 'POST':
        shipping_address = request.form.get('shipping_address')
        total_amount = float(request.form.get('total_amount'))

        print(f"Setting session data in POST: customer_id={customer_id}, shipping_address={shipping_address}, total_amount={total_amount}")

        if not shipping_address or not payment_method:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

        session['customer_id'] = customer_id
        session['shipping_address'] = shipping_address
        session['total_amount'] = total_amount
        session.modified = True

    else:
        # Fetch cart items to display
        cart_items = view_cart_items(conn, customer_id)

        if not cart_items:
            cart_items = []

        # Convert tuples to dictionaries
        cart_items = [
            {
                'cart_id': item[0],
                'book_id': item[1],
                'title': item[2],
                'price': float(item[3]),
                'quantity': int(item[4]),
                'cover_img_url': item[5]
            }
            for item in cart_items
        ]

        total_items = sum(item['quantity'] for item in cart_items)
        total_price = sum(item['price'] * item['quantity'] for item in cart_items)
        formatted_total_amount =f'{total_price:.2f}'

        # Calculate the signature here
        payfast_params = {
            'merchant_id': current_app.config['PAYFAST_MERCHANT_ID'],
            'merchant_key': current_app.config['PAYFAST_MERCHANT_KEY'],
            'return_url': url_for('auth.payment_success', _external=True),
            'cancel_url': url_for('auth.payment_cancel', _external=True),
            'notify_url': url_for('auth.payment_notify', _external=True),
            'email_address': email,
            'm_payment_id': str(customer_id),
            'amount': f"{float(formatted_total_amount):.2f}",
            'item_name': 'Order Payment'
            
        }

        # Debugging: Log the parameter values
        print("=== PayFast Parameters ===")
        for key, value in payfast_params.items():
            print(f"{key}: {value}")

        signature_string = ''
        for key, value in payfast_params.items():
            if value:
                signature_string += f"{key}={urllib.parse.quote_plus(value)}&"

        passphrase = current_app.config.get('PAYFAST_PASS_PHRASE')
        if passphrase:
            signature_string += f"passphrase={urllib.parse.quote_plus(passphrase)}"

        # Debugging: Log the raw signature string
        print("=== Raw Signature String ===")
        print(signature_string)

        # Generate the MD5 hash of the signature string
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
        # Debugging: Log the generated signature
        print("=== Generated Signature ===")
        print(signature)
        
        conn.close()
        return render_template('checkout.html',
            email = email,
            customer_id = customer_id, 
            cart_items=cart_items, 
            total_items=total_items, 
            total_price=formatted_total_amount,
            signature = signature,
            PAYFAST_MERCHANT_ID = current_app.config['PAYFAST_MERCHANT_ID'],
            PAYFAST_MERCHANT_KEY = current_app.config['PAYFAST_MERCHANT_KEY'])

@auth.route('/orders/<int:customer_id>')
def view_user_orders(customer_id):
    
    conn = create_connection(current_app.config["DATABASE"])
    orders =  view_orders_from_db(conn, customer_id)
    conn.close()
    return render_template('orders.html', orders = orders)

@auth.route('/order_details/<int:order_id>')
def view_order_details(order_id):
    conn = create_connection(current_app.config["DATABASE"])
    order_details = get_order_details(conn, order_id)
    conn.close()
    return render_template('order_details.html', order_details=order_details)


@auth.route('/payment_success', methods=['POST', 'GET'])
def payment_success():
    # Fetch payment details from PayFast response (POST request)
    payment_status = request.form.get('payment_status', 'COMPLETE')  # Default to COMPLETE for now
    m_payment_id = request.form.get('m_payment_id')  # Customer ID or unique order ID
    amount_paid = request.form.get('amount_gross')  # Amount sent back from PayFast

    # Debugging: Log the payment status
    print(f"Payment Status: {payment_status}")
    print(f"Payment ID: {m_payment_id}")
    print(f"Amount Paid: {amount_paid}")

    # Check if payment was successful
    if payment_status != 'COMPLETE':
        return render_template('payment_failed.html', message="Payment not successful."), 400

    order_id = place_order()
    if isinstance(order_id, dict):
        return jsonify(order_id), 400
    return render_template('payment_success.html', order_id=order_id)

@auth.route('/payment_cancel')
def payment_cancel():
    return render_template('payment_cancel.html')

@auth.route('/payment_notify', methods=['POST'])
def payment_notify():
    # PayFast sends a POST request here with payment details
    payment_status = request.form.get('payment_status')
    m_payment_id = request.form.get('m_payment_id')
    amount_gross = request.form.get('amount_gross')

    # Log the notification data for debugging
    print("Payment Notification Received:")
    print(f"Payment Status: {payment_status}")
    print(f"Payment ID: {m_payment_id}")
    print(f"Amount Paid: {amount_gross}")

    # You can add additional validation here if needed

    return "Payment notification received", 200

