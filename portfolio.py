import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_config import get_connection
from tkinter import messagebox
import mysql.connector


def open_portfolio_window(username, view="portfolio"):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        win = tb.Toplevel()
        win.title(
            f"{'All Portfolios' if username == 'all' else username}'s {'Portfolio' if view == 'portfolio' else 'Transactions'}")
        win.geometry("1100x700")

        # Summary frame
        summary_frame = tb.Frame(win)
        summary_frame.pack(fill="x", padx=10, pady=10)

        if username == "all":  # Broker view
            # Get summary stats
            cursor.execute("SELECT COUNT(DISTINCT BuyerId) FROM Portfolio")
            investor_count = cursor.fetchone()[0]

            cursor.execute("SELECT SUM(Quantity * PurchasePrice) FROM Portfolio")
            total_investment = cursor.fetchone()[0] or 0

            cursor.execute(
                "SELECT SUM(Quantity * (s.Price - p.PurchasePrice)) FROM Portfolio p JOIN Stocks s ON p.StockId = s.StockId")
            total_pl = cursor.fetchone()[0] or 0

            cursor.execute("SELECT SUM(Amount) FROM Dividend")
            total_dividends = cursor.fetchone()[0] or 0

            tb.Label(summary_frame, text=f"Investors: {investor_count}", font=("Helvetica", 10)).pack(side="left",
                                                                                                      padx=10)
            tb.Label(summary_frame, text=f"Total Investment: ₹{total_investment:,.2f}", font=("Helvetica", 10)).pack(
                side="left", padx=10)
            tb.Label(summary_frame, text=f"Total P/L: ₹{total_pl:,.2f}",
                     font=("Helvetica", 10), foreground="green" if total_pl >= 0 else "red").pack(side="left", padx=10)
            tb.Label(summary_frame, text=f"Total Dividends: ₹{total_dividends:,.2f}", font=("Helvetica", 10)).pack(
                side="left", padx=10)

            if view == "portfolio":
                cursor.execute("""
                    SELECT b.Name, s.StockId, s.StockName, p.Quantity, 
                           p.PurchasePrice, s.Price,
                           (p.Quantity * p.PurchasePrice) AS Investment,
                           (p.Quantity * (s.Price - p.PurchasePrice)) AS ProfitLoss
                    FROM Portfolio p
                    JOIN Buyer b ON p.BuyerId = b.BuyerId
                    JOIN Stocks s ON p.StockId = s.StockId
                    ORDER BY b.Name, s.StockId
                """)

                # Create container frame for treeview
                container = tb.Frame(win)
                container.pack(fill="both", expand=True, padx=10, pady=10)

                # Create Treeview with automatic scrolling
                tree = tb.Treeview(
                    container,
                    columns=("buyer", "id", "stock", "qty", "buy", "current", "invest", "profit"),
                    show="headings",
                    height=20,  # Fixed height
                    bootstyle="primary"
                )

                # Configure headings
                tree.heading("buyer", text="Buyer", anchor=W)
                tree.heading("id", text="Stock ID", anchor=W)
                tree.heading("stock", text="Stock", anchor=W)
                tree.heading("qty", text="Qty", anchor=W)
                tree.heading("buy", text="Buy Price", anchor=W)
                tree.heading("current", text="Current Price", anchor=W)
                tree.heading("invest", text="Investment", anchor=W)
                tree.heading("profit", text="P/L", anchor=W)

                # Configure columns
                tree.column("buyer", width=120, stretch=NO)
                tree.column("id", width=80, stretch=NO)
                tree.column("stock", width=150, stretch=NO)
                tree.column("qty", width=60, stretch=NO)
                tree.column("buy", width=100, stretch=NO)
                tree.column("current", width=100, stretch=NO)
                tree.column("invest", width=100, stretch=NO)
                tree.column("profit", width=100, stretch=NO)

                # Add to container with both expand
                tree.pack(fill="both", expand=True)

            else:  # Transactions view
                # Create a frame for the transaction log
                transaction_frame = tb.Frame(win)
                transaction_frame.pack(fill="both", expand=True, padx=10, pady=10)

                tb.Label(transaction_frame, text="Complete Transaction History", font=("Helvetica", 12, "bold")).pack(
                    anchor="w")

                # Treeview for transaction log
                tree = tb.Treeview(
                    transaction_frame,
                    columns=("id", "buyer", "stockid", "stock", "type", "qty", "price", "amount", "date"),
                    show="headings",
                    height=20,
                    bootstyle="primary"
                )

                # Configure columns
                tree.heading("id", text="Txn ID", anchor=W)
                tree.heading("buyer", text="Buyer", anchor=W)
                tree.heading("stockid", text="Stock ID", anchor=W)
                tree.heading("stock", text="Stock", anchor=W)
                tree.heading("type", text="Type", anchor=W)
                tree.heading("qty", text="Qty", anchor=W)
                tree.heading("price", text="Price", anchor=W)
                tree.heading("amount", text="Amount", anchor=W)
                tree.heading("date", text="Date & Time", anchor=W)

                tree.column("id", width=60, stretch=NO)
                tree.column("buyer", width=100, stretch=NO)
                tree.column("stockid", width=70, stretch=NO)
                tree.column("stock", width=120, stretch=NO)
                tree.column("type", width=70, stretch=NO)
                tree.column("qty", width=60, stretch=NO)
                tree.column("price", width=80, stretch=NO)
                tree.column("amount", width=90, stretch=NO)
                tree.column("date", width=150, stretch=NO)

                tree.pack(fill="both", expand=True)

                # Get complete transaction history
                cursor.execute("""
                    SELECT t.TransactionId, b.Name, s.StockId, s.StockName, 
                           t.TransactionType, t.Quantity, t.Price, 
                           (t.Quantity * t.Price) AS Amount,
                           DATE_FORMAT(t.TransactionDate, '%Y-%m-%d %H:%i:%s') AS FormattedDate
                    FROM Transactions t
                    JOIN Buyer b ON t.BuyerId = b.BuyerId
                    JOIN Stocks s ON t.StockId = s.StockId
                    ORDER BY t.TransactionDate DESC
                """)

                # Insert data into treeview
                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)

        else:  # Buyer view
            cursor.execute("SELECT BuyerId FROM Buyer WHERE Name = %s", (username,))
            buyer_result = cursor.fetchone()
            if buyer_result is None:
                messagebox.showerror("Error", "Buyer record not found")
                return
            buyer_id = buyer_result[0]

            # Get buyer stats - Fixed query by separating the dividend calculation
            cursor.execute("""
                SELECT SUM(p.Quantity * p.PurchasePrice), 
                       SUM(p.Quantity * (s.Price - p.PurchasePrice)),
                       b.Capital
                FROM Portfolio p
                JOIN Stocks s ON p.StockId = s.StockId
                JOIN Buyer b ON p.BuyerId = b.BuyerId
                WHERE p.BuyerId = %s
            """, (buyer_id,))
            investment, profit_loss, capital = cursor.fetchone()

            # Get dividends separately
            cursor.execute("""
                SELECT SUM(Amount) 
                FROM Dividend 
                WHERE BuyerId = %s
            """, (buyer_id,))
            dividends = cursor.fetchone()[0] or 0

            investment = investment or 0
            profit_loss = profit_loss or 0
            capital = capital or 0

            tb.Label(summary_frame, text=f"Total Investment: ₹{investment:,.2f}", font=("Helvetica", 10)).pack(
                side="left", padx=10)
            tb.Label(summary_frame, text=f"Profit/Loss: ₹{profit_loss:,.2f}",
                     font=("Helvetica", 10), foreground="green" if profit_loss >= 0 else "red").pack(side="left",
                                                                                                     padx=10)
            tb.Label(summary_frame, text=f"Dividends: ₹{dividends:,.2f}", font=("Helvetica", 10)).pack(side="left",
                                                                                                       padx=10)
            tb.Label(summary_frame, text=f"Available Capital: ₹{capital:,.2f}", font=("Helvetica", 10)).pack(
                side="left", padx=10)

            if view == "portfolio":
                cursor.execute("""
                    SELECT s.StockId, s.StockName, p.Quantity, 
                           p.PurchasePrice, s.Price,
                           (p.Quantity * p.PurchasePrice) AS Investment,
                           (p.Quantity * (s.Price - p.PurchasePrice)) AS ProfitLoss
                    FROM Portfolio p
                    JOIN Stocks s ON p.StockId = s.StockId
                    WHERE p.BuyerId = %s
                    ORDER BY s.StockId
                """, (buyer_id,))

                # Create container frame for treeview
                container = tb.Frame(win)
                container.pack(fill="both", expand=True, padx=10, pady=10)

                # Create Treeview with automatic scrolling
                tree = tb.Treeview(
                    container,
                    columns=("id", "stock", "qty", "buy", "current", "invest", "profit"),
                    show="headings",
                    height=20,
                    bootstyle="primary"
                )

                # Configure headings
                tree.heading("id", text="Stock ID", anchor=W)
                tree.heading("stock", text="Stock", anchor=W)
                tree.heading("qty", text="Qty", anchor=W)
                tree.heading("buy", text="Buy Price", anchor=W)
                tree.heading("current", text="Current Price", anchor=W)
                tree.heading("invest", text="Investment", anchor=W)
                tree.heading("profit", text="P/L", anchor=W)

                # Configure columns
                tree.column("id", width=80, stretch=NO)
                tree.column("stock", width=150, stretch=NO)
                tree.column("qty", width=60, stretch=NO)
                tree.column("buy", width=100, stretch=NO)
                tree.column("current", width=100, stretch=NO)
                tree.column("invest", width=100, stretch=NO)
                tree.column("profit", width=100, stretch=NO)

                tree.pack(fill="both", expand=True)

            else:  # Transactions view
                # Create a frame for the transaction log
                transaction_frame = tb.Frame(win)
                transaction_frame.pack(fill="both", expand=True, padx=10, pady=10)

                tb.Label(transaction_frame, text="Your Complete Transaction History",
                         font=("Helvetica", 12, "bold")).pack(anchor="w")

                # Treeview for transaction log
                tree = tb.Treeview(
                    transaction_frame,
                    columns=("id", "stockid", "stock", "type", "qty", "price", "amount", "date"),
                    show="headings",
                    height=20,
                    bootstyle="primary"
                )

                # Configure columns
                tree.heading("id", text="Txn ID", anchor=W)
                tree.heading("stockid", text="Stock ID", anchor=W)
                tree.heading("stock", text="Stock", anchor=W)
                tree.heading("type", text="Type", anchor=W)
                tree.heading("qty", text="Qty", anchor=W)
                tree.heading("price", text="Price", anchor=W)
                tree.heading("amount", text="Amount", anchor=W)
                tree.heading("date", text="Date & Time", anchor=W)

                tree.column("id", width=60, stretch=NO)
                tree.column("stockid", width=70, stretch=NO)
                tree.column("stock", width=120, stretch=NO)
                tree.column("type", width=70, stretch=NO)
                tree.column("qty", width=60, stretch=NO)
                tree.column("price", width=80, stretch=NO)
                tree.column("amount", width=90, stretch=NO)
                tree.column("date", width=150, stretch=NO)

                tree.pack(fill="both", expand=True)

                query = f"""
                    SELECT t.TransactionId, s.StockId, s.StockName, 
                           t.TransactionType, t.Quantity, t.Price, 
                           (t.Quantity * t.Price) AS Amount,
                           DATE_FORMAT(t.TransactionDate, '%Y-%m-%d %H:%i:%s') AS FormattedDate
                    FROM Transactions t
                    JOIN Stocks s ON t.StockId = s.StockId
                    WHERE t.BuyerId = {buyer_id}
                    ORDER BY t.TransactionDate DESC
                """
                cursor.execute(query)

                # Insert data into treeview
                for row in cursor.fetchall():
                    tree.insert("", "end", values=row)

        # Insert data into treeview (for portfolio views)
        if view == "portfolio":
            for row in cursor.fetchall():
                tree.insert("", "end", values=row)

        # View toggle button
        if username != "all":  # Only show toggle for individual buyers
            if view == "portfolio":
                tb.Button(win, text="View Transactions",
                          command=lambda: [win.destroy(), open_portfolio_window(username, "transactions")],
                          bootstyle=INFO).pack(pady=10)
            else:
                tb.Button(win, text="View Portfolio",
                          command=lambda: [win.destroy(), open_portfolio_window(username, "portfolio")],
                          bootstyle=INFO).pack(pady=10)

        tb.Button(win, text="Close", command=win.destroy, bootstyle=DANGER).pack(pady=10)

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()