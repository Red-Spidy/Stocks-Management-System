import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_config import get_connection
from tkinter import messagebox
import mysql.connector
from stock_management import add_stock_window, update_stock_price_window, delete_stock_window
from datetime import datetime

def execute_transaction(buyer_id, tree, action, refresh_callback):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Please select a stock")
        return

    stock_id = selected[0]

    dialog = tb.Toplevel()
    dialog.title(f"{action} Stock")
    dialog.geometry("350x300")

    def get_stock_info():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT s.StockName, s.Price, t.Quantity 
                FROM Stocks s
                JOIN Types t ON s.StockId = t.StockId
                WHERE s.StockId = %s
            """, (stock_id,))
            return cursor.fetchone()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return None
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def get_owned_quantity():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Quantity FROM Portfolio WHERE BuyerId = %s AND StockId = %s",
                         (buyer_id, stock_id))
            result = cursor.fetchone()
            return result[0] if result else 0
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            return 0
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    stock_info = get_stock_info()
    if not stock_info:
        dialog.destroy()
        return

    stock_name, price, total_qty = stock_info

    # For sell transactions, check available quantity
    current_qty = 0
    if action == "SELL":
        current_qty = get_owned_quantity()

    tb.Label(dialog, text=f"Stock: {stock_name} (ID: {stock_id})").pack(pady=5)
    tb.Label(dialog, text=f"Price: ₹{price:.2f}").pack(pady=5)
    tb.Label(dialog, text=f"Total Available: {total_qty}").pack(pady=5)

    if action == "SELL":
        tb.Label(dialog, text=f"Currently Owned: {current_qty}").pack(pady=5)

    tb.Label(dialog, text="Quantity:").pack(pady=5)
    qty_entry = tb.Entry(dialog)
    qty_entry.pack(pady=5)

    def confirm_transaction():
        try:
            quantity = int(qty_entry.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive")
                return

            if action == "SELL" and quantity > current_qty:
                messagebox.showerror("Error", f"You only own {current_qty} shares")
                return

            if quantity > total_qty:
                messagebox.showerror("Error", f"Only {total_qty} shares available")
                return

            conn = None
            cursor = None
            try:
                conn = get_connection()
                cursor = conn.cursor()

                # Check buyer's capital for BUY transactions
                if action == "BUY":
                    cursor.execute("SELECT Capital FROM Buyer WHERE BuyerId = %s", (buyer_id,))
                    result = cursor.fetchone()
                    if not result:
                        messagebox.showerror("Error", "Buyer record not found")
                        return
                    capital = result[0]
                    total_cost = quantity * price
                    if total_cost > capital:
                        messagebox.showerror("Error",
                                         f"Insufficient capital. You need ₹{total_cost:,.2f} but have ₹{capital:,.2f}")
                        return

                # Record transaction
                cursor.execute(""" 
                    INSERT INTO Transactions (BuyerId, StockId, TransactionType, Quantity, Price, TransactionDate)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (buyer_id, stock_id, action, quantity, price, datetime.now()))

                # Update portfolio
                if action == "BUY":
                    # Update buyer's capital
                    cursor.execute("UPDATE Buyer SET Capital = Capital - %s WHERE BuyerId = %s",
                                   (quantity * price, buyer_id))

                    # Update available quantity
                    cursor.execute("UPDATE Types SET Quantity = Quantity - %s WHERE StockId = %s",
                                   (quantity, stock_id))

                    # Check if stock already exists in portfolio
                    cursor.execute("SELECT COUNT(*) FROM Portfolio WHERE BuyerId = %s AND StockId = %s",
                                   (buyer_id, stock_id))
                    exists = cursor.fetchone()[0] > 0

                    if exists:
                        cursor.execute(""" 
                            UPDATE Portfolio 
                            SET Quantity = Quantity + %s,
                                PurchasePrice = %s
                            WHERE BuyerId = %s AND StockId = %s
                        """, (quantity, price, buyer_id, stock_id))
                    else:
                        cursor.execute(""" 
                            INSERT INTO Portfolio (BuyerId, StockId, Quantity, PurchasePrice)
                            VALUES (%s, %s, %s, %s)
                        """, (buyer_id, stock_id, quantity, price))
                else:  # SELL
                    # Update buyer's capital
                    cursor.execute("UPDATE Buyer SET Capital = Capital + %s WHERE BuyerId = %s",
                                   (quantity * price, buyer_id))

                    # Update available quantity
                    cursor.execute("UPDATE Types SET Quantity = Quantity + %s WHERE StockId = %s",
                                   (quantity, stock_id))

                    cursor.execute(""" 
                        UPDATE Portfolio 
                        SET Quantity = Quantity - %s
                        WHERE BuyerId = %s AND StockId = %s
                    """, (quantity, buyer_id, stock_id))

                    # Remove if quantity becomes zero
                    cursor.execute(""" 
                        DELETE FROM Portfolio 
                        WHERE BuyerId = %s AND StockId = %s AND Quantity <= 0
                    """, (buyer_id, stock_id))

                conn.commit()
                messagebox.showinfo("Success", f"Stock {action} completed!")
                dialog.destroy()
                refresh_callback()
                return True
            except ValueError:
                messagebox.showerror("Error", "Invalid quantity")
            except mysql.connector.Error as err:
                if conn and conn.is_connected():
                    conn.rollback()
                messagebox.showerror("Database Error", str(err))
                return False
            finally:
                if cursor:
                    cursor.close()
                if conn and conn.is_connected():
                    conn.close()
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity")
            return False

    tb.Button(dialog, text=f"Confirm {action}",
              command=confirm_transaction,
              bootstyle=SUCCESS if action == "BUY" else DANGER).pack(pady=10)

