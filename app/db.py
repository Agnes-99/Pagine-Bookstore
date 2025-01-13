import sqlite3
import string 
import random


def create_connection(db_file):

    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Connected to SQLite database: {db_file}")
    except sqlite3.Error as e:
        print(f"SQLite Error: {e}, could not connect to database.")
    except OSError as e:
        print(f"OSError: {e}, invalid file path: {db_file}")
    except Exception as e:
        print(f"Unexpected Error: {e}")

    return conn



def create_tables(conn):

	if conn is None:
		print("Connection is not established ")
		return
	
	try: 
		cur = conn.cursor()
		
		cur.execute('''

			CREATE TABLE IF NOT EXISTS Users(
			   
			   user_id INTEGER PRIMARY KEY AUTOINCREMENT,
			   firstname TEXT NOT NULL,
			   lastname TEXT NOT NULL,
			   email TEXT UNIQUE NOT NULL,
			   password_hash TEXT NOT NULL,
			   phone TEXT,
			   address TEXT,
			   city TEXT,
			   province TEXT,
			   zip_code TEXT
			   )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Authors(
			  
			  author_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  name TEXT NOT NULL,
			  bio TEXT,
			  birthdate DATE,
			  nationality TEXT
			  )
		''')

		cur.execute('''
		    
			CREATE TABLE IF NOT EXISTS Publishers(
			  
				publisher_id INTEGER PRIMARY KEY  AUTOINCREMENT,
			  	name TEXT NOT NULL,
			  	address TEXT,
			  	phone TEXT,
			  	email TEXT
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Genres(
			  
			  genre_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  name TEXT,
			  description TEXT
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Books(
			  
			  book_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  title TEXT NOT NULL,
			  author_id INTEGER,
			  publisher_id INTEGER,
			  genre_id INTEGER,
			  isbn TEXT NOT NULL,
			  price REAL NOT NULL,
			  stock_quantity INTEGER NOT NULL,
			  description TEXT,
			  cover_img_url TEXT NOT NULL,
			  FOREIGN KEY (author_id) REFERENCES Authors(author_id),
			  FOREIGN KEY (publisher_id) REFERENCES Publishers(publisher_id),
			  FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Orders(
			  
			  order_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  customer_id INTEGER,
			  order_date DATETIME,
			  status TEXT,
			  total_amount REAL,
			  FOREIGN KEY(customer_id) REFERENCES Users(user_id)
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Order_Items(
			  
			  order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  order_id INTEGER,
			  book_id INTEGER,
			  quantity INTEGER,
			  price REAL,
			  FOREIGN KEY(order_id) REFERENCES Orders(order_id),
			  FOREIGN KEY(book_id) REFERENCES Books(book_id)
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Reviews(
			  
			  review_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  book_id INTEGER,
			  customer_id INTEGER,
			  rating INTEGER,
			  comment TEXT,
			  review_date DATETIME,
			  FOREIGN KEY(book_id) REFERENCES Books(book_id),
			  FOREIGN KEY(customer_id) REFERENCES Users(user_id)
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Shopping_cart(
			  
			  cart_id INTEGER PRIMARY KEY AUTOINCREMENT,
			  customer_id INTEGER,
			  book_id INTEGER,
			  quantity INTEGER,
			  date_added DATETIME,
			  FOREIGN KEY(customer_id) REFERENCES Users(user_id),
			  FOREIGN KEY(book_id) REFERENCES Books(book_id) 
			  )
		''')

		cur.execute('''

			CREATE TABLE IF NOT EXISTS Wishlist(
			  
			  wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
		      book_id INTEGER,
			  customer_id INTEGER,
			  date_added DATETIME,
			  FOREIGN KEY(book_id) REFERENCES Books(book_id),
			  FOREIGN KEY(customer_id) REFERENCES Users(user_id)
			  )
		''')

		cur.execute('''
			CREATE TABLE IF NOT EXISTS Subscriptions(
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				name TEXT NOT NULL,
				email TEXT NOT NULL UNIQUE,
				subcribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
				);
			''')

		conn.commit()
		print("Tables created successfully.")

	except sqlite3.Error as e:
		print(f"Error creating tables: {e}")
	finally:
		cur.close() if cur else None


