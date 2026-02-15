import board
import busio
import time
import math
import adafruit_ssd1306
import adafruit_mmc56x3
import adafruit_gps

# -------------------------
# CONFIG
# -------------------------

DECLINATION = 7.6
DESTINATION_THRESHOLD = 20  # meters

STORES = [
    ("Hangloose Liquors", 40.391667, -105.074722),
    ("Liquor Max", 40.392624, -105.078987),
    ("Loveland Liquors", 40.407356, -105.074522),
    ("Downtown Liquors", 40.397761, -105.075225),
    ("Tap & Tavern Liquors", 40.391541, -105.075894),
    ("34 Liquors", 40.391215, -105.074441),
    ("Loveland Wine & Spirits", 40.423462, -105.073910),
    ("Westside Liquors", 40.405944, -105.104500),
    ("Boise Liquor", 40.416218, -105.072214),
    ("North Wilson Liquors", 40.417985, -105.072018),
    ("Liqour One", 40.407939, -105.108377),
    ("Locomotive Liquors", 40.407142, -105.074758),
]

# -------------------------
# HARDWARE INIT
# -------------------------

i2c = board.STEMMA_I2C()

display = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3D)

mag = adafruit_mmc56x3.MMC5603(i2c)

uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
gps = adafruit_gps.GPS(uart, debug=False)

gps.send_command(b"PMTK220,1000")
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")


# -------------------------
# STARTUP SCREEN
# -------------------------

def startup_screen():

    display.fill(0)

    display.text("INTRODUCING", 18, 10, 1)
    display.text("BOOZE COMPASS", 8, 25, 1)

    display.rect(14, 45, 100, 10, 1)

    for i in range(0, 98, 4):

        display.fill_rect(16, 47, i, 6, 1)
        display.show()
        time.sleep(0.04)

    time.sleep(0.5)


# -------------------------
# DESTINATION SCREEN
# -------------------------

def destination_screen(store_name):

    display.fill(0)

    display.rect(0, 0, 128, 64, 1)

    display.text("BOOZIN", 18, 12, 1)
    display.text("TIME!", 28, 28, 1)

    display.text(store_name[:16], 0, 48, 1)

    display.show()


# -------------------------
# DISTANCE CALCULATION
# -------------------------

def distance(lat1, lon1, lat2, lon2):

    R = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2

    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


# -------------------------
# BEARING CALCULATION
# -------------------------

def bearing(lat1, lon1, lat2, lon2):

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dlambda = math.radians(lon2 - lon1)

    y = math.sin(dlambda) * math.cos(phi2)
    x = math.cos(phi1)*math.sin(phi2) - math.sin(phi1)*math.cos(phi2)*math.cos(dlambda)

    return (math.degrees(math.atan2(y, x)) + 360) % 360


# -------------------------
# FIND CLOSEST STORE
# -------------------------

def get_closest_store(lat, lon):

    closest = None
    closest_dist = 9999999

    for store in STORES:

        d = distance(lat, lon, store[1], store[2])

        if d < closest_dist:

            closest_dist = d
            closest = store

    return closest, closest_dist


# -------------------------
# ARROW DRAWING
# -------------------------

def draw_arrow(direction):

    cx = 64
    cy = 32
    size = 18

    if direction == "N":

        display.line(cx, cy-size, cx, cy+size, 1)
        display.line(cx, cy-size, cx-6, cy-size+6, 1)
        display.line(cx, cy-size, cx+6, cy-size+6, 1)

    elif direction == "S":

        display.line(cx, cy-size, cx, cy+size, 1)
        display.line(cx, cy+size, cx-6, cy+size-6, 1)
        display.line(cx, cy+size, cx+6, cy+size-6, 1)

    elif direction == "E":

        display.line(cx-size, cy, cx+size, cy, 1)
        display.line(cx+size, cy, cx+size-6, cy-6, 1)
        display.line(cx+size, cy, cx+size-6, cy+6, 1)

    elif direction == "W":

        display.line(cx-size, cy, cx+size, cy, 1)
        display.line(cx-size, cy, cx-size+6, cy-6, 1)
        display.line(cx-size, cy, cx-size+6, cy+6, 1)

    elif direction == "NE":

        display.line(cx-12, cy+12, cx+12, cy-12, 1)
        display.line(cx+12, cy-12, cx+2, cy-12, 1)
        display.line(cx+12, cy-12, cx+12, cy-2, 1)

    elif direction == "NW":

        display.line(cx+12, cy+12, cx-12, cy-12, 1)
        display.line(cx-12, cy-12, cx-2, cy-12, 1)
        display.line(cx-12, cy-12, cx-12, cy-2, 1)

    elif direction == "SE":

        display.line(cx-12, cy-12, cx+12, cy+12, 1)
        display.line(cx+12, cy+12, cx+2, cy+12, 1)
        display.line(cx+12, cy+12, cx+12, cy+2, 1)

    elif direction == "SW":

        display.line(cx+12, cy-12, cx-12, cy+12, 1)
        display.line(cx-12, cy+12, cx-2, cy+12, 1)
        display.line(cx-12, cy+12, cx-12, cy+2, 1)


# -------------------------
# DIRECTION LOGIC
# -------------------------

def get_direction(diff):

    if diff < 22.5 or diff >= 337.5:
        return "N"
    elif diff < 67.5:
        return "NE"
    elif diff < 112.5:
        return "E"
    elif diff < 157.5:
        return "SE"
    elif diff < 202.5:
        return "S"
    elif diff < 247.5:
        return "SW"
    elif diff < 292.5:
        return "W"
    else:
        return "NW"


# -------------------------
# STARTUP
# -------------------------

startup_screen()

arrived = False


# -------------------------
# MAIN LOOP
# -------------------------

while True:

    gps.update()

    mag_x, mag_y, mag_z = mag.magnetic

    heading = math.degrees(math.atan2(mag_y, mag_x))
    heading += DECLINATION
    heading %= 360

    display.fill(0)

    if gps.has_fix:

        lat = gps.latitude
        lon = gps.longitude

        nearest_store, nearest_dist = get_closest_store(lat, lon)

        # DESTINATION REACHED
        if nearest_dist <= DESTINATION_THRESHOLD:

            arrived = True
            destination_screen(nearest_store[0])

        else:

            arrived = False

            target_bearing = bearing(lat, lon, nearest_store[1], nearest_store[2])

            diff = (target_bearing - heading + 360) % 360

            direction = get_direction(diff)

            draw_arrow(direction)

            display.text(nearest_store[0][:16], 0, 0, 1)
            display.text(str(int(nearest_dist)) + "m", 0, 54, 1)

            display.show()

    else:

        display.text("Waiting for GPS", 10, 28, 1)
        display.show()

    time.sleep(0.1)
