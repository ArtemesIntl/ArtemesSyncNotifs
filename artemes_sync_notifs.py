# (c) 2020 ARTEMES INTERNATIONAL, LLC.
#       WWW.MAISONARTEMES.COM
import board
import neopixel
import touchio
import adafruit_fancyled.adafruit_fancyled as fancy
from adafruit_bluefruit_connect.packet import Packet
from adafruit_bluefruit_connect.button_packet import ButtonPacket
from adafruit_bluefruit_connect.color_packet import ColorPacket
from adafruit_ble import BLERadio
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.nordic import UARTService

NUM_LEDS = 20             # number of ring LEDs
RIGHT_PIN = board.A1     # wiring
LEFT_PIN = board.A6
CPX_PIN = board.D8       # CPX Neopixels D8

touch_A2 = touchio.TouchIn(board.A2)
touch_A3 = touchio.TouchIn(board.A3)
touch_A4 = touchio.TouchIn(board.A4)
touch_A5 = touchio.TouchIn(board.A5)
touch_TX = touchio.TouchIn(board.TX)

# Online/Sync Mode
PALETTE_ARTEMES = [fancy.CRGB(0.0, 0.3, 0.7),  # Blue
                   fancy.CRGB(0.0, 0.0, 1.0),  # Blue
                   fancy.CRGB(27, 20, 100)]
                   # fancy.CRGB(95, 39, 205)] Purple

# Torch Mode
PALETTE_TORCH = [fancy.CRGB(255, 255, 255)]  # White

# Off Mode
PALETTE_OFF = [fancy.CRGB(0, 0, 0)]  # Black

# Alert Mode
PALETTE_ALERT = [fancy.CRGB(255, 0, 0),  # Red
                 fancy.CRGB(0, 0, 0),
                 fancy.CRGB(234, 65, 0)]  # Red

right = neopixel.NeoPixel(RIGHT_PIN, NUM_LEDS, brightness=1.0, auto_write=False)
left = neopixel.NeoPixel(LEFT_PIN, NUM_LEDS, brightness=1.0, auto_write=False)
cpx = neopixel.NeoPixel(CPX_PIN, NUM_LEDS, brightness=1.0, auto_write=False)

offset = 0  # color spin
offset_increment = 1
OFFSET_MAX = 1000000

# BLE
ble = BLERadio()
uart = UARTService()
advertisement = ProvideServicesAdvertisement(uart)

def set_palette(palette):
    for i in range(NUM_LEDS):
        color = fancy.palette_lookup(palette, (offset + i) / NUM_LEDS)
        color = fancy.gamma_adjust(color, brightness=1.0)
        right[i] = color.pack()
    right.show()

    for i in range(NUM_LEDS):
        color = fancy.palette_lookup(palette, (offset + i) / NUM_LEDS)
        color = fancy.gamma_adjust(color, brightness=1.0)
        left[i] = color.pack()
    left.show()

    for i in range(NUM_LEDS):
        color = fancy.palette_lookup(palette, (offset + i) / NUM_LEDS)
        color = fancy.gamma_adjust(color, brightness=1.0)
        cpx[i] = color.pack()
    cpx.show()

# palette on startup
palette_choice = PALETTE_ARTEMES

# palette cycling
cycling = True

# advertising?
advertising = False

while True:

    if cycling:
        set_palette(palette_choice)
        offset = (offset + offset_increment) % OFFSET_MAX

    if not ble.connected and not advertising:
        ble.start_advertising(advertisement)
        advertising = True

    # connected via Bluetooth
    if ble.connected:
        advertising = False
        if uart.in_waiting:
            packet = Packet.from_stream(uart)
            if isinstance(packet, ColorPacket):
                cycling = False
                # Set all pixels to one color
                right.fill(packet.color)
                left.fill(packet.color)
                cpx.fill(packet.color)
                right.show()
                left.show()
                cpx.show()
            elif isinstance(packet, ButtonPacket):
                cycling = True
                if packet.pressed:
                    if packet.button == ButtonPacket.BUTTON_1:
                        palette_choice = PALETTE_OFF
                    elif packet.button == ButtonPacket.BUTTON_2:
                        palette_choice = PALETTE_TORCH
                    elif packet.button == ButtonPacket.BUTTON_3:
                        palette_choice = PALETTE_ALERT
                        offset_increment = 6
                    elif packet.button == ButtonPacket.BUTTON_4:
                        palette_choice = PALETTE_ARTEMES
                        offset_increment = 1

                # animation speed
                    elif packet.button == ButtonPacket.UP:
                        offset_increment += 1
                    elif packet.button == ButtonPacket.DOWN:
                        offset_increment -= 1

    if touch_A2.value:
        cycling = True
        palette_choice = PALETTE_OFF
    elif touch_A3.value:
        cycling = True
        palette_choice = PALETTE_TORCH
    elif touch_A4.value:
        cycling = True
        palette_choice = PALETTE_ALERT
        offset_increment = 6
    elif touch_A5.value:
        cycling = True
        palette_choice = PALETTE_ARTEMES
        offset_increment = 1
