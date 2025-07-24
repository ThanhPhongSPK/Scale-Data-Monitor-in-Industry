import tkinter as tk
from tkinter import ttk
import pandas as pd
import threading
import subprocess
from datetime import datetime
from store_dataMYSQL import fetch_data
import serial.tools.list_ports

def start_scale_script():
    subprocess.Popen(["python", "Connect_to_scale.py"])

def update_table():
    global data
    if auto_update_enabled:
        data = fetch_data()
        
        tree.delete(*tree.get_children())  # Clear existing rows
        for i, row in enumerate(reversed(data), 1):
            tree.insert("", "end", values=(i, *row), tags=("grid",))

    root.after(1000, update_table)  # Refresh every 2 seconds

def export_to_excel():
    df = pd.DataFrame(data, columns=["Date", "Time", "Gross", "Tare", "Net"])
    df.to_csv("scale_data.csv", index=False)
    status_label.config(text="✅ Data exported successfully !!!")

auto_update_enabled = True

def filter_data():
    global auto_update_enabled
    auto_update_enabled = False  # Disable auto-update when filtering

    start_date = start_date_entry.get().strip()
    end_date = end_date_entry.get().strip()
    start_time = start_time_entry.get().strip()
    end_time = end_time_entry.get().strip()

    filtered_data = []
    
    for row in data:
        row_date = row[0]  # Extract Time (YY:MM:DD)
        row_time = row[1]  # Extract Time (HH:MM:SS)

        row_datetime = datetime.strptime(f"{row_date} {row_time}", "%Y-%m-%d %H:%M:%S")

        # Convert user input to datetime format if both date and time are given
        if start_date and end_date and start_time and end_time:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
            end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")
            if start_datetime <= row_datetime <= end_datetime:
                filtered_data.append(row)

        # Filter only by Date if Time is not provided
        elif start_date and end_date and not start_time and not end_time:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
            if start_date_obj <= row_date <= end_date_obj:
                filtered_data.append(row)

        # Filter only by Time if Date is not provided
        elif start_time and end_time and not start_date and not end_date:
            row_time = datetime.strptime(f"{row_time}", "%H:%M:%S").time()
            start_time_obj = datetime.strptime(start_time, "%H:%M:%S").time()
            end_time_obj = datetime.strptime(end_time, "%H:%M:%S").time()
            if start_time_obj <= row_time <= end_time_obj:
                filtered_data.append(row)

    # Update the table with filtered data
    tree.delete(*tree.get_children())  # Clear table
    for i, row in enumerate(reversed(filtered_data), 1):
        tree.insert("", "end", values=(i, *row), tags=("grid",))

    status_label.config(text="✅ Showing filtered data. Auto-refresh paused.")


def clear_filter():
    global auto_update_enabled
    auto_update_enabled = True  # Re-enable auto-update
    update_table()  # Refresh table with full data
    status_label.config(text="✅ Auto-refresh enabled.")

# Function to get available COM ports
def get_com_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# Function to start `Connect_to_scale.py` with user-selected settings

# Start the scale reading script in a separate thread
threading.Thread(target=start_scale_script, daemon=True).start()

# 🚀 UI Setup
root = tk.Tk()
root.title("📊 Scale Data Management")
root.geometry("1400x700")
root.configure(bg="#121212")

# 🚀 Modern Styling
style = ttk.Style()
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#0078D7", foreground="white")
style.configure("Treeview", font=("Arial", 11), rowheight=30, background="#2E2E2E", foreground="white", fieldbackground="#2E2E2E")

# 🚀 Title
title_label = tk.Label(root, text="Live Scale Data Monitoring", font=("Arial", 22, "bold"), bg="#121212", fg="white")
title_label.pack(pady=15)

# 🚀 Frame for Filters
frame_filters = tk.Frame(root, bg="#121212")
frame_filters.pack(pady=10)

entry_style = {"width": 18, "font": ("Arial", 12), "bg": "#2E2E2E", "fg": "white", "insertbackground": "white"}