def open_stock_window(username, mode="view"):
    win = tb.Toplevel()
    win.title(f"Stocks - {mode.capitalize()}")
    win.geometry("1000x600")

    # Treeview to display stocks with ID column
    tree = tb.Treeview(win, columns=("id", "name", "price", "market", "broker", "qty", "owned"), show="headings")
    tree.heading("id", text="Stock ID")
    tree.heading("name", text="Stock Name")
    tree.heading("price", text="Price")
    tree.heading("market", text="Market")
    tree.heading("broker", text="Broker")
    tree.heading("qty", text="Available Qty")
    tree.heading("owned", text="Owned Qty" if mode != "manage" else "Action")

    tree.column("id", width=80)
    tree.column("name", width=150)
    tree.column("price", width=100)
    tree.column("market", width=120)
    tree.column("broker", width=120)
    tree.column("qty", width=100)
    tree.column("owned", width=100)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Button frame
    btn_frame = tb.Frame(win)
    btn_frame.pack(pady=10)

    def refresh_stock_list():
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()

            for item in tree.get_children():
                tree.delete(item)

            if mode == "manage":
                # Broker view - all stocks with edit options
                cursor.execute(""" 
                    SELECT s.StockId, s.StockName, s.Price, 
                           CONCAT(m.Type, ' (', m.Country, ')') AS Market,
                           bp.Name AS Broker,
                           t.Quantity AS TotalQty
                    FROM Stocks s
                    JOIN Market m ON s.MarketId = m.MarketId
                    JOIN BrokerPlatform bp ON s.BrokerId = bp.PlatformId
                    JOIN Types t ON s.StockId = t.StockId
                    ORDER BY s.StockId
                """)
                for stock in cursor.fetchall():
                    stock_id, name, price, market, broker, total_qty = stock
                    tree.insert("", "end", iid=stock_id,
                              values=(stock_id, name, f"₹{price:.2f}", market, broker, total_qty, "-"))
            else:
                # Get buyer_id for buyer view
                cursor.execute("SELECT BuyerId FROM Buyer WHERE Name = %s", (username,))
                buyer_result = cursor.fetchone()
                if buyer_result is None:
                    messagebox.showerror("Error", "Buyer record not found. Please contact support.")
                    return
                buyer_id = buyer_result[0]

                # Get buyer's capital
                cursor.execute("SELECT Capital FROM Buyer WHERE BuyerId = %s", (buyer_id,))
                capital_result = cursor.fetchone()
                if not capital_result:
                    messagebox.showerror("Error", "Could not retrieve buyer capital")
                    return
                capital = capital_result[0]

                # Buyer view - with owned quantities
                cursor.execute(""" 
                    SELECT s.StockId, s.StockName, s.Price, 
                           CONCAT(m.Type, ' (', m.Country, ')') AS Market,
                           bp.Name AS Broker,
                           t.Quantity AS TotalQty,
                           IFNULL(p.Quantity, 0) AS OwnedQty
                    FROM Stocks s
                    JOIN Market m ON s.MarketId = m.MarketId
                    JOIN BrokerPlatform bp ON s.BrokerId = bp.PlatformId
                    JOIN Types t ON s.StockId = t.StockId
                    LEFT JOIN Portfolio p ON s.StockId = p.StockId AND p.BuyerId = %s
                    ORDER BY s.StockId
                """, (buyer_id,))
                for stock in cursor.fetchall():
                    stock_id, name, price, market, broker, total_qty, qty = stock
                    tree.insert("", "end", iid=stock_id,
                              values=(stock_id, name, f"₹{price:.2f}", market, broker, total_qty, qty))

                # Display buyer's capital
                capital_label.config(text=f"Available Capital: ₹{capital:,.2f}")

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def edit_stock_price():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a stock")
            return

        stock_id = selected[0]
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT StockName, Price FROM Stocks WHERE StockId = %s", (stock_id,))
            stock_name, price = cursor.fetchone()
            update_stock_price_window(stock_id, price)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def remove_stock():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a stock")
            return

        stock_id = selected[0]
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT StockName FROM Stocks WHERE StockId = %s", (stock_id,))
            stock_name = cursor.fetchone()[0]
            delete_stock_window(stock_id, stock_name)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # Capital display for buyers
    capital_label = tb.Label(win, text="", font=("Helvetica", 10, "bold"))
    capital_label.pack(pady=5)

    if mode == "view":
        # Get buyer_id for transaction buttons
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT BuyerId FROM Buyer WHERE Name = %s", (username,))
            buyer_result = cursor.fetchone()
            if buyer_result is None:
                messagebox.showerror("Error", "Buyer record not found. Please contact support.")
                win.destroy()
                return
            buyer_id = buyer_result[0]

            tb.Button(btn_frame, text="Refresh", command=refresh_stock_list, bootstyle=PRIMARY).pack(side="left",
                                                                                                   padx=5)
            tb.Button(btn_frame, text="Buy",
                      command=lambda: execute_transaction(buyer_id, tree, "BUY", refresh_stock_list),
                      bootstyle=SUCCESS).pack(side="left", padx=5)
            tb.Button(btn_frame, text="Sell",
                      command=lambda: execute_transaction(buyer_id, tree, "SELL", refresh_stock_list),
                      bootstyle=DANGER).pack(side="left", padx=5)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
            win.destroy()
            return
        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
    elif mode == "manage":
        tb.Button(btn_frame, text="Refresh", command=refresh_stock_list, bootstyle=PRIMARY).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Add Stock", command=add_stock_window, bootstyle=SUCCESS).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Edit Price", command=edit_stock_price, bootstyle=WARNING).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Remove Stock", command=remove_stock, bootstyle=DANGER).pack(side="left", padx=5)

    tb.Button(btn_frame, text="Close", command=win.destroy, bootstyle=DANGER).pack(side="right", padx=5)

    refresh_stock_list()