# boot.py or main.py

from machine import Pin, time_pulse_us
import urequests
import time

# Pin setup
TRIG_PIN = Pin(5, Pin.OUT)
ECHO_PIN = Pin(18, Pin.IN)
BUZZER_PIN = Pin(19, Pin.OUT)

# Wi-Fi setup
def connect():
    import network
    ssid = "わたしも大好き"
    password = "151229122105"  # <- change to match your hotspot password
    station = network.WLAN(network.STA_IF)

    if not station.isconnected():
        station.active(True)
        station.connect(ssid, password)
        while not station.isconnected():
            pass

    print("Connection successful")
    print(station.ifconfig())

connect()
time.sleep(2)

# Telegram Bot Details
BOT_TOKEN = '8453170032:AAHlJIaWTOD1eO0NqtL_qzQOt-D8MMLsX-E'
CHAT_ID = '5987485260'

# Send message to Telegram
def send_telegram_message(distance):
    timestamp = int(time.time())
    message = "Distance Detected: {:.2f} cm at {}".format(distance, timestamp)
    url = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}".format(
        BOT_TOKEN, CHAT_ID, message)
    try:
        response = urequests.get(url)
        content = response.text
        print(content)
        if "<html>" in content.lower():
            print("⚠️ Captive portal detected. Telegram message not actually sent.")
        else:
            print("✅ Telegram message sent")
        response.close()
    except Exception as e:
        print("Failed to send Telegram message:", e)

# Distance reading
def get_distance():
    TRIG_PIN.off()
    time.sleep_us(2)
    TRIG_PIN.on()
    time.sleep_us(10)
    TRIG_PIN.off()

    duration = time_pulse_us(ECHO_PIN, 1, 30000)
    if duration < 0:
        return -1
    distance_cm = (duration / 2) / 29.1
    return distance_cm

# Loop
while True:
    distance = get_distance()

    if distance > 0:
        print("Distance: {:.2f} cm".format(distance))
        if distance < 5:
            BUZZER_PIN.on()
            send_telegram_message(distance)
        else:
            BUZZER_PIN.off()
    else:
        print("Error reading distance")

    # Send to Google Form
    h = {'content-type': 'application/x-www-form-urlencoded'}
    form_url = 'https://docs.google.com/forms/d/e/1FAIpQLScM7QQL-mvmjLeibaPexRa8JpApiqFPL73jWwvvXSr9qrzQow/formResponse?usp=pp_url&'
    form_data = 'entry.1822356281=' + str(distance)
    try:
        r = urequests.post(form_url, data=form_data, headers=h)
        r.close()
        print("Data sent to Google Form")
    except:
        print("Failed to send to Google Form")

    time.sleep(10)
