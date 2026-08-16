import time
import mysql.connector
import bcrypt
import time
import mysql.connector
import bcrypt
from twilio.rest import Client
import mysql.connector
import schedule
import time
from twilio.rest import Client
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import threading


# Function to set warranty reminders for a user
# Twilio credentials (replace with your own values)
TWILIO_ACCOUNT_SID = "AC51802bca71499b6da25284cf0471f8ef"
TWILIO_AUTH_TOKEN = "57de58d69e299a2151ac4144c646b6f4"
TWILIO_PHONE_NUMBER = "+15109534342"
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def send_twilio_sms(body, to_phone_number):
    try:
        message = twilio_client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        print(f"Twilio SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Twilio SMS sending failed: {str(e)}")


def set_warranty_reminders(conn, user_id):
    try:
        with conn.cursor() as cursor:
            # Fetch the user's phone number
            cursor.execute("SELECT phone_number FROM users WHERE id = %s", (user_id,))
            user_data = cursor.fetchone()
            if not user_data:
                print("User not found in the database.")
                return

            user_phone_number = user_data[0]
            interval_days = int(input("Enter the interval (in days) for warranty reminders: "))

            # Fetch product details
            cursor.execute("""
                SELECT product_name, purchase_date, warranty_period
                FROM offline_product_registrations
                WHERE user_id = %s
            """, (user_id,))
            products = cursor.fetchall()

            if not products:
                print("No products found for reminders.")
                return

            for product in products:
                product_name, purchase_date, warranty_period = product
                if isinstance(purchase_date, str):
                    purchase_date = datetime.strptime(purchase_date, '%Y-%m-%d').date()

                warranty_expiry_date = purchase_date + relativedelta(months=warranty_period)
                expiry_date_str = warranty_expiry_date.strftime('%Y-%m-%d')
                ack_message = (f"Reminder set for {product_name}. Warranty valid until {expiry_date_str}. "
                               f"Next reminder in {interval_days} days.")
                send_twilio_sms(ack_message, user_phone_number)

                # Schedule the warranty reminders
                schedule.every(interval_days).days.do(
                    send_twilio_sms, f"Warranty Reminder for {product_name}: Check your warranty.", user_phone_number
                )

            # Start the scheduler thread if it's not already running
            if not any(t.name == 'SchedulerThread' for t in threading.enumerate()):
                scheduler_thread = threading.Thread(target=run_scheduler, name='SchedulerThread')
                scheduler_thread.daemon = True
                scheduler_thread.start()

            print("Warranty reminders have been set for all products.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Function to display loading animation
def loading_animation():
    for _ in range(10):
        print(".", end="", flush=True)
        time.sleep(0.5)

# Function to display the welcome message and menu
def display_menu():
    print("Welcome to Product Registration App")
    print("Loading", end=" ")
    loading_animation()
    print("\nOptions:")
    print("1. Register Product")
    print("2. Set Warranty Reminders")
    print("3. Display Registered Products")
    print("4. Logout")

# Create a MySQL database connection
conn = mysql.connector.connect(
    host='localhost',  # Change to the address of your local MySQL server
    user='root',  # Use your MySQL 'root' user
    password='daddy',  # Replace with your MySQL root password
    database='datafix',
)

# Create a cursor to execute SQL queries
cursor = conn.cursor()

# Function to create separate tables for offline and online product registrations
def create_offline_product_registration_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS offline_product_registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_name VARCHAR(255),
        seller VARCHAR(255),
        purchase_date DATE,
        warranty_period INT,
        warranty_code VARCHAR(255),
        purchase_bill_path VARCHAR(255),
        source_url VARCHAR(255) DEFAULT NULL
    )
    """

    cursor.execute(create_table_query)
    conn.commit()

# Function to register a user
def register_user():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        phone_number VARCHAR(255) NOT NULL
    )"""
    print("You chose to register an account.")
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    email = input("Enter your email: ")
    phone_number = input("Enter your phone number: ")

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    insert_user_query = "INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)"
    user_data = (username, hashed_password, email, phone_number)

    try:
        with conn.cursor() as cursor:
            cursor.execute(create_table_query)  # Execute the table creation query
            cursor.execute(insert_user_query, user_data)  # Insert the user data
            conn.commit()
            print("Account registered successfully.")
    except mysql.connector.Error as err:
        print(f"Database error: {err}")


