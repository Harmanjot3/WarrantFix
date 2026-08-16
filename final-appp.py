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
import tkinter as tk
from PIL import Image, ImageTk
from functools import partial
from tkinter import simpledialog, messagebox

#img1 = Image.open("images/black.jpg")
#img_s = img1.resize((500,500))

# Function to set warranty reminders for a user
# Twilio credentials (replace with your own values)
TWILIO_ACCOUNT_SID = "AC51802bca71499b6da25284cf0471f8ef"
TWILIO_AUTH_TOKEN = "57de58d69e299a2151ac4144c646b6f4"
TWILIO_PHONE_NUMBER = "+13343842190"
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


def set_warranty_reminders():
    user_id = simpledialog.askstring("Enter:", "Enter the user ID:")
    user_name = simpledialog.askstring("Enter:", "The user name:")
    try:
        with conn.cursor() as cursor:
            # Fetch user's phone number
            cursor.execute("SELECT phone_number FROM users WHERE user_name = %s", (user_name,))
            user_data = cursor.fetchone()
            if not user_data:
                messagebox.showwarning("Warning", "Not available")
                return

            user_phone_number = user_data[0]

            # Ask user for the interval
            try:
                interval_days = simpledialog.askstring("Enter", "The interval days")
            except ValueError:
                messagebox.showwarning("Warning", "Not possible")
                return

            # Fetch product details from both offline and online product tables
            cursor.execute("""
                SELECT product_name, purchase_date, warranty_period
                FROM offline_product_registrations
                WHERE user_id = %s
                UNION
                SELECT product_name, purchase_date, warranty_period
                FROM online_product_registrations
                WHERE user_id = %s
            """, (user_id, user_id))
            products = cursor.fetchall()

            for product in products:
                product_name, purchase_date, warranty_period = product

                # Check if purchase_date is a string and convert it to a date object if necessary
                if isinstance(purchase_date, str):
                    purchase_date = datetime.strptime(purchase_date, "%Y-%m-%d").date()
                elif not isinstance(purchase_date, date):
                    messagebox.showwarning("Warning", "Unable to do...")
                    continue

                # Calculate warranty expiry date
                warranty_expiry_date = purchase_date + relativedelta(months=warranty_period)
                expiry_date_str = warranty_expiry_date.strftime("%Y-%m-%d")

                # Send acknowledgment message for each product
                ack_message = (f"Reminder set for {product_name}. Warranty valid until {expiry_date_str}. "
                               f"Next reminder in {interval_days} days.")
                send_twilio_sms(ack_message, user_phone_number)

                # Schedule the warranty reminders for each product
                schedule.every(interval_days).days.do(
                    send_twilio_sms, f"Warranty Reminder for {product_name}: Check your warranty.", user_phone_number
                )
                scheduler_thread = threading.Thread(target=run_scheduler)
                scheduler_thread.daemon = True  # Makes the thread exit when the main program exits
                scheduler_thread.start()

                messagebox.showinfo("Success", "Messages have been sent.")

            else:
                messagebox.showinfo(".", ".")

    except mysql.connector.Error as err:
        messagebox.showinfo("Database error")

# Function to display loading animation
def loading_animation():
    for _ in range(10):
        print(".", end="", flush=True)
        time.sleep(0.5)

# Function to display the welcome message and menu
def display_menu():
    root = tk.Tk()
    root.title("Shopping App")
    root.maxsize(500,500)
    
    canvas = tk.Canvas(root, bg = "black", height = 500, width = 500)
    canvas.pack()

    welcome = tk.Label(root, text="Registration", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)

