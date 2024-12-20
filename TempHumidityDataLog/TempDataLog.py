import serial
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def setup_google_sheets():
    # Set up Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open("Temperature and Humidity Log").sheet1
    return sheet

def log_to_google_sheets(sheet, data):
    # Append data to the sheet
    sheet.append_row(data)

def main():
    # Set up serial communication
    ser = serial.Serial('COM7', 115200)  # Adjust the port as needed
    time.sleep(2)  # Allow time for the serial connection to initialize

    # Set up Google Sheets
    try:
        sheet = setup_google_sheets()
        print("Connected to Google Sheets")
    except Exception as e:
        print(f"Failed to connect to Google Sheets: {e}")
        return

    print("Listening for data...")
    while True:
        try:
            # Read data from serial
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                print(f"Received: {line}")

                # Parse data
                if line.startswith("{") and line.endswith("}"):
                    line = line[1:-1]  # Remove braces
                    parts = line.split(",")  # Split by commas

                    if len(parts) == 3:  # Expecting 3 parts: DHT11 temp, DHT11 humidity, DS18B20 temp
                        try:
                            # Parse the data, ensuring correct formatting
                            dht11_temp = float(parts[0])  # DHT11 Temperature
                            dht11_humidity = float(parts[1].replace("%", ""))  # Remove "%" and convert to float
                            ds18b20_temp = float(parts[2])  # DS18B20 Temperature

                            # Get the current date and time
                            timestamp = time.strftime("%Y-%m-%d")  # Date in YYYY-MM-DD format
                            current_time = time.strftime("%H:%M:%S")  # Time in HH:MM:SS format

                            # Log to Google Sheets (Date, Time, DHT11 Temp, DHT11 Humidity, DS18B20 Temp)
                            log_to_google_sheets(sheet, [timestamp, current_time, dht11_temp, dht11_humidity, ds18b20_temp])
                            print("Data logged to Google Sheets")

                        except ValueError:
                            print("Failed to parse data")

        except KeyboardInterrupt:
            print("Exiting...")
            ser.close()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
