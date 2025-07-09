import ttkbootstrap as tb
from ttkbootstrap.constants import *
from stocks import open_stock_window
from portfolio import open_portfolio_window
from broker_actions import open_broker_actions_window

def open_dashboard(username, role):
    root = tb.Window(themename="darkly")
    root.title(f"Stock Management Dashboard ({role})")
    root.geometry("500x350")

    tb.Label(root, text=f"Welcome {username} ({role})", font=("Helvetica", 16)).pack(pady=10)

    btn_frame = tb.Frame(root)
    btn_frame.pack(pady=20)

    if role == "Buyer":
        # Buyer buttons
        tb.Button(btn_frame, text="View Portfolio",
                 command=lambda: open_portfolio_window(username),
                 bootstyle=PRIMARY).grid(row=0, column=0, padx=10, pady=5)
        tb.Button(btn_frame, text="View Stocks",
                 command=lambda: open_stock_window(username, "view"),
                 bootstyle=PRIMARY).grid(row=0, column=1, padx=10, pady=5)
        tb.Button(btn_frame, text="View Transactions",
                 command=lambda: open_portfolio_window(username, "transactions"),
                 bootstyle=INFO).grid(row=1, column=0, padx=10, pady=5)
        tb.Button(btn_frame, text="Buy Stocks",
                 command=lambda: open_stock_window(username, "view"),
                 bootstyle=SUCCESS).grid(row=1, column=1, padx=10, pady=5)
        tb.Button(btn_frame, text="Sell Stocks",
                 command=lambda: open_stock_window(username, "view"),
                 bootstyle=DANGER).grid(row=2, column=0, columnspan=2, pady=5)
    else:
        # Broker buttons
        tb.Button(btn_frame, text="Manage Stocks",
                 command=lambda: open_stock_window(username, "manage"),
                 bootstyle=SUCCESS).grid(row=0, column=0, padx=10, pady=5)
        tb.Button(btn_frame, text="Broker Actions",
                 command=lambda: open_broker_actions_window(username),
                 bootstyle=WARNING).grid(row=0, column=1, padx=10, pady=5)
        tb.Button(btn_frame, text="View All Portfolios",
                 command=lambda: open_portfolio_window("all", "portfolio"),
                 bootstyle=INFO).grid(row=1, column=0, padx=10, pady=5)
        tb.Button(btn_frame, text="View All Transactions",
                 command=lambda: open_portfolio_window("all", "transactions"),
                 bootstyle=INFO).grid(row=1, column=1, padx=10, pady=5)

    tb.Button(root, text="Logout", command=root.destroy, bootstyle=DANGER).pack(pady=20)

    root.mainloop()