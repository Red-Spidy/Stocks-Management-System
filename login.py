import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from db_config import get_connection
from dashboard import open_dashboard
from signup import signup
import mysql.connector

def login():
    def validate_login():
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        role = role_var.get().strip()

        if not username or not password or not role:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s AND role = %s",
                           (username, password, role))
            result = cursor.fetchone()

            if result:
                messagebox.showinfo("Login Success", f"Welcome {username} ({role})!")
                login_window.destroy()
                open_dashboard(username, role)
            else:
                messagebox.showerror("Error", "Invalid credentials or role.")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def open_signup():
        login_window.withdraw()
        signup()
        login_window.deiconify()

    login_window = tb.Window(themename="darkly")
    login_window.title("Login")
    login_window.geometry("300x350")

    tb.Label(login_window, text="Username:").pack(pady=5)
    username_entry = tb.Entry(login_window)
    username_entry.pack(pady=5)

    tb.Label(login_window, text="Password:").pack(pady=5)
    password_entry = tb.Entry(login_window, show="*")
    password_entry.pack(pady=5)

    tb.Label(login_window, text="Login As:").pack(pady=5)
    role_var = tb.StringVar()
    role_combo = tb.Combobox(login_window, textvariable=role_var, values=["Buyer", "Broker"], state="readonly")
    role_combo.pack(pady=5)
    role_combo.current(0)

    tb.Button(login_window, text="Login", command=validate_login, bootstyle=SUCCESS).pack(pady=15)

    tb.Label(login_window, text="Don't have an account?").pack(pady=5)
    tb.Button(login_window, text="Sign Up", command=open_signup, bootstyle=INFO).pack()

    login_window.mainloop()

if __name__ == "__main__":
    login()