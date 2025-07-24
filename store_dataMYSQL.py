import mysql.connector 
from datetime import datetime

def connect_db():
    
    db = mysql.connector.connect(
        host="localhost",
        user="phong_IOT",
        password="phongdeptrai",
        database="Scale_project"
    )   
    return db

def insert_measurement(date, time, gross, tare, net):
    
    try:
        # Convert date from dd/mm/yyyy to yyyy-mm-dd
        converted_date = datetime.strptime(date, "%d/%m/%Y").strftime("%Y-%m-%d")
        
        db = connect_db()
        cursor = db.cursor()
        
        sql = """INSERT INTO measurements (date, time, gross, tare, net)
                 VALUES (%s, %s, %s, %s, %s)"""
        values = (converted_date, time, gross, tare, net)
        
        cursor.execute(sql, values)
        db.commit()
        print("✅ Data successfully inserted into MySQL!")
        
        cursor.close()
        db.close()
        
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")

# Function to fetch data from MySQL
def fetch_data():
    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT date, time, gross, tare, net FROM measurements ORDER BY id DESC")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except mysql.connector.Error as err:
        print(f"❌ Database Error: {err}")
        return []
        