tk.Label(frame_filters, text="From Date:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5)
start_date_entry = tk.Entry(frame_filters, **entry_style)
start_date_entry.grid(row=0, column=1, padx=5)

tk.Label(frame_filters, text="From Time:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=5)
start_time_entry = tk.Entry(frame_filters, **entry_style)
start_time_entry.grid(row=0, column=3, padx=5)

tk.Label(frame_filters, text="To Date:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=1, column=0, padx=5)
end_date_entry = tk.Entry(frame_filters, **entry_style)
end_date_entry.grid(row=1, column=1, padx=5)

tk.Label(frame_filters, text="To Time:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=1, column=2, padx=5)
end_time_entry = tk.Entry(frame_filters, **entry_style)
end_time_entry.grid(row=1, column=3, padx=5)


# 🚀 Serial Configuration Frame
frame_serial = tk.Frame(root, bg="#121212")
frame_serial.pack(pady=10)

# COM Port Selection
port_var = tk.StringVar()
baudrate_var = tk.StringVar()

def start_scale_script():
    selected_port = port_var.get()
    selected_baudrate = baudrate_var.get()
    
    if not selected_port or not selected_baudrate:
        status_label.config(text="❌ Please select a COM port and Baud rate!", fg="red")
        return

    # Start the script with selected settings
    subprocess.Popen(["python", "Connect_to_scale.py", selected_port, selected_baudrate])
    status_label.config(text=f"✅ Scale started on {selected_port} at {selected_baudrate} baud.", fg="green")

tk.Label(frame_serial, text="Select COM Port:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=0, column=0, padx=5)
port_dropdown = ttk.Combobox(frame_serial, textvariable=port_var, values=get_com_ports(), state="readonly", width=15)
port_dropdown.grid(row=0, column=1, padx=5)
port_dropdown.set(get_com_ports()[0] if get_com_ports() else "No Ports Found")

# Baud Rate Selection
tk.Label(frame_serial, text="Baud Rate:", bg="#121212", fg="white", font=("Arial", 12)).grid(row=0, column=2, padx=5)
baudrate_dropdown = ttk.Combobox(frame_serial, textvariable=baudrate_var, values=["9600", "19200", "38400", "57600", "115200"], state="readonly", width=15)
baudrate_dropdown.grid(row=0, column=3, padx=5)
baudrate_dropdown.set("9600")  # Default baud rate

# Start Scale Button
btn_start_scale = tk.Button(root, text="▶ Start Scale", command=start_scale_script, font=("Arial", 12, "bold"), bg="#0078D7", fg="white", width=15)
btn_start_scale.pack(pady=10)

# 🚀 Buttons Styling
frame_buttons = tk.Frame(root, bg="#121212")
frame_buttons.pack(pady=10)

btn_style = {"font": ("Arial", 13), "width": 16, "height": 1, "bd": 2, "relief": "ridge"}

btn_filter = tk.Button(frame_buttons, text="Filter", command=filter_data, bg="#0078D7", fg="white", **btn_style)
btn_filter.grid(row=0, column=0, padx=10)

btn_export = tk.Button(frame_buttons, text="Export to Excel", command=export_to_excel, bg="#28A745", fg="white", **btn_style)
btn_export.grid(row=0, column=1, padx=10)

btn_exit = tk.Button(frame_buttons, text="Exit", command=root.quit, bg="#D73A49", fg="white", **btn_style)
btn_exit.grid(row=0, column=2, padx=10)

btn_clear_filter = tk.Button(frame_buttons, text="Clear Filter", command=clear_filter, bg="#FFA500", fg="white", **btn_style)
btn_clear_filter.grid(row=0, column=3, padx=10)

# 🚀 Table Styling
columns = ("ID", "Date", "Time", "Gross", "Tare", "Net")
tree = ttk.Treeview(root, columns=columns, show="headings", height=16)

# Add alternate row colors
tree.tag_configure("oddrow", background="#1E1E1E")
tree.tag_configure("evenrow", background="#252525")

for col in columns:
    tree.heading(col, text=col, anchor="center")
    tree.column(col, width=140, anchor="center")

tree.pack(pady=10, padx=20)

# 🚀 Status Label
status_label = tk.Label(root, text="", bg="#121212", fg="white", font=("Arial", 12))
status_label.pack()

# Start real-time update
update_table()

# Run GUI
root.mainloop()