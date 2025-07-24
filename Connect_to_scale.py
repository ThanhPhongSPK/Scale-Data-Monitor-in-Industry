
import serial
import time
import sys
from store_dataMYSQL import insert_measurement

# Configure the serial connection
# Get COM Port and Baud Rate from Arguments
if len(sys.argv) < 3:
    print("Usage: python Connect_to_scale.py <COM_PORT> <BAUD_RATE>")
    sys.exit(1)

com_port = sys.argv[1]  # User-selected COM port
baud_rate = int(sys.argv[2])  # User-selected baud rate

# Configure the serial connection
ser = serial.Serial(
    port=com_port,  
    baudrate=baud_rate,        
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

try:
    if not ser.is_open:
        ser.open()

    buffer = {}  # Dictionary to store received values
    all_keys = ["Date", "Time", "Gross", "Tare", "Net"] 
    required_keys = ["Date", "Time", "Gross"]  
    last_update = time.time()  

    while True:
        if ser.in_waiting > 0:  
            line = ser.readline().decode('utf-8').strip()  
            print("Received:", line)  # Debugging

            parts = line.split()
            
            # Ignore empty or invalid lines
            if len(parts) < 2:
                continue  
            
            key = parts[0]  # Extract field name 
            value = parts[-1]  # Extract the last part 

            if key in all_keys:
                if key in ["Gross", "Tare", "Net"]:  # Convert numeric values
                    try:
                        buffer[key] = float(parts[-2])  # Extract number before "kg"
                    except ValueError:
                        buffer[key] = 0.0  
                else:
                    buffer[key] = value  # Store Date/Time as a string

            # Update timestamp for when data was last received
            last_update = time.time()

        # Wait for additional data if some values are missing
        # Wait 1 seconds after last received data
        if time.time() - last_update > 1:  
            if all(k in buffer for k in required_keys):
                  
                # Ensure missing values default to 0.0
                buffer.setdefault("Tare", 0.0)  
                buffer.setdefault("Net", 0.0)

                print("\nFinal Measurement:")
                print(f"Date: {buffer['Date']}, Time: {buffer['Time']}, "
                      f"Gross: {buffer['Gross']} kg, Tare: {buffer['Tare']} kg, Net: {buffer['Net']} kg")
                print("-" * 30)
                
                # Store data to database (MYSQL)
                insert_measurement(buffer['Date'], buffer['Time'], buffer['Gross'], buffer['Tare'], buffer['Net'])
                
                # Clear the buffer for the next data set
                buffer.clear()

except KeyboardInterrupt:
    print("Exiting...")

finally:
    ser.close()
    print("Serial connection closed.")
