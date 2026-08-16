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
from datetime import datetime

# Function to send an SMS using Twilio
def send_twilio_sms(body, to_phone_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        message = client.messages.create(
            body=body,
            from_=TWILIO_PHONE_NUMBER,
            to=to_phone_number
        )
        print(f"Twilio SMS sent successfully: {message.sid}")
    except Exception as e:
        print(f"Twilio SMS sending failed: {str(e)}")

# Function to set warranty reminders for a user
# Twilio credentials (replace with your own values)
TWILIO_ACCOUNT_SID = "AC51802bca71499b6da25284cf0471f8ef"
TWILIO_AUTH_TOKEN = "57de58d69e299a2151ac4144c646b6f4"
TWILIO_PHONE_NUMBER = "+1234567890"  # Replace with y
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
def set_warranty_reminders(user_id):
    # Fetch user's phone number from the database
    select_user_query = "SELECT phone_number FROM users WHERE id = %s"
    cursor.execute(select_user_query, (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user_phone_number = user_data[0]
    else:
        print("User not found in the database.")
        return

    # Set warranty reminders (adjust the scheduling time and message as needed)
    schedule.every().day.at("14:00").do(
        send_twilio_sms, "Warranty Reminder: Check your warranty.", user_phone_number
    )

    # Keep running the scheduler
    while True:
        schedule.run_pending()
        time.sleep(1)
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
    print("1. Register Product Online")
    print("2. Register Product Offline")
    print("3. Set Warranty Reminders")
    print("4. Display Registered Products")
    print("5. Logout")

# Create a MySQL database connection
conn = mysql.connector.connect(
    host='localhost',  # Change to the address of your local MySQL server
    user='root',  # Use your MySQL 'root' user
    password='daddy1234',  # Replace with your MySQL root password
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
        purchase_bill_path VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)
    conn.commit()

def create_online_product_registration_table(cursor):
    create_table_query = """
    CREATE TABLE IF NOT EXISTS online_product_registrations (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        product_name VARCHAR(255),
        purchase_date DATE,
        warranty_period INT,
        warranty_code VARCHAR(255),
        source_url VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)
    conn.commit()


# Function to register a user
def register_user():
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
            cursor.execute(insert_user_query, user_data)
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
def register_offline_product(user_id):
    print("You chose offline product registration.")
    product_name = input("Enter the product name: ")
    seller = input("Enter the seller: ")
    purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
    warranty_period = int(input("Enter the warranty period in months: "))
    warranty_code = input("Enter the warranty code: ")
    purchase_bill_path = input("Enter the purchase bill path: ")

    insert_product_query = """
    INSERT INTO offline_product_registrations (user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    product_data = (user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path)

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_product_query, product_data)
            conn.commit()
            print("Offline product registered successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to register an online product
def register_online_product(user_id):
    print("You chose online product registration.")
    product_name = input("Enter the product name: ")
    purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
    warranty_period = int(input("Enter the warranty period in months: "))
    warranty_code = input("Enter the warranty code: ")
    source_url = input("Enter the source URL: ")

    insert_product_query = """
    INSERT INTO online_product_registrations (user_id, product_name, purchase_date, warranty_period, warranty_code, source_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    """

    product_data = (user_id, product_name, purchase_date, warranty_period, warranty_code, source_url)

    try:
        with conn.cursor() as cursor:
            cursor.execute(insert_product_query, product_data)
            conn.commit()
            print("Online product registered successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")

# Function to display registered products
def display_registered_products(user_id):
    print("Registered Products:")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT product_name, seller, purchase_date, warranty_code FROM online_product_registrations WHERE user_id = %s", (user_id,))
            online_products = cursor.fetchall()
            print("Online Products:")
            for product in online_products:
                print(f"Product Name: {product[0]}, Seller: {product[1]}, Purchase Date: {product[2]}, Warranty Code: {product[3]}")

        with conn.cursor() as cursor:
            cursor.execute("SELECT product_name, seller, purchase_date, warranty_code FROM offline_product_registrations WHERE user_id = %s", (user_id,))
            offline_products = cursor.fetchall()
            print("Offline Products:")
            for product in offline_products:
                print(f"Product Name: {product[0]}, Seller: {product[1]}, Purchase Date: {product[2]}, Warranty Code: {product[3]}")

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
    create_online_product_registration_table(cursor)

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
        print("1. Register Product Online")
        print("2. Register Product Offline")
        print("3. Set Warranty Reminders")
        print("4. Display Registered Products")
        print("5. Logout")

        choice = input("Enter your choice (1/2/3/4/5): ")

        if choice == "1":
            register_online_product(user_id)
        elif choice == "2":
            register_offline_product(user_id)
        elif choice == "3":
            set_warranty_reminders(user_id)
        elif choice == "4":
            display_registered_products(user_id)
        elif choice == "5":
            print("Logout successful.")
            break
        else:
            print("Invalid choice. Please choose 1, 2, 3, 4, or 5.")

if __name__ == "__main__":
    main()


