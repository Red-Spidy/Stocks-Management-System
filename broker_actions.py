import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_config import get_connection
from tkinter import messagebox
import mysql.connector
from datetime import datetime

def open_broker_actions_window(username):
    def execute_action(action):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            action_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = ""

            if action == "commission":
                # Apply 5% commission
                cursor.execute("UPDATE Stocks SET Price = Price * 1.05")
                message = "5% commission applied to all stocks"

                # Record action
                cursor.execute("""
                    INSERT INTO BrokerActions (ActionType, ActionDetails, ActionTime, Username)
                    VALUES (%s, %s, %s, %s)
                """, ("Commission", message, action_time, username))

            elif action == "dividends":
                # Distribute 2% dividends
                cursor.execute("""
                    INSERT INTO Dividend (BuyerId, Date, Amount)
                    SELECT p.BuyerId, CURDATE(), SUM(p.Quantity * p.PurchasePrice) * 0.02
                    FROM Portfolio p
                    GROUP BY p.BuyerId
                """)
                message = "2% dividends distributed to all investors"

                # Record action
                cursor.execute("""
                    INSERT INTO BrokerActions (ActionType, ActionDetails, ActionTime, Username)
                    VALUES (%s, %s, %s, %s)
                """, ("Dividend", message, action_time, username))

            elif action == "investments":
                # Calculate total investments
                cursor.execute("""
                    UPDATE Buyer b
                    SET Capital = (
                        SELECT IFNULL(SUM(p.Quantity * p.PurchasePrice), 0)
                        FROM Portfolio p
                        WHERE p.BuyerId = b.BuyerId
                    )
                """)

                cursor.execute("SELECT SUM(Capital) FROM Buyer")
                total_investment = cursor.fetchone()[0] or 0
                message = f"Total investments calculated: ₹{total_investment:,.2f}"

                # Record action
                cursor.execute("""
                    INSERT INTO BrokerActions (ActionType, ActionDetails, ActionTime, Username)
                    VALUES (%s, %s, %s, %s)
                """, ("Investment", message, action_time, username))

            conn.commit()
            messagebox.showinfo("Success", message)
            refresh_action_history()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    def refresh_action_history():
        for item in history_tree.get_children():
            history_tree.delete(item)

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ActionType, ActionDetails, ActionTime 
                FROM BrokerActions 
                WHERE Username = %s
                ORDER BY ActionTime DESC
                LIMIT 20
            """, (username,))

            for action in cursor.fetchall():
                history_tree.insert("", "end", values=action)

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()

    win = tb.Toplevel()
    win.title(f"Broker Actions - {username}")
    win.geometry("900x600")

    # Main frames
    main_frame = tb.Frame(win)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Action buttons frame
    action_frame = tb.Frame(main_frame)
    action_frame.pack(fill="x", pady=10)

    tb.Label(action_frame, text="Broker Actions:", font=("Helvetica", 12)).pack(anchor="w")

    btn_frame = tb.Frame(action_frame)
    btn_frame.pack(fill="x", pady=5)

    actions = [
        ("Apply 5% Commission", "commission", WARNING),
        ("Distribute 2% Dividends", "dividends", SUCCESS),
        ("Calculate Investments", "investments", INFO)
    ]

    for text, action, style in actions:
        tb.Button(btn_frame, text=text,
                  command=lambda a=action: execute_action(a),
                  bootstyle=style).pack(side="left", padx=5)

    # Stats frame
    stats_frame = tb.Frame(main_frame)
    stats_frame.pack(fill="x", pady=10)

    tb.Label(stats_frame, text="Market Statistics:", font=("Helvetica", 12)).pack(anchor="w")

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Get market stats
        cursor.execute("SELECT COUNT(*) FROM Stocks")
        stock_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(DISTINCT BuyerId) FROM Portfolio")
        investor_count = cursor.fetchone()[0]

        cursor.execute("SELECT SUM(Quantity * PurchasePrice) FROM Portfolio")
        total_investment = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(Amount) FROM Dividend")
        total_dividends = cursor.fetchone()[0] or 0

        stats_text = f"Stocks: {stock_count} | Investors: {investor_count} | " \
                     f"Total Investment: ₹{total_investment:,.2f} | " \
                     f"Total Dividends: ₹{total_dividends:,.2f}"

        tb.Label(stats_frame, text=stats_text).pack(anchor="w")

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

    # Action history frame
    history_frame = tb.Frame(main_frame)
    history_frame.pack(fill="both", expand=True)

    tb.Label(history_frame, text="Your Recent Actions:", font=("Helvetica", 12)).pack(anchor="w")

    history_tree = tb.Treeview(history_frame, columns=("type", "details", "time"), show="headings")
    history_tree.heading("type", text="Action Type")
    history_tree.heading("details", text="Details")
    history_tree.heading("time", text="Time")
    history_tree.column("type", width=120)
    history_tree.column("details", width=500)
    history_tree.column("time", width=150)
    history_tree.pack(fill="both", expand=True)

    tb.Button(win, text="Close", command=win.destroy, bootstyle=DANGER).pack(pady=10)

    refresh_action_history()
