import qrcode
import io
import sys
import os

if os.path.isfile("/home/pi/kcb-config/scripts/qrcode.png"):
    os.remove("/home/pi/kcb-config/scripts/qrcode.png")

data = sys.argv[1]

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)
img = qr.make_image(fill_color='black', back_color='white')
img.save("/home/pi/kcb-config/scripts/qrcode.png")
