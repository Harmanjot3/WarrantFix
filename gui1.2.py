import time
from datetime import datetime, timedelta
import mysql.connector
import bcrypt

# Function to display loading animation
def loading_animation():
    for _ in range(10):
        print(".", end="", flush=True)
        time.sleep(0.5)

# Function to display the welcome message and menu
def display_menu():
    print("\nOptions:")
    print("1. Register Product Online")
    print("2. Register Product Offline")
    print("3. Set Warranty Reminders")
    print("4. Display Registered Products")
    print("5. Logout")

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

# Function to register a user
def register_user(cursor, username, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    insert_user_query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    user_data = (username, hashed_password)
    cursor.execute(insert_user_query, user_data)

# Function to log in a user
def login_user(cursor, username, password):
    cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
    user_data = cursor.fetchone()
    if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
        return user_data[0]
    return None

# Function to register an offline product
def register_offline_product(cursor, user_id):
    print("You chose offline product registration.")
    product_name = input("Enter the product name: ")
    seller = input("Enter the seller: ")
    purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
    warranty_period = input("Enter the warranty period in months: ")
    warranty_code = input("Enter the warranty code: ")
    purchase_bill_path = input("Enter the purchase bill path: ")

    insert_product_query = """
    INSERT INTO offline_product_registrations (user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    product_data = (user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path)
    cursor.execute(insert_product_query, product_data)
    print("Offline product registered successfully.")

# Function to register an online product
def register_online_product(cursor, user_id):
    print("You chose online product registration.")
    product_name = input("Enter the product name: ")
    purchase_date = input("Enter the purchase date (YYYY-MM-DD): ")
    warranty_period = input("Enter the warranty period in months: ")
    warranty_code = input("Enter the warranty code: ")
    source_url = input("Enter the source URL: ")

    insert_product_query = """
    INSERT INTO online_product_registrations (user_id, product_name, purchase_date, warranty_period, warranty_code, source_url)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    product_data = (user_id, product_name, purchase_date, warranty_period, warranty_code, source_url)
    cursor.execute(insert_product_query, product_data)
    print("Online product registered successfully.")

# Function to calculate the warranty expiry date
from datetime import datetime, timedelta


# Function to get the warranty expiry date
def get_warranty_expiry_date(purchase_date, warranty_period):
    # Convert the purchase_date to a datetime object
    purchase_date = datetime.combine(purchase_date, datetime.min.time())

    # Calculate the warranty expiry date
    expiry_date = purchase_date + timedelta(days=warranty_period * 30)

    # Calculate the remaining days
    remaining_days = (expiry_date - datetime.now()).days

    return f"{expiry_date.date()} ({remaining_days} days remaining)"


# Function to display all registered products along with warranty information
# Function to display all registered products along with warranty information
def display_registered_products(conn, cursor, user_id):
    select_offline_products_query = "SELECT id, product_name, purchase_date, warranty_period FROM offline_product_registrations WHERE user_id = %s"
    select_online_products_query = "SELECT id, product_name, purchase_date, warranty_period FROM online_product_registrations WHERE user_id = %s"

    cursor.execute(select_offline_products_query, (user_id,))
    offline_products = cursor.fetchall()

    cursor.execute(select_online_products_query, (user_id,))
    online_products = cursor.fetchall()

    print("\nRegistered Products:")
    print("\nOffline Products:")
    for product in offline_products:
        print(f"{product[0]}. {product[1]} - Warranty Expires on {get_warranty_expiry_date(product[2], product[3])}")

    print("\nOnline Products:")
    for product in online_products:
        print(f"{product[0]}. {product[1]} - Warranty Expires on {get_warranty_expiry_date(product[2], product[3])}")


# Main function
def main():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='daddy1234',
        database='datafix',
    )

    cursor = conn.cursor()

    create_offline_product_registration_table(cursor)
    create_online_product_registration_table(cursor)

    while True:
        print("\nWelcome to Product Registration App")
        print("Options:")
        print("1. Login")
        print("2. Register an Account")

        choice = input("Enter your choice (1/2): ")

        if choice == "1":
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            user_id = login_user(cursor, username, password)

            if user_id:
                print("Login successful.")
                while True:
                    display_menu()
                    choice = input("Enter your choice (1/2/3/4/5): ")

                    if choice == "1":
                        register_online_product(cursor, user_id)
                    elif choice == "2":
                        register_offline_product(cursor, user_id)
                    elif choice == "3":
                        set_warranty_reminders(cursor, user_id)
                    elif choice == "4":
                        display_registered_products(conn, cursor, user_id)
                    elif choice == "5":
                        print("Logout successful.")
                        break
                    else:
                        print("Invalid choice. Please choose 1, 2, 3, 4, or 5.")
            else:
                print("Login failed. Please check your credentials.")

        elif choice == "2":
            username = input("Enter a username: ")
            password = input("Enter a password: ")
            register_user(cursor, username, password)
            print("Account registered successfully.")

        else:
            print("Invalid choice. Please choose 1 or 2.")

    conn.close()

if __name__ == "__main__":
    main()