#Functions-------------------------------------------------------------------------------------------

def subscribe_db(conn, name, email):
	try:
		cur = conn.cursor()
		cur.execute('''
			INSERT INTO Subscriptions(name, email)
			VALUES(?,?)
			''',(name,email))
		conn.commit()
		print("User subscribed succsefully")
	except sqlite3.Error as e:
		print(f"Error subscribing: {e}")
	finally:
		cur.close() if cur else None


def insert_user(conn, firstname, lastname,email,hashed_password):
	try:
		cur = conn.cursor()
		cur.execute('''
				INSERT INTO Users(firstname, lastname, email, password_hash)
				VALUES (?,?,?,?)
				''', (firstname, lastname, email, hashed_password))
		conn.commit()
		print("User inserted successfully")
	except sqlite3.Error as e:
		print(f"Error inserting user: {e}")
	finally:
		cur.close() if cur else None

def update_user(conn, email, phone, address, city, province,zip_code):
	try:
		cur = conn.cursor()
		cur.execute('''

				UPDATE Users SET
				phone =?,
				address =?,
				city=?,
				province=?,
				zip_code=?
				WHERE email=?''',
				(phone,address,city,province,zip_code, email))
		conn.commit()
		print("User updated successfully")
	except sqlite3.Error as e:
		print(f"Error updating user: {e}")
	finally:
		cur.close() if cur else None

def get_user_update_details(conn, email):
	try:
		cur= conn.cursor()
		cur.execute('''
			SELECT phone, address, city, province, zip_code
			FROM Users
			WHERE email=?
			''',(email,))
		user = cur.fetchone()
		if user:
			print("updated details retrived(dp.py) successfully")
		return user
	except sqlite3.Error as e:
		print(f"Error fetching updated details:{e}")
	finally:
		cur.close() if cur else None

def get_initial_user_details(conn,email):
	try:
		cur = conn.cursor()
		cur.execute('''
			SELECT firstname,lastname
			FROM Users
			WHERE email=?
			''',(email,))
		user = cur.fetchone()
		if user:
			print("initial details retrived(dp.py) successfully",user)
		return user
	except sqlite3.Error as e:
		print(f"Error fetching initial details{e}")
	finally:
		cur.close() if cur else None

def get_books_by_category(conn,category_name):
	try:
		cur = conn.cursor()
		query ='''
	
			SELECT b.book_id, b.title, a.name AS author_name, p.name AS publisher_name, b.price, b.cover_img_url
			FROM Books b
			JOIN Authors a ON b.author_id =a.author_id
			JOIN Publishers p ON b.publisher_id =p.publisher_id
			JOIN Genres g ON b.genre_id =g.genre_id
			WHERE g.name =?
		'''
		cur.execute(query,(category_name,))
		rows = cur.fetchall()
		books =[
			{	
				'book_id':row[0],
				'title':row[1],
				'author_name':row[2],
				'publisher_name':row[3],
				'price':row[4],
				'cover_img_url':row[5]
			}
			for row in rows
		]
		if books:
			print("book info reteieved successfully",books)
		return books
	except sqlite3.Error as e:
		print(f"Error fetching books: {e}")
		return[]
	finally:
		cur.close() if cur else None

def get_book_id(conn,book_tittle):
	try:
		cur=conn.cursor()
		query ='''
		  SELECT book_id FROM Books 
		  WHERE title=?
		'''
		book_id = cur.execute(query,(book_tittle,)).fetchone()
		print("book Id retrived: ", book_id)
		return book_id
	except sqlite3.Error as e:
		print(f"Error getting book id: {e}")
	finally:
		cur.close() if cur else None

