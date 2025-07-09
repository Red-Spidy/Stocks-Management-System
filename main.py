### db_config.py
import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Red_Spidy",
        database="Stock_Management"
    )


### login.py
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from db_config import get_connection
from dashboard import open_dashboard

def login_window():
    root = ttk.Window(themename="darkly")
    root.title("Login")
    root.geometry("300x250")

    ttk.Label(root, text="Username").pack(pady=5)
    user_entry = ttk.Entry(root)
    user_entry.pack()

    ttk.Label(root, text="Password").pack(pady=5)
    pass_entry = ttk.Entry(root, show="*")
    pass_entry.pack()

    def login():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s",
                       (user_entry.get(), pass_entry.get()))
        result = cursor.fetchone()
        if result:
            root.destroy()
            open_dashboard(user_entry.get())
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    ttk.Button(root, text="Login", command=login, bootstyle="success").pack(pady=15)
    root.mainloop()


### dashboard.py
import tkinter as tk
import ttkbootstrap as ttk
from buyers import open_buyer_window
from stocks import open_stock_window
from portfolio import open_portfolio_window

def open_dashboard(username):
    root = ttk.Window(themename="cyborg")
    root.title("Stock Management Dashboard")
    root.geometry("500x300")

    ttk.Label(root, text=f"Welcome {username}", font=("Helvetica", 16)).pack(pady=10)
    ttk.Button(root, text="Manage Buyers", command=open_buyer_window).pack(pady=5)
    ttk.Button(root, text="Manage Stocks", command=open_stock_window).pack(pady=5)
    ttk.Button(root, text="View Portfolio", command=open_portfolio_window).pack(pady=5)

    root.mainloop()


### buyers.py
import tkinter as tk
import ttkbootstrap as ttk
from db_config import get_connection

def open_buyer_window():
    win = ttk.Toplevel()
    win.title("Buyers")
    win.geometry("500x400")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Buyer")
    records = cursor.fetchall()

    ttk.Label(win, text="Buyers List", font=("Arial", 14)).pack(pady=10)
    for rec in records:
        ttk.Label(win, text=f"{rec[1]} | ₹{rec[5]}").pack()

    conn.close()


### stocks.py
import tkinter as tk
import ttkbootstrap as ttk
from db_config import get_connection

def open_stock_window():
    win = ttk.Toplevel()
    win.title("Stocks")
    win.geometry("500x400")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Stocks")
    records = cursor.fetchall()

    ttk.Label(win, text="Stocks List", font=("Arial", 14)).pack(pady=10)
    for rec in records:
        ttk.Label(win, text=f"{rec[1]} | ₹{rec[2]}").pack()

    conn.close()


### portfolio.py
import tkinter as tk
import ttkbootstrap as ttk
from db_config import get_connection

def open_portfolio_window():
    win = ttk.Toplevel()
    win.title("Portfolio")
    win.geometry("500x400")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT Portfolio.BuyerId, Buyer.Name, Portfolio.StockId, Portfolio.Quantity, Portfolio.PurchasePrice FROM Portfolio JOIN Buyer ON Portfolio.BuyerId = Buyer.BuyerId")
    records = cursor.fetchall()

    ttk.Label(win, text="Portfolio List", font=("Arial", 14)).pack(pady=10)
    for rec in records:
        ttk.Label(win, text=f"{rec[1]} owns {rec[3]} of Stock {rec[2]} at ₹{rec[4]}").pack()

    conn.close()


### main.py
from login import login

if __name__ == "__main__":
    login()
