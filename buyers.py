import ttkbootstrap as tb
from ttkbootstrap.constants import *
from db_config import get_connection
import mysql.connector

def open_buyer_window():
    win = tb.Toplevel()
    win.title("Buyers")
    win.geometry("500x400")

    # Initialize connection and cursor
    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SHOW COLUMNS FROM Buyer")
        columns = cursor.fetchall()
        col_names = [col[0] for col in columns]

        def refresh_buyer_list():
            nonlocal cursor
            try:
                for item in tree.get_children():
                    tree.delete(item)
                cursor.execute("SELECT * FROM Buyer")
                records = cursor.fetchall()
                for rec in records:
                    tree.insert("", "end", iid=rec[0], values=(rec[1], f"₹{rec[5]:,.2f}"))
            except mysql.connector.Error as err:
                tb.messagebox.showerror("Error", f"Failed to refresh buyer list: {err}")

        def add_buyer():
            def save_new_buyer():
                nonlocal cursor
                try:
                    name = entry_name.get().strip()
                    capital = entry_capital.get().strip()
                    if not name or not capital:
                        tb.messagebox.showerror("Error", "Please enter both name and capital.")
                        return
                    try:
                        capital_val = float(capital)
                        if capital_val <= 0:
                            tb.messagebox.showerror("Error", "Capital must be positive.")
                            return
                    except ValueError:
                        tb.messagebox.showerror("Error", "Capital must be a number.")
                        return

                    # Check if buyer already exists
                    cursor.execute("SELECT COUNT(*) FROM Buyer WHERE Name = %s", (name,))
                    if cursor.fetchone()[0] > 0:
                        tb.messagebox.showerror("Error", "Buyer with this name already exists.")
                        return

                    cursor.execute("SELECT MAX(BuyerId) FROM Buyer")
                    max_id = cursor.fetchone()[0]
                    new_id = (max_id or 0) + 1

                    cursor.execute(
                        "INSERT INTO Buyer (BuyerId, Name, Capital) VALUES (%s, %s, %s)",
                        (new_id, name, capital_val))
                    conn.commit()
                    refresh_buyer_list()
                    add_win.destroy()
                except mysql.connector.Error as err:
                    tb.messagebox.showerror("Error", f"Failed to add buyer: {err}")

            add_win = tb.Toplevel(win)
            add_win.title("Add Buyer")
            add_win.geometry("300x150")
            add_win.grab_set()

            tb.Label(add_win, text="Buyer Name:").pack(pady=5)
            entry_name = tb.Entry(add_win)
            entry_name.pack(pady=5)

            tb.Label(add_win, text="Initial Capital:").pack(pady=5)
            entry_capital = tb.Entry(add_win)
            entry_capital.pack(pady=5)

            tb.Button(add_win, text="Save", command=save_new_buyer, bootstyle=SUCCESS).pack(pady=10)

        def edit_buyer():
            nonlocal cursor
            selected = tree.selection()
            if not selected:
                tb.messagebox.showwarning("Warning", "Please select a buyer to edit.")
                return
            buyer_id = selected[0]
            try:
                cursor.execute("SELECT Name, Capital FROM Buyer WHERE BuyerId = %s", (buyer_id,))
                buyer = cursor.fetchone()
                if not buyer:
                    tb.messagebox.showerror("Error", "Selected buyer not found.")
                    return

                def save_edited_buyer():
                    try:
                        name = entry_name.get().strip()
                        capital = entry_capital.get().strip()
                        if not name or not capital:
                            tb.messagebox.showerror("Error", "Please enter both name and capital.")
                            return
                        try:
                            capital_val = float(capital)
                            if capital_val <= 0:
                                tb.messagebox.showerror("Error", "Capital must be positive.")
                                return
                        except ValueError:
                            tb.messagebox.showerror("Error", "Capital must be a number.")
                            return

                        # Check if name is being changed to an existing name
                        cursor.execute("SELECT COUNT(*) FROM Buyer WHERE Name = %s AND BuyerId != %s",
                                       (name, buyer_id))
                        if cursor.fetchone()[0] > 0:
                            tb.messagebox.showerror("Error", "Another buyer with this name already exists.")
                            return

                        cursor.execute("UPDATE Buyer SET Name = %s, Capital = %s WHERE BuyerId = %s",
                                       (name, capital_val, buyer_id))
                        conn.commit()
                        refresh_buyer_list()
                        edit_win.destroy()
                    except mysql.connector.Error as err:
                        tb.messagebox.showerror("Error", f"Failed to update buyer: {err}")

                edit_win = tb.Toplevel(win)
                edit_win.title("Edit Buyer")
                edit_win.geometry("300x150")

                tb.Label(edit_win, text="Buyer Name:").pack(pady=5)
                entry_name = tb.Entry(edit_win)
                entry_name.insert(0, buyer[0])
                entry_name.pack(pady=5)

                tb.Label(edit_win, text="Capital:").pack(pady=5)
                entry_capital = tb.Entry(edit_win)
                entry_capital.insert(0, str(buyer[1]))
                entry_capital.pack(pady=5)

                tb.Button(edit_win, text="Save", command=save_edited_buyer, bootstyle=SUCCESS).pack(pady=10)

            except mysql.connector.Error as err:
                tb.messagebox.showerror("Error", f"Failed to fetch buyer details: {err}")

        def delete_buyer():
            nonlocal cursor
            selected = tree.selection()
            if not selected:
                tb.messagebox.showwarning("Warning", "Please select a buyer to delete.")
                return
            buyer_id = selected[0]
            confirm = tb.messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected buyer?")
            if confirm:
                try:
                    # First delete portfolio entries
                    cursor.execute("DELETE FROM Portfolio WHERE BuyerId = %s", (buyer_id,))
                    # Then delete transactions
                    cursor.execute("DELETE FROM Transactions WHERE BuyerId = %s", (buyer_id,))
                    # Then delete dividend records
                    cursor.execute("DELETE FROM Dividend WHERE BuyerId = %s", (buyer_id,))
                    # Finally delete the buyer
                    cursor.execute("DELETE FROM Buyer WHERE BuyerId = %s", (buyer_id,))
                    conn.commit()
                    refresh_buyer_list()
                except Exception as e:
                    conn.rollback()
                    tb.messagebox.showerror("Error", f"Failed to delete buyer: {e}")

        def on_window_close():
            if cursor:
                cursor.close()
            if conn:
                conn.close()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", on_window_close)

        tb.Label(win, text="Buyers List", font=("Arial", 14)).pack(pady=10)

        tree = tb.Treeview(win, columns=("name", "capital"), show="headings", selectmode="browse")
        tree.heading("name", text="Buyer Name")
        tree.heading("capital", text="Capital")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        btn_frame = tb.Frame(win)
        btn_frame.pack(pady=10)

        tb.Button(btn_frame, text="Add Buyer", command=add_buyer, bootstyle=SUCCESS).grid(row=0, column=0, padx=5)
        tb.Button(btn_frame, text="Edit Buyer", command=edit_buyer, bootstyle=WARNING).grid(row=0, column=1, padx=5)
        tb.Button(btn_frame, text="Delete Buyer", command=delete_buyer, bootstyle=DANGER).grid(row=0, column=2, padx=5)
        tb.Button(btn_frame, text="Refresh", command=refresh_buyer_list, bootstyle=INFO).grid(row=0, column=3, padx=5)

        refresh_buyer_list()

    except mysql.connector.Error as err:
        tb.messagebox.showerror("Error", f"Failed to connect to database: {err}")
        win.destroy()