# Function to log in a user
def login_user():

    print("You chose to log in.")
    username = input("Enter your username: ")
    password = input("Enter your password: ")

    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                print("Login successful.")
                return user_data[0]
            else:
                print("Login failed. Please check your credentials.")
                return None
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None

# Function to register an offline product

def register_product(user_id):
        print("You are registering a product.")
        is_online = input("Is this product registered online? (yes/no): ").strip().lower()

        product_name = input("Enter the product name: ")
        purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
        warranty_period = int(input("Enter the warranty period in months: "))
        warranty_code = input("Enter the warranty code: ")

        # Initialize optional fields based on whether the product is online or offline
        if is_online == "yes":
            seller = None  # Not needed for online products
            purchase_bill_path = None  # Not needed for online products
            source_url = input("Enter the source URL: ")  # Required for online products
        else:
            seller = input("Enter the seller: ")  # Required for offline products
            purchase_bill_path = input("Enter the purchase bill path: ")  # Required for offline products
            source_url = None  # Not applicable for offline products

        insert_product_query = """
        INSERT INTO offline_product_registrations (
            user_id, product_name, seller, purchase_date, warranty_period, warranty_code,
            purchase_bill_path, source_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        product_data = (
        user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path, source_url)

        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_product_query, product_data)
                conn.commit()
                print("Product registered successfully.")
        except mysql.connector.Error as err:
            print(f"Database error: {err}")


# Function to display registered products
def display_registered_products(user_id):
    print("Registered Products:")
    try:
        with conn.cursor() as cursor:
            # Query to fetch all products for the given user_id
            cursor.execute("""
                SELECT product_name, seller, purchase_date, warranty_code, purchase_bill_path, source_url
                FROM offline_product_registrations
                WHERE user_id = %s
            """, (user_id,))
            products = cursor.fetchall()

            # Check and print products based on whether they are online or offline
            print("Products:")
            for product in products:
                product_name, seller, purchase_date, warranty_code, purchase_bill_path, source_url = product
                if source_url:  # This indicates an online registration
                    print(f"Online Product - Name: {product_name}, Purchase Date: {purchase_date}, Warranty Code: {warranty_code}, Source URL: {source_url}")
                else:  # This indicates an offline registration
                    print(f"Offline Product - Name: {product_name}, Seller: {seller}, Purchase Date: {purchase_date}, Warranty Code: {warranty_code}, Bill Path: {purchase_bill_path}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Function to get warranty expiry date
def get_warranty_expiry_date(purchase_date, warranty_period):
    purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d")
    expiry_date = purchase_date + relativedelta(months=int(warranty_period))
    remaining_days = (expiry_date - datetime.now().date()).days
    return expiry_date.strftime("%Y-%m-%d"), remaining_days

# Main function
def main():
    create_offline_product_registration_table(cursor)

    while True:
        print("Welcome to Product Registration App")
        print("Options:")
        print("1. Login")
        print("2. Register an Account")

        choice = input("Enter your choice (1/2): ")

        if choice == "1":
            user_id = login_user()  # No arguments needed

            if user_id:
                print("Login successful.")
                user_menu(user_id)
            else:
                print("Login failed. Please check your credentials.")

        elif choice == "2":
            register_user()  # No arguments needed
            print("Account registered successfully.")

        else:
            print("Invalid choice. Please choose 1 or 2.")


def user_menu(user_id):
    while True:
        print("\nOptions:")
        print("1. Register Product")
        print("2. Set Warranty Reminders")
        print("3. Display Registered Products")
        print("4. Logout")

        choice = input("Enter your choice (1/2/3/4): ")

        if choice == "1":
            register_product(user_id)
        elif choice == "2":
            set_warranty_reminders(conn, user_id)
        elif choice == "3":
            display_registered_products(user_id)
        elif choice == "4":
            print("Logout successful.")
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()