def get_least_stock_books(conn):
    try:
        cur = conn.cursor()
        query = '''
            SELECT b.book_id,b.title, a.name AS author_name, p.name AS publisher_name, b.price, b.cover_img_url, b.stock_quantity, g.name AS genre_name
            FROM Books b
            JOIN Authors a ON b.author_id = a.author_id
            JOIN Publishers p ON b.publisher_id = p.publisher_id
            JOIN Genres g ON b.genre_id = g.genre_id
            ORDER BY b.stock_quantity ASC  
            LIMIT 6  
        '''

        cur.execute(query)
        rows = cur.fetchall()

        least_stock_books = []
        for row in rows:
            book = {
            	'book_id':row[0],
                'title': row[1],
                'author_name': row[2],
                'publisher_name': row[3],
                'price': row[4],
                'cover_img_url': row[5],
                'stock_quantity': row[6],
                'genre_name': row[7]
            }
            least_stock_books.append(book)

        return least_stock_books

    except sqlite3.Error as e:
        print(f"Error fetching books: {e}")
        return []

    finally:
        cur.close() if cur else None

def get_seasonal_books_db(conn, season):
    """
    Fetch books for the given season by searching for seasonal keywords in the description.
    """
    try:
        cur = conn.cursor()
        
        # Define seasonal keywords
        keywords = {
            "Winter": ["snow", "cold", "winter", "frost", "ice"],
            "Summer": ["sun", "summer", "beach", "heat", "vacation"],
            "Spring": ["spring", "bloom", "flower", "rain", "rebirth"],
            "Autumn": ["fall", "autumn", "leaves", "harvest", "pumpkin"]
        }
        
        season_keywords = keywords.get(season, [])
        if not season_keywords:
            print(f"Invalid season: {season}. Please choose 'Winter', 'Summer', 'Spring', or 'Autumn'.")
            return []

        # search for keywords
        query = f'''
            SELECT b.book_id, b.title, a.name AS author_name, p.name AS publisher_name,
                   b.price, b.cover_img_url, b.stock_quantity, g.name AS genre_name, b.description
            FROM Books b
            JOIN Authors a ON b.author_id = a.author_id
            JOIN Publishers p ON b.publisher_id = p.publisher_id
            JOIN Genres g ON b.genre_id = g.genre_id
            WHERE {" OR ".join(["b.description LIKE ?" for _ in season_keywords])}
            ORDER BY b.title ASC
        '''
        
        # Create parameters for placeholders
        params = [f"%{keyword}%" for keyword in season_keywords]
        cur.execute(query, params)
        
        rows = cur.fetchall()
        seasonal_books = []
        
        for row in rows:
            book = {
                'book_id': row[0],
                'title': row[1],
                'author_name': row[2],
                'publisher_name': row[3],
                'price': row[4],
                'cover_img_url': row[5],
                'stock_quantity': row[6],
                'genre_name': row[7],
                'description': row[8]
            }
            seasonal_books.append(book)
        
        return seasonal_books

    except sqlite3.Error as e:
        print(f"Error fetching seasonal books: {e}")
        return []
    finally:
        cur.close() if cur else None

def get_author_of_the_month_db(conn, author):
   
    try:
        cur = conn.cursor()
        query = '''
            SELECT b.book_id, b.title, b.price, b.cover_img_url, b.stock_quantity, 
                   g.name AS genre_name, a.name AS author_name
            FROM Books b
            JOIN Authors a ON b.author_id = a.author_id
            JOIN Genres g ON b.genre_id = g.genre_id
            WHERE a.name = ?  -- Filter by author name
            ORDER BY b.title ASC  -- Order books alphabetically by title
        '''
        
        cur.execute(query, (author,))
        rows = cur.fetchall()

        # Store the author's books in a list
        author_books = []
        for row in rows:
            book = {
                'book_id': row[0],
                'title': row[1],
                'price': row[2],
                'cover_img_url': row[3],
                'stock_quantity': row[4],
                'genre_name': row[5],
                'author_name': row[6]
            }
            author_books.append(book)
        
        return {
            "author_name": author,
            "books": author_books
        }

    except sqlite3.Error as e:
        print(f"Error fetching author of the month details: {e}")
        return None

    finally:
        cur.close() if cur else None

