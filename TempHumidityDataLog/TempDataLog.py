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
                    parts = line.split(",")

                    if len(parts) == 3:
                        try:
                            ambient_temp = float(parts[0])
                            humidity = float(parts[1].replace("%", ""))
                            liquid_temp = float(parts[2])

                            # Log to Google Sheets
                            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                            log_to_google_sheets(sheet, [timestamp, ambient_temp, humidity, liquid_temp])
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