#online reg
    uname = tk.Label(root, text = "Username", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    uname.place(x = 200, y = 140)

    uname_fill = tk.Entry(root, relief="sunken")
    uname_fill.place(x = 200, y = 185)

    password = tk.Label(root, text = "Password", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    password.place(x = 200, y = 235)

    password_fill = tk.Entry(root, relief="sunken")
    password_fill.place(x = 200, y = 280)

    email = tk.Label(root, text = "Email", relief="raised",
                width = 20, height = 2, font = ("Segoe UI", 8))
    email.place(x = 200, y = 320)

    email = tk.Entry(root, relief="sunken")
    email.place(x = 200, y = 360)

    phone_number = tk.Label(root, text = "Phone", relief="raised",
                width = 20, height = 2, font = ("Segoe UI", 8))
    phone_number.place(x = 200, y = 390)

    phone_number = tk.Entry(root, relief="sunken")
    phone_number.place(x = 200, y = 430)

    root.mainloop()

# Create a MySQL database connection
conn = mysql.connector.connect(
    host='localhost',
    user = 'root',
    password = 'daddy1234',
    database = 'datafix'
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
    def submit_registration():
        username = usern.get()
        password = password1.get()
        email = email_id.get()
        phone_number = phone_no.get()

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            with conn.cursor() as cursor:
                insert_user_query = "INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)"
                user_data = (username, hashed_password.decode('utf-8'), email, phone_number)
                cursor.execute(insert_user_query, user_data)
                conn.commit()
                messagebox.showinfo("Success", "Account registered successfully.")
                root.destroy()
        except mysql.connector.Error as err:
            messagebox.showwarning("Database error", str(err))

    root = tk.Tk()
    root.title("Register User")
    root.maxsize(500,500)
    
    canvas = tk.Canvas(root, bg = "black", height = 500, width = 500)
    canvas.pack()
    
    usern = tk.StringVar()
    password1 = tk.StringVar()
    email_id = tk.StringVar()
    phone_no = tk.StringVar()

    welcome = tk.Label(root, text="Registration", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)

    #online reg
    uname = tk.Label(root, text = "Username", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    uname.place(x = 200, y = 140)

    uname_fill = tk.Entry(root, textvariable=usern, relief="sunken")
    uname_fill.place(x = 200, y = 185)

    password = tk.Label(root, text = "Password", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    password.place(x = 200, y = 235)

    password_fill = tk.Entry(root,textvariable=password1, relief="sunken")
    password_fill.place(x = 200, y = 280)

    email = tk.Label(root, text = "Email", relief="raised",
                width = 20, height = 2, font = ("Segoe UI", 8))
    email.place(x = 200, y = 320)

    email = tk.Entry(root,textvariable=email_id, relief="sunken")
    email.place(x = 200, y = 360)

    phone_number = tk.Label(root, text = "Phone", relief="raised",
                width = 20, height = 2, font = ("Segoe UI", 8))
    phone_number.place(x = 200, y = 390)

    phone_number = tk.Entry(root, textvariable=phone_no, relief="sunken")
    phone_number.place(x = 200, y = 430)
    
    submission = tk.Button(root, text = "SUBMIT", relief="raised", bg="yellow",
                width = 20, height = 2, font = ("Segoe UI", 8), command = submit_registration)

    submission.place(x = 200, y = 460)

    root.mainloop()



# Function to log in a user
def login_user():
    def submit_login():
        username = username_entry.get()
        password = password_entry.get()

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                    messagebox.showinfo("Success", "Login successful.")
                    root.destroy()
                else:
                    messagebox.showwarning("Failed", "Login failed. Please check your credentials.")
        except mysql.connector.Error as err:
            messagebox.showwarning("Database error", str(err))
            
        user_menu()

    root = tk.Tk()
    root.title("Login User")
    root.maxsize(500,500)
    
    canvas = tk.Canvas(root, bg = "black", height = 500, width = 500)
    canvas.pack()
    username_entry = tk.StringVar()
    password_entry = tk.StringVar()

    


    welcome = tk.Label(root, text="Login", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)

#online reg
    uname1 = tk.Label(root, text = "Username", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    uname1.place(x = 200, y = 140)

    uname_fill1 = tk.Entry(root,textvariable=username_entry, relief="sunken")
    uname_fill1.place(x = 200, y = 185)

    password1 = tk.Label(root, text = "Password", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8))
    password1.place(x = 200, y = 235)

    password_fill1 = tk.Entry(root,textvariable=password_entry, relief="sunken")
    password_fill1.place(x = 200, y = 280)


    submit_button = tk.Button(root, text = "Submit", relief = "raised", bg="cyan", width = 20,
                          height = 2, font = ("Segoe UI", 8), command = submit_login)
    submit_button.place(x = 200, y = 350)

    root.mainloop()


# Function to register an offline product
def register_offline_product():

    root = tk.Tk()
    root.title("Offline Registration")
    root.maxsize(600, 600)

    user_id = simpledialog.askstring("Enter", "User ID:")
    prodname = tk.StringVar()
    sellername = tk.StringVar()
    pdatename = tk.StringVar()
    warrantyname = tk.StringVar()
    war_code = tk.StringVar()
    purchasebill = tk.StringVar()

    canvas = tk.Canvas(root, bg="black", height=600, width=600)
    canvas.pack()

    welcome = tk.Label(root, text="Offline Product Registration", bg="yellow", relief="raised",
                   width=30, height=3, font=("Segoe UI", 12))
    welcome.place(x=140, y=30)

    prod_name = tk.Label(root, text = "Product Name:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    prod_name.place(x = 140, y = 130)

    prod_entry = tk.Entry(root,textvariable=prodname, relief="sunken", font = ("Segoe UI", 8))
    prod_entry.place(x = 350, y = 135)

    seller = tk.Label(root, text = "Seller:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    seller_entry = tk.Entry(root, textvariable = sellername, relief="sunken", font = ("Segoe UI", 8))
    seller.place(x = 140, y = 180)
    seller_entry.place(x = 350, y = 185)

    pdate = tk.Label(root, text = "Purchase date:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    pdate_entry = tk.Entry(root, relief="sunken", font = ("Segoe UI", 8))
    pdate.place(x = 140, y = 230)
    pdate_entry.place(x = 350, y = 237)

    warranty = tk.Label(root, text = "Warranty period:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    warranty_entry = tk.Entry(root,textvariable=warrantyname, relief="sunken", font = ("Segoe UI", 8))

    warranty.place(x = 140, y = 280)
    warranty_entry.place(x = 350, y = 287)


    warranty_code = tk.Label(root, text = "Warranty code:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    warranty_code_e = tk.Entry(root,textvariable=war_code, relief="sunken", font = ("Segoe UI", 8))

    warranty_code.place(x = 140, y = 330)
    warranty_code_e.place(x = 350, y = 338)

    purchase_bill_path = tk.Label(root, text="Purchase Bill Path:", bg="white", relief="raised",
                               width=30, height=3, font=("Segoe UI", 8))
    purchase_bill_entry = tk.Entry(root, textvariable=purchasebill, relief="sunken", font=("Segoe UI", 8))
    purchase_bill_path.place(x=140, y=390)
    purchase_bill_entry.place(x=350, y=394)


    def offlineReg(user_id, product_name, seller, warranty_period, warranty_code):
        user_id = str(user_id)
        product_name = str(product_name.get())
        seller = str(seller.get())
        warranty_period = int(3)
        warranty_code = str(warranty_code.get())
        
        conn = mysql.connector.connect(
            host='localhost',
            user = 'root',
            password = 'Daddy1234',
            database = 'datafix'
        )

# Create a cursor to execute SQL queries
        cursor = conn.cursor()

        insert_product_query = """
        INSERT INTO offline_product_registrations (user_id, product_name, seller, warranty_period, warranty_code)
        VALUES (%s, %s, %s, %s, %s)
        """

        product_data = (user_id, product_name, seller, warranty_period, warranty_code)

        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_product_query, product_data)
                conn.commit()
                messagebox.showinfo("Successful!", "Registration successful!")
        except mysql.connector.Error as err:
                messagebox.showwarning("Error", f"Error: {err}")
        finally:
            cursor.close()  # Close the cursor in the finally block to avoid the "unread result found" warning



    offlineReg = partial(offlineReg, user_id, prodname, sellername, warrantyname, war_code)

    submit_button = tk.Button(root, text="Submit", bg="yellow",
                          relief="raised", width=30, height=2, font=("Segoe UI", 9), command=offlineReg)

    submit_button.place(x=140, y=450)

    root.mainloop()


# Function to register an online product
def register_online_product():
    root = tk.Tk()
    root.title("Online Registration")
    root.maxsize(600,600)

    product = tk.StringVar()
    sellern = tk.StringVar()
    pdateval = tk.StringVar()
    warrantyval = tk.StringVar()
    war_code = tk.StringVar()
    source_url_entry1 = tk.StringVar()
    
    user_id = simpledialog.askstring("Enter", "Enter")
    
    canvas = tk.Canvas(root, bg = "black", height = 600, width = 600)
    canvas.pack()

    welcome = tk.Label(root, text = "Online Product Registration", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)

    prod_name = tk.Label(root, text = "Product Name:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    prod_name.place(x = 140, y = 130)

    prod_entry = tk.Entry(root, textvariable=product, relief="sunken", font = ("Segoe UI", 8))
    prod_entry.place(x = 350, y = 135)

    seller = tk.Label(root, text = "Seller:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    seller_entry = tk.Entry(root, textvariable=sellern, relief="sunken", font = ("Segoe UI", 8))
    seller.place(x = 140, y = 180)
    seller_entry.place(x = 350, y = 185)

    pdate = tk.Label(root, text = "Purchase date:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    pdate_entry = tk.Entry(root, textvariable=pdateval, relief="sunken", font = ("Segoe UI", 8))
    pdate.place(x = 140, y = 230)
    pdate_entry.place(x = 350, y = 237)

    warranty = tk.Label(root, text = "Warranty period:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    warranty_entry = tk.Entry(root,textvariable=warrantyval, relief="sunken", font = ("Segoe UI", 8))

    warranty.place(x = 140, y = 280)
    warranty_entry.place(x = 350, y = 287)


    warranty_code = tk.Label(root, text = "Warranty code:", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    warranty_code_e = tk.Entry(root,textvariable=war_code, relief="sunken", font = ("Segoe UI", 8))

    warranty_code.place(x = 140, y = 330)
    warranty_code_e.place(x = 350, y = 338)

    source_url = tk.Label(root, text = "Source URL", bg = "white", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 8))
    source_url_entry = tk.Entry(root,textvariable=source_url_entry1, relief="sunken", font = ("Segoe UI", 8))
    source_url.place(x = 140, y = 390)
    source_url_entry.place(x = 350, y = 394)
    
    
    def online_prod(user_id, product_name, warranty_period, warranty_code, source_url):
        
        user_id = str(user_id)
        product_name = str(product_name.get())
        warranty_period = str(3)
        warranty_code = str(warranty_code.get())
        source_url = str(source_url.get())
        
        conn = mysql.connector.connect(
            host='localhost',  # Change to the address of your local MySQL server
            user='root',  # Use your MySQL 'root' user
            password='daddy1234',  # Replace with your MySQL root password
            database='datafix',
        )

# Create a cursor to execute SQL
        cursor = conn.cursor()
        
        insert_product_query = """
                INSERT INTO online_product_registrations (user_id, product_name, warranty_period, warranty_code, source_url)
                VALUES (%s, %s, %s, %s, %s)
                """

        product_data = (user_id, product_name, warranty_period, warranty_code, source_url)

        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_product_query, product_data)
                conn.commit()
                messagebox.showinfo("Successful", "Done")
            
        except mysql.connector.Error as err:
            messagebox.showwarning("Warning", f"{err}")
        
    online_prod = partial(online_prod, user_id,  product, warrantyval, war_code, source_url_entry1)

    submit_button = tk.Button(root, text = "Submit", bg = "yellow", 
                          relief = "raised", width = 30, height = 2, font = ("Segoe UI", 9), command = online_prod)

    submit_button.place(x = 140, y = 450)


    root.mainloop()

    

# Function to display registered products
def display_registered_products(user_id):
    print("Registered Products:")
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT product_name, purchase_date, warranty_code, source_url FROM online_product_registrations WHERE user_id = %s", (user_id,))
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

    root = tk.Tk()
    root.title("Main App")
    root.minsize(500,500)
    #ims = ImageTk.PhotoImage(img_s)
    #iml = tk.Label(root, image = ims)
    #iml.pack()
    
    welcome = tk.Label(root, text="Welcome", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)
    
    login = tk.Button(root, text = "Login", relief="raised",
                       width = 20, height = 2, font = ("Segoe UI", 8), command = login_user)
    login.place(x = 200, y = 140)
    
    register = tk.Button(root, text = "Register", relief = "raised",
                         width = 20, height = 2, font = ("Segoe UI", 8), command = register_user)
    register.place(x = 200, y = 180)
    
    root.mainloop()
    


def user_menu():
    
    root = tk.Tk()
    root.title("Shopping App")
    root.maxsize(500,500)
    canvas = tk.Canvas(root, bg = "black", height = 500, width = 500)
    canvas.pack()

    welcome = tk.Label(root, text="Welcome to warranty registration app", bg = "yellow", relief="raised",
                   width = 30, height = 3, font = ("Segoe UI", 12))
    welcome.place(x = 140, y = 30)

    #online reg
    online_reg = tk.Button(root, text = "Register products online", relief="raised",
                       width = 20, height = 3, font = ("Segoe UI", 9), command = register_online_product)
    online_reg.place(x = 200, y = 150)

    #offline reg
    offline_reg = tk.Button(root, text = "Register products offline", relief="raised",
                       width = 20, height = 3, font = ("Segoe UI", 9), command = register_offline_product)
    offline_reg.place(x = 200, y = 210)

    #warranty
    warranty = tk.Button(root, text = "Set Warranty Reminders", relief="raised",
                       width = 20, height = 3, font = ("Segoe UI", 9), command = set_warranty_reminders)
    warranty.place(x = 200, y = 270)

    #registered
    registered = tk.Button(root, text = "Select Registered", relief="raised",
                       width = 20, height = 3, font = ("Segoe UI", 9))
    registered.place(x = 200, y = 330)

    #logout
    logout = tk.Button(root, text = "Logout", relief="raised",
                       width = 20, height = 3, font = ("Segoe UI", 9), command = main)
    logout.place(x = 200, y = 390)

    root.mainloop()

if __name__ == "__main__":
    main()