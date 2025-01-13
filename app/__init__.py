from flask import Flask
from .db import create_connection, create_tables, close_connection
import os
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__, static_folder="../static", template_folder="../templates")
    
    #Debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Loading environment variables from: {os.path.join(os.path.dirname(__file__), 'payment.env')}")

    load_dotenv(os.path.join(os.path.dirname(__file__), 'payment.env'))


    app.config["DATABASE"] = "pagine.db"
    app.secret_key = 'Apples&Bananas'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['SESSION_PERMANENT'] = True
    app.config['SESSION_TYPE'] ='filesystem'
   
    app.config['PAYFAST_MERCHANT_ID'] = os.getenv('PAYFAST_MERCHANT_ID', 'sandbox_merchant_id')
    app.config['PAYFAST_MERCHANT_KEY'] = os.getenv('PAYFAST_MERCHANT_KEY', 'sandbox_merchant_key')
    app.config['PAYFAST_PASS_PHRASE'] = os.getenv('PAYFAST_PASS_PHRASE', 'sandbox_pass_phrase')
    app.config['PAYFAST_URL'] = 'https://sandbox.payfast.co.za/eng/process'

    #Debugging
    print(f"Merchant ID: {app.config['PAYFAST_MERCHANT_ID']}")
    print(f"Merchant Key: {app.config['PAYFAST_MERCHANT_KEY']}")
    print(f"PAYFAST PASS PHRASE: {app.config['PAYFAST_PASS_PHRASE']}")

    from .auth import auth
    app.register_blueprint(auth)

    def init_db():
        conn = create_connection(app.config["DATABASE"])
        if conn:
            create_tables(conn)
            close_connection(conn)
        else:
            print("Error: Unable to connect to the database.")
    init_db()
        
    return app