def get_user_id(conn, email):
	try:
		cur = conn.cursor()  
		query ='''
				SELECT user_id from Users WHERE email=?
				'''
		user_id = cur.execute(query,(email,)).fetchone()
		print("User Id retrived:", user_id)
		return user_id
	except sqlite3.Error as e:
		print(f"Error getting user id:{e}")
	finally:
		cur.close() if cur else None


def add_to_cart_db(conn,customer_id, book_id,quantity,date_added):
	try:
		cur =conn.cursor()

		existing_item = get_cart_item(conn,customer_id, book_id)

		if existing_item:
			cart_id = existing_item[0]
			new_quantity = existing_item[3] + quantity
			update_cart_db(conn,new_quantity,cart_id)
		else: 
			query = '''
					INSERT INTO shopping_cart (customer_id, book_id, quantity, date_added)
					VALUES(?,?,?,?)
				'''
			cur.execute(query,(customer_id,book_id,quantity,date_added))
		conn.commit()
		print("Items added to shopping cart successfully")
	except sqlite3.Error as e:
		print(f"Error adding items to cart:{e}")
	finally:
		cur.close() if cur else None

def get_cart_item(conn, customer_id, book_id):
	try:
		cur = conn.cursor()
		query ='''
			SELECT * FROM shopping_cart
			WHERE customer_id=? AND book_id=?
		'''
		cur.execute(query, (customer_id, book_id))
		return cur.fetchone()
	except sqlite3.Error as e:
		print(f"Error checking cart for item:{e}")
		return None
	finally: 
		cur.close() if cur else None

def view_cart_items(conn, customer_id):
	try:
		cur = conn.cursor()
		query ='''
			SELECT sc.cart_id,b.book_id, b.title, b.price, sc.quantity, b.cover_img_url
			FROM shopping_cart sc
			JOIN books b ON sc.book_id = b.book_id
			WHERE sc.customer_id=?
		'''
		cart_items = cur.execute(query,(customer_id,)).fetchall()
		print("Cart items fetch successful!", cart_items)
		return cart_items
	except sqlite3.Error as e:
		print(f"cart items fetch unsucessful:{e}")
		return[]
	finally:
		cur.close() if cur else None

def remove_from_cart_db(conn, customer_id, book_id):
	
	try:
		cur = conn.cursor()
		query = '''
			DELETE FROM shopping_cart WHERE customer_id=? AND book_id =?
		'''
		cur.execute(query,(customer_id, book_id))
		conn.commit()
		print(f"Item with Book_id {book_id} removed from cart for customer {customer_id}")
	except sqlite3.Error as e:
		print(f"Error removing item from cart:{e}")
		conn.rollback()
	finally:
		cur.close() if cur else None

def update_cart_db(conn,quantity,cart_id):
	try:
		cur = conn.cursor()
		query ='''
			UPDATE shopping_cart SET quantity =? WHERE cart_id =?
			'''
		cur.execute(query,(quantity, cart_id))
		conn.commit()
		print("Cart Updated")
	except sqlite3.Error as e :
		print(f"error updating cart:{e}")
		conn.rollback()
	finally:
		cur.close() if cur else None

def get_cart_items(conn, customer_id):
	try:
		cur = conn.cursor()
		query ='''
				SELECT b.price, sc.quantity, sc.book_id
				FROM shopping_cart sc
				JOIN books b ON sc.book_id = b.book_id
				WHERE sc.customer_id =?	
		'''
		cur.execute(query,(customer_id,))
		cart_items =cur.fetchall()
		print(f"cart items for customer_id {customer_id}: {cart_items}")
		return cart_items
	except sqlite3.Error as e:
		print(f"Error fetching total amount: {e}")
		return[]
	finally:
		cur.close() if cur else None

def move_to_cart_items(conn,order_id, cart_items):
	try:
		cur=conn.cursor()
		query = '''
				INSERT INTO order_items(order_id, book_id, quantity, price)
				VALUES(?,?,?,?)
			'''
		cur.execute(query,(order_id,cart_items['book_id'], cart_items['quantity'], cart_items['price']))
		conn.commit()
		print("Moved to items_cart successfully")
	except sqlite3.Error as e:
		print(f"Error moving to cart_items: {e}")
	finally:
		cur.close() if cur else None

