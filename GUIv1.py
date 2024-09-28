import tkinter as tk
import time,datetime
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
import mysql.connector
import bcrypt
import threading
import schedule
from twilio.rest import Client
from tkinter.scrolledtext import ScrolledText

# Twilio credentials
TWILIO_ACCOUNT_SID = "AC51802bca71499b6da25284cf0471f8ef"
TWILIO_AUTH_TOKEN = "52b60c7c7908159902d45132cef217e1"
TWILIO_PHONE_NUMBER = "+15109534342"
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Connect to MySQL database
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='daddy',
    database='datafix',
)

# Function to run the scheduler for sending reminders
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Function to send SMS using Twilio
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

# Main application class
class ProductRegistrationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Product Registration App")
        self.geometry("400x400")
        self.user_id = None
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_window()
        tk.Label(self, text="Username").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        tk.Label(self, text="Password").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        tk.Button(self, text="Login", command=self.login_user).pack()
        tk.Button(self, text="Register", command=self.create_registration_screen).pack()

    def create_registration_screen(self):
        self.clear_window()
        tk.Label(self, text="Username").pack()
        self.username_entry = tk.Entry(self)
        self.username_entry.pack()
        tk.Label(self, text="Password").pack()
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        tk.Label(self, text="Email").pack()
        self.email_entry = tk.Entry(self)
        self.email_entry.pack()
        tk.Label(self, text="Phone Number").pack()
        self.phone_entry = tk.Entry(self)
        self.phone_entry.pack()
        tk.Button(self, text="Register", command=self.register_user).pack()
        tk.Button(self, text="Back to Login", command=self.create_login_screen).pack()

    def login_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                user_data = cursor.fetchone()
                if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                    messagebox.showinfo("Login", "Login successful")
                    self.user_id = user_data[0]
                    self.create_main_menu()
                else:
                    messagebox.showerror("Error", "Invalid credentials")
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    def register_user(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        email = self.email_entry.get()
        phone_number = self.phone_entry.get()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        insert_user_query = "INSERT INTO users (username, password, email, phone_number) VALUES (%s, %s, %s, %s)"
        user_data = (username, hashed_password, email, phone_number)
        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_user_query, user_data)
                conn.commit()
                messagebox.showinfo("Success", "Account registered successfully")
                self.create_login_screen()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    def create_main_menu(self):
        self.clear_window()
        tk.Button(self, text="Register Product", command=self.create_product_registration_screen).pack()
        tk.Button(self, text="Set Warranty Reminders", command=self.create_warranty_reminder_screen).pack()
        tk.Button(self, text="Display Registered Products", command=self.display_registered_products).pack()
        tk.Button(self, text="Logout", command=self.logout).pack()

    def create_product_registration_screen(self):
        self.clear_window()

        tk.Label(self, text="Product Name").pack()
        self.product_name_entry = tk.Entry(self)
        self.product_name_entry.pack()

        tk.Label(self, text="Purchase Date (YYYY-MM-DD)").pack()
        self.purchase_date_entry = tk.Entry(self)
        self.purchase_date_entry.pack()

        tk.Label(self, text="Warranty Period (Months)").pack()
        self.warranty_period_entry = tk.Entry(self)
        self.warranty_period_entry.pack()

        tk.Label(self, text="Warranty Code").pack()
        self.warranty_code_entry = tk.Entry(self)
        self.warranty_code_entry.pack()

        self.registration_type = tk.StringVar(value="offline")
        tk.Label(self, text="Is the product registered online or offline?").pack()
        tk.Radiobutton(self, text="Offline", variable=self.registration_type, value="offline", command=self.toggle_registration_type).pack()
        tk.Radiobutton(self, text="Online", variable=self.registration_type, value="online", command=self.toggle_registration_type).pack()

        self.seller_label = tk.Label(self, text="Seller")
        self.seller_label.pack()
        self.seller_entry = tk.Entry(self)
        self.seller_entry.pack()

        self.purchase_bill_label = tk.Label(self, text="Purchase Bill Path")
        self.purchase_bill_label.pack()
        self.purchase_bill_entry = tk.Entry(self)
        self.purchase_bill_entry.pack()

        self.source_url_label = tk.Label(self, text="Source URL")
        self.source_url_label.pack_forget()
        self.source_url_entry = tk.Entry(self)
        self.source_url_entry.pack_forget()

        tk.Button(self, text="Register", command=self.register_product).pack()
        tk.Button(self, text="Back", command=self.create_main_menu).pack()

    def toggle_registration_type(self):
        if self.registration_type.get() == "online":
            self.seller_label.pack_forget()
            self.seller_entry.pack_forget()
            self.purchase_bill_label.pack_forget()
            self.purchase_bill_entry.pack_forget()
            self.source_url_label.pack()
            self.source_url_entry.pack()
        else:
            self.seller_label.pack()
            self.seller_entry.pack()
            self.purchase_bill_label.pack()
            self.purchase_bill_entry.pack()
            self.source_url_label.pack_forget()
            self.source_url_entry.pack_forget()

    def register_product(self):
        product_name = self.product_name_entry.get()
        purchase_date = self.purchase_date_entry.get()
        warranty_period = self.warranty_period_entry.get()
        warranty_code = self.warranty_code_entry.get()

        if self.registration_type.get() == "online":
            seller = None
            purchase_bill_path = None
            source_url = self.source_url_entry.get()
        else:
            seller = self.seller_entry.get()
            purchase_bill_path = self.purchase_bill_entry.get()
            source_url = None

        insert_product_query = """
        INSERT INTO offline_product_registrations (
            user_id, product_name, seller, purchase_date, warranty_period, warranty_code,
            purchase_bill_path, source_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        product_data = (
            self.user_id, product_name, seller, purchase_date, warranty_period, warranty_code, purchase_bill_path, source_url)

        try:
            with conn.cursor() as cursor:
                cursor.execute(insert_product_query, product_data)
                conn.commit()
                messagebox.showinfo("Success", "Product registered successfully")
                self.create_main_menu()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    def create_warranty_reminder_screen(self):
        self.clear_window()

        tk.Label(self, text="Reminder Interval (in days)").pack()
        self.interval_days_entry = tk.Entry(self)
        self.interval_days_entry.pack()

        tk.Button(self, text="Set Reminders", command=self.set_warranty_reminders).pack()
        tk.Button(self, text="Back", command=self.create_main_menu).pack()

    def set_warranty_reminders(self):
        interval_days = self.interval_days_entry.get()

        try:
            interval_days = int(interval_days)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number for days.")
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT phone_number FROM users WHERE id = %s", (self.user_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    messagebox.showerror("Error", "User not found")
                    return

                user_phone_number = user_data[0]
                cursor.execute("""
                    SELECT product_name, purchase_date, warranty_period
                    FROM offline_product_registrations
                    WHERE user_id = %s
                """, (self.user_id,))
                products = cursor.fetchall()

                if not products:
                    messagebox.showerror("Error", "No products found for reminders")
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

                    schedule.every(interval_days).days.do(
                        send_twilio_sms, f"Warranty Reminder for {product_name}: Check your warranty.", user_phone_number
                    )

                # Check if scheduler thread is running
                if not any(t.name == 'SchedulerThread' for t in threading.enumerate()):
                    scheduler_thread = threading.Thread(target=run_scheduler, name='SchedulerThread')
                    scheduler_thread.daemon = True
                    scheduler_thread.start()

                messagebox.showinfo("Success", "Warranty reminders have been set for all products.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def display_registered_products(self):
        self.clear_window()

        text_box = ScrolledText(self, width=50, height=20)
        text_box.pack(pady=10)

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT product_name, seller, purchase_date, warranty_code, purchase_bill_path, source_url
                    FROM offline_product_registrations
                    WHERE user_id = %s
                """, (self.user_id,))
                products = cursor.fetchall()

                if not products:
                    text_box.insert(tk.END, "No products found.\n")
                else:
                    for product in products:
                        product_name, seller, purchase_date, warranty_code, purchase_bill_path, source_url = product
                        if source_url:
                            text_box.insert(tk.END, f"Online Product:\n")
                            text_box.insert(tk.END, f"  Name: {product_name}\n")
                            text_box.insert(tk.END, f"  Purchase Date: {purchase_date}\n")
                            text_box.insert(tk.END, f"  Warranty Code: {warranty_code}\n")
                            text_box.insert(tk.END, f"  Source URL: {source_url}\n\n")
                        else:
                            text_box.insert(tk.END, f"Offline Product:\n")
                            text_box.insert(tk.END, f"  Name: {product_name}\n")
                            text_box.insert(tk.END, f"  Seller: {seller}\n")
                            text_box.insert(tk.END, f"  Purchase Date: {purchase_date}\n")
                            text_box.insert(tk.END, f"  Warranty Code: {warranty_code}\n")
                            text_box.insert(tk.END, f"  Bill Path: {purchase_bill_path}\n\n")

        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

        tk.Button(self, text="Back", command=self.create_main_menu).pack()

    def logout(self):
        self.create_login_screen()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = ProductRegistrationApp()
    app.mainloop()
