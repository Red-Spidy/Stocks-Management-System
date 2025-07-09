import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_config import get_connection
import mysql.connector
import datetime
from tkinter import messagebox


def log_message(level, message):
    with open("signup_log.txt", "a") as log_file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] [{level}] {message}\n")


def signup():
    def register_user():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        confirm_password = confirm_password_entry.get().strip()
        role = role_var.get().strip()

        if not username or not password or not confirm_password or not role:
            messagebox.showerror("Error", "All fields are required.")
            log_message("ERROR", "All fields are required.")
            return

        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match.")
            log_message("ERROR", "Passwords do not match.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Username already exists.")
                log_message("ERROR", "Username already exists.")
                return

            # Create user in users table
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, password, role))

            if role == "Buyer":
                # Collect buyer details from the role-specific fields
                name = role_fields_frame.name_entry.get().strip()
                email = role_fields_frame.email_entry.get().strip()
                mobile = role_fields_frame.mobile_entry.get().strip()
                aadhar = role_fields_frame.aadhar_entry.get().strip()
                pan = role_fields_frame.pan_entry.get().strip()
                bank_account = role_fields_frame.bank_entry.get().strip()
                demat_account = role_fields_frame.demat_entry.get().strip()
                capital = role_fields_frame.capital_entry.get().strip()

                # Validate buyer fields
                if not all([name, email, mobile, aadhar, pan, bank_account, demat_account, capital]):
                    messagebox.showerror("Error", "All buyer fields are required.")
                    conn.rollback()
                    return

                try:
                    capital = float(capital)
                    if capital <= 0:
                        messagebox.showerror("Error", "Capital must be positive.")
                        conn.rollback()
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid capital amount.")
                    conn.rollback()
                    return

                # Get next BuyerId
                cursor.execute("SELECT MAX(BuyerId) FROM Buyer")
                max_id = cursor.fetchone()[0]
                buyer_id = (max_id or 0) + 1

                # Insert into Buyer table
                cursor.execute("""
                    INSERT INTO Buyer (BuyerId, Name, Email, MobileNumber, AadharId, 
                                     Capital, KYCStatus, PANNo, LinkedBankAccount, DematAccount, ProfitLoss)
                    VALUES (%s, %s, %s, %s, %s, %s, 'Pending', %s, %s, %s, 0)
                """, (buyer_id, name, email, mobile, aadhar, capital, pan, bank_account, demat_account))

                # Insert into Has table (mobile number)
                cursor.execute("INSERT INTO Has (BuyerId, MobileNumber) VALUES (%s, %s)",
                               (buyer_id, mobile))

                log_message("INFO", f"Buyer account created: {name} (ID: {buyer_id})")

            elif role == "Broker":
                # Collect broker details from the role-specific fields
                name = role_fields_frame.name_entry.get().strip()
                mobile = role_fields_frame.mobile_entry.get().strip()
                website = role_fields_frame.website_entry.get().strip()
                commission = role_fields_frame.commission_entry.get().strip()

                # Validate broker fields
                if not all([name, mobile, website, commission]):
                    messagebox.showerror("Error", "All broker fields are required.")
                    conn.rollback()
                    return

                try:
                    commission = float(commission)
                    if commission <= 0:
                        messagebox.showerror("Error", "Commission must be positive.")
                        conn.rollback()
                        return
                except ValueError:
                    messagebox.showerror("Error", "Invalid commission rate.")
                    conn.rollback()
                    return

                # Get next PlatformId
                cursor.execute("SELECT MAX(PlatformId) FROM BrokerPlatform")
                max_id = cursor.fetchone()[0]
                platform_id = (max_id or 0) + 1

                # Insert into BrokerPlatform table
                cursor.execute("""
                    INSERT INTO BrokerPlatform (PlatformId, Name, MobileNumber, Website, Commission)
                    VALUES (%s, %s, %s, %s, %s)
                """, (platform_id, name, mobile, website, commission))

                log_message("INFO", f"Broker account created: {name} (ID: {platform_id})")

            conn.commit()
            messagebox.showinfo("Success", "Account created successfully!")
            log_message("INFO", f"User {username} created successfully as {role}")
            signup_window.destroy()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            log_message("DB_ERROR", str(err))
            if 'conn' in locals():
                conn.rollback()
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def show_role_fields():
        # Clear previous role-specific fields
        for widget in role_fields_frame.winfo_children():
            widget.destroy()

        role = role_var.get()

        if role == "Buyer":
            # Buyer fields
            tb.Label(role_fields_frame, text="Full Name:").pack(pady=2)
            name_entry = tb.Entry(role_fields_frame)
            name_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Email:").pack(pady=2)
            email_entry = tb.Entry(role_fields_frame)
            email_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Mobile Number:").pack(pady=2)
            mobile_entry = tb.Entry(role_fields_frame)
            mobile_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Aadhar ID:").pack(pady=2)
            aadhar_entry = tb.Entry(role_fields_frame)
            aadhar_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="PAN Number:").pack(pady=2)
            pan_entry = tb.Entry(role_fields_frame)
            pan_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Bank Account:").pack(pady=2)
            bank_entry = tb.Entry(role_fields_frame)
            bank_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Demat Account:").pack(pady=2)
            demat_entry = tb.Entry(role_fields_frame)
            demat_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Initial Capital (₹):").pack(pady=2)
            capital_entry = tb.Entry(role_fields_frame)
            capital_entry.pack(pady=2)

            # Store references to entries
            role_fields_frame.name_entry = name_entry
            role_fields_frame.email_entry = email_entry
            role_fields_frame.mobile_entry = mobile_entry
            role_fields_frame.aadhar_entry = aadhar_entry
            role_fields_frame.pan_entry = pan_entry
            role_fields_frame.bank_entry = bank_entry
            role_fields_frame.demat_entry = demat_entry
            role_fields_frame.capital_entry = capital_entry

        elif role == "Broker":
            # Broker fields
            tb.Label(role_fields_frame, text="Broker Name:").pack(pady=2)
            name_entry = tb.Entry(role_fields_frame)
            name_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Mobile Number:").pack(pady=2)
            mobile_entry = tb.Entry(role_fields_frame)
            mobile_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Website:").pack(pady=2)
            website_entry = tb.Entry(role_fields_frame)
            website_entry.pack(pady=2)

            tb.Label(role_fields_frame, text="Commission Rate (%):").pack(pady=2)
            commission_entry = tb.Entry(role_fields_frame)
            commission_entry.pack(pady=2)

            # Store references to entries
            role_fields_frame.name_entry = name_entry
            role_fields_frame.mobile_entry = mobile_entry
            role_fields_frame.website_entry = website_entry
            role_fields_frame.commission_entry = commission_entry

    signup_window = tb.Toplevel()
    signup_window.title("Sign Up")
    signup_window.geometry("500x700")

    main_frame = tb.Frame(signup_window)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    tb.Label(main_frame, text="Create a New Account", font=("Helvetica", 14, "bold")).pack(pady=10)

    # Basic account info
    tb.Label(main_frame, text="Username:").pack(pady=2)
    username_entry = tb.Entry(main_frame)
    username_entry.pack(pady=2)

    tb.Label(main_frame, text="Password:").pack(pady=2)
    password_entry = tb.Entry(main_frame, show="*")
    password_entry.pack(pady=2)

    tb.Label(main_frame, text="Confirm Password:").pack(pady=2)
    confirm_password_entry = tb.Entry(main_frame, show="*")
    confirm_password_entry.pack(pady=2)

    tb.Label(main_frame, text="Register As:").pack(pady=2)
    role_var = tb.StringVar()
    role_combo = tb.Combobox(main_frame, textvariable=role_var,
                             values=["Buyer", "Broker"], state="readonly")
    role_combo.pack(pady=2)
    role_combo.current(0)
    role_combo.bind("<<ComboboxSelected>>", lambda e: show_role_fields())

    # Role-specific fields frame
    role_fields_frame = tb.Frame(main_frame)
    role_fields_frame.pack(fill="x", pady=10)

    # Show initial role fields
    show_role_fields()

    # Register button
    tb.Button(main_frame, text="Sign Up", command=register_user,
              bootstyle=SUCCESS).pack(pady=20)


if __name__ == "__main__":
    signup()