def delete_cart(conn, customer_id):
	try:
		cur = conn.cursor()
		query = '''
			DELETE FROM shopping_cart WHERE customer_id=?
		'''
		cur.execute(query,(customer_id,))
		conn.commit()
		print(f"Cart cleared for customer_id {customer_id}")
	except sqlite3.Error as e:
		print(f"Error clearing cart: {e}")
	finally:
		cur.close() if cur else None

def view_orders_from_db(conn, customer_id):
	try:
		cur = conn.cursor()
		query ='''
				SELECT * FROM Orders
				WHERE customer_id =?
			'''
		orders = cur.execute(query,(customer_id,)).fetchall()
		print("orders fetched successfully")
		return orders
	except sqlite3.Error as e:
		print(f"Error fetching orders: {e}")
		return[]
	finally:
		cur.close() if cur else None

def get_order_details(conn, order_id):
	try:
		cur =conn.cursor()
		query = '''
				SELECT oi.order_item_id, b.title, b.price, oi.quantity
				FROM order_items oi
				JOIN books b ON oi.book_id = b.book_id
				WHERE oi.order_id =?
				'''
		order_details = cur.execute(query,(order_id,)).fetchall()
		print("Order details fetched succsefully")
		return order_details
	except sqlite3.Error as e:
		print(f"Error fetching order details:{e}")
		return []
	finally:
		cur.close() if cur else None


def close_connection(conn):
	if conn:
		conn.close()
		print("Connection closed")


def create_order(conn, customer_id, order_date, total_amount, shipping_address, items):
	try:
		cur=conn.cursor()
		generated_order_id = generate_orderNo()
		query = '''
				INSERT INTO Orders(order_id, customer_id, order_date,status,total_amount,shipping_address)
				VALUES(?,?,'Pending',?,?)
		'''
		cur.execute(query,(generated_order_id,customer_id,order_date,total_amount,shipping_address))
		order_id = cur.lastrowid
		print(f"Order submitted successfully:{order_id}")

		query2 ='''
			INSERT INTO Order_Items(order_id,book_id,quantity,price)
			VALUES (?,?,?,?)
		'''
		for price, quantity, book_id in items:
			cur.execute(query2,(order_id,book_id,quantity,price))

		print(f"Order_items addeded succesffully in cart_items table for order_id: {order_id}")
		conn.commit()
		print("Transcation commited succesfully")
	except sqlite3.Error as e:
		print(f"Error adding Order or Order Items:{e}")
		conn.rollback()
	finally:
		cur.close() 

def search_books_db(conn, query):
	try:
		cur = conn.cursor()
		query =f"%{query}%"
		cur.execute('''
			SELECT book_id,title, name, cover_img_url
			FROM Books 
			INNER JOIN Authors ON Books.author_id = Authors.author_id
			WHERE title LIKE ? OR name LIKE ? OR description LIKE ?
			''', (query, query, query))
		results = cur.fetchall()
		print("Search results retrived successfully")
		return results
	except sqlite3.Error as e:
		print(f" Error searching database: {e}")
		return []
	finally:
		cur.close() if cur else None

def get_book_details_db(conn, book_id):
	try: 
		cur = conn. cursor()
		query = '''
				SELECT Books.title,
				Authors.name As author,
				Genres.name as genre,
				Books.isbn,
				Books.price,
				Books.stock_quantity,
				Books.description,
				Books.cover_img_url
				FROM Books
				LEFT JOIN Authors ON Books.author_id=Authors.author_id
				LEFT JOIN Genres ON Books.genre_id = Genres.genre_id
				WHERE book_id = ?
		'''
		cur.execute(query, (book_id,))
		book = cur.fetchone()
		print(f"Book retrived successfully: {book}")
		return book
	except sqlite3.Error as e:
		print(f"Error retrieving book: {e}")
		return None
	finally:
		cur.close() if cur else None

#Generate random order number 
def generate_orderNo(length=6):
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choice(characters) for _ in range(length))


