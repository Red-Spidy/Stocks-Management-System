import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from db_config import get_connection


def add_stock_window():
    def generate_stock_id():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(StockId) FROM Stocks")
            max_id = cursor.fetchone()[0]
            return (max_id or 0) + 1
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def save_stock():
        name = name_entry.get().strip()
        price = price_entry.get().strip()
        market_id = market_var.get().split(" - ")[0] if market_var.get() else ""
        broker_id = broker_var.get().split(" - ")[0] if broker_var.get() else ""
        indicator = indicator_entry.get().strip()
        delivery = delivery_var.get()
        quality = quality_entry.get().strip()
        lots = lots_entry.get().strip()
        quantity = qty_entry.get().strip()
        units = units_var.get()

        if not all([name, price, market_id, broker_id, indicator, delivery,
                    quality, lots, quantity, units]):
            messagebox.showerror("Error", "All fields are required")
            return

        conn = None
        cursor = None
        try:
            price = float(price)
            lots = int(lots)
            quantity = int(quantity)

            if price <= 0 or lots <= 0 or quantity <= 0:
                messagebox.showerror("Error", "Price, lots, and quantity must be positive")
                return

            stock_id = generate_stock_id()
            if stock_id is None:
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO Stocks (StockId, StockName, Price, BrokerId, MarketId)
                VALUES (%s, %s, %s, %s, %s)
            """, (stock_id, name, price, broker_id, market_id))

            cursor.execute("""
                INSERT INTO Types (StockId, Indicator, Delivery, Quality, Lots, Quantity, Units)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (stock_id, indicator, delivery, quality, lots, quantity, units))

            cursor.execute("""
                INSERT INTO Updates (StockId, PlatformId)
                VALUES (%s, %s)
            """, (stock_id, broker_id))

            conn.commit()
            messagebox.showinfo("Success", f"Stock added successfully!\nStock ID: {stock_id}")
            win.destroy()

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid number format: {e}")
        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # Create root window if it doesn't exist
    if not tk._default_root or not tk._default_root.winfo_exists():
        root = tk.Tk()
        root.withdraw()

    win = tb.Toplevel()
    win.title("Add New Stock")
    win.geometry("500x600")

    # Create container with standard tkinter Frame to avoid ttkbootstrap styling issues
    container = tk.Frame(win)
    container.pack(fill="both", expand=True)

    # Create canvas with standard tkinter Canvas
    canvas = tk.Canvas(container)
    canvas.pack(side="left", fill="both", expand=True)

    # Create scrollbar with standard tkinter Scrollbar (not ttk)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Create scrollable frame with ttkbootstrap for styling
    scrollable_frame = tb.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Form fields
    tb.Label(scrollable_frame, text="Stock Name:").pack(pady=2)
    name_entry = tb.Entry(scrollable_frame)
    name_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Price:").pack(pady=2)
    price_entry = tb.Entry(scrollable_frame)
    price_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Market:").pack(pady=2)
    market_var = tb.StringVar()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MarketId, CONCAT(Type, ' (', Country, ')') FROM Market")
        markets = cursor.fetchall()
        market_combo = tb.Combobox(scrollable_frame, textvariable=market_var,
                                 values=[f"{m[0]} - {m[1]}" for m in markets])
        market_combo.pack(pady=2)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    tb.Label(scrollable_frame, text="Broker Platform:").pack(pady=2)
    broker_var = tb.StringVar()
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT PlatformId, Name FROM BrokerPlatform")
        brokers = cursor.fetchall()
        broker_combo = tb.Combobox(scrollable_frame, textvariable=broker_var,
                                 values=[f"{b[0]} - {b[1]}" for b in brokers])
        broker_combo.pack(pady=2)
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    tb.Label(scrollable_frame, text="Indicator:").pack(pady=2)
    indicator_entry = tb.Entry(scrollable_frame)
    indicator_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Delivery:").pack(pady=2)
    delivery_var = tb.StringVar()
    delivery_combo = tb.Combobox(scrollable_frame, textvariable=delivery_var,
                               values=["Intraday", "Delivery"])
    delivery_combo.pack(pady=2)
    delivery_combo.current(0)

    tb.Label(scrollable_frame, text="Quality:").pack(pady=2)
    quality_entry = tb.Entry(scrollable_frame)
    quality_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Lots:").pack(pady=2)
    lots_entry = tb.Entry(scrollable_frame)
    lots_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Total Quantity:").pack(pady=2)
    qty_entry = tb.Entry(scrollable_frame)
    qty_entry.pack(pady=2)

    tb.Label(scrollable_frame, text="Units:").pack(pady=2)
    units_var = tb.StringVar()
    units_combo = tb.Combobox(scrollable_frame, textvariable=units_var,
                            values=["Shares", "Kg", "Lots"])
    units_combo.pack(pady=2)
    units_combo.current(0)

    tb.Button(scrollable_frame, text="Save", command=save_stock, bootstyle=SUCCESS).pack(pady=10)

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)


def update_stock_price_window(stock_id, current_price):
    def save_price():
        conn = None
        cursor = None
        try:
            new_price = float(price_entry.get())
            if new_price <= 0:
                messagebox.showerror("Error", "Price must be positive")
                return

            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE Stocks SET Price = %s
                WHERE StockId = %s
            """, (new_price, stock_id))

            conn.commit()
            messagebox.showinfo("Success", "Price updated successfully!")
            win.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid price format")
        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    win = tb.Toplevel()
    win.title("Update Stock Price")
    win.geometry("300x200")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT StockName FROM Stocks WHERE StockId = %s", (stock_id,))
        stock_name = cursor.fetchone()[0]
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        stock_name = "Unknown"
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()

    tb.Label(win, text=f"Stock: {stock_name} (ID: {stock_id})").pack(pady=5)
    tb.Label(win, text=f"Current Price: ₹{current_price:.2f}").pack(pady=5)

    tb.Label(win, text="New Price:").pack(pady=5)
    price_entry = tb.Entry(win)
    price_entry.pack(pady=5)

    tb.Button(win, text="Update", command=save_price, bootstyle=PRIMARY).pack(pady=10)


def delete_stock_window(stock_id, stock_name):
    def confirm_delete():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM Portfolio WHERE StockId = %s", (stock_id,))
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Cannot delete stock - it exists in portfolios")
                return

            cursor.execute("DELETE FROM Types WHERE StockId = %s", (stock_id,))
            cursor.execute("DELETE FROM Updates WHERE StockId = %s", (stock_id,))
            cursor.execute("DELETE FROM Stocks WHERE StockId = %s", (stock_id,))

            conn.commit()
            messagebox.showinfo("Success", f"Stock {stock_name} deleted")
            win.destroy()

        except mysql.connector.Error as err:
            if conn and conn.is_connected():
                conn.rollback()
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    win = tb.Toplevel()
    win.title("Confirm Deletion")
    win.geometry("400x150")

    tb.Label(win, text=f"Are you sure you want to delete {stock_name} (ID: {stock_id})?",
             font=("Helvetica", 12)).pack(pady=10)

    btn_frame = tb.Frame(win)
    btn_frame.pack(pady=10)

    tb.Button(btn_frame, text="Cancel", command=win.destroy, bootstyle=SECONDARY).pack(side="left", padx=10)
    tb.Button(btn_frame, text="Delete", command=confirm_delete, bootstyle=DANGER).pack(side="left", padx=10)