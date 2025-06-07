# import modules
import qrcode
from PIL import Image

import argparse

parser = argparse.ArgumentParser(description="A resume generator script that takes some options to control the script output.")

parser.add_argument("-l", "--logo", help="Path of the logo image file to integrate into the qr code")
parser.add_argument("-w", "--width", help="Width of the logo image in pixels", type=int, default=100)
parser.add_argument("-u", "--url", help="URL or text to encode in the QR code", default="https://github.com/Nokheenig/")
parser.add_argument("-c", "--color", help="Color of the QR code", default='Black')
parser.add_argument("-e", "--error_correction", help="Error correction level for the QR code (L, M, Q, H)", default='H', choices=['L', 'M', 'Q', 'H'])
parser.add_argument("-s", "--size", help="Size of the QR code in pixels", type=int, default=300)
parser.add_argument("-f", "--file", help="Output file name for the QR code image", default='qr.png')

args = parser.parse_args()

# taking image which user wants 
# in the QR code center
Logo_link = args.logo if args.logo else "res/img/empty.jpg"

logo = Image.open(Logo_link)

# taking base width
basewidth = args.width if args.width else 100

# adjust image size
wpercent = (basewidth/float(logo.size[0]))
hsize = int((float(logo.size[1])*float(wpercent)))
logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)
QRcode = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    border=0
)

# taking url or text

# https://nokheenig.github.io/Python_TexResumeGenerator/
url = args.url if args.url else "https://github.com/Nokheenig/"

# adding URL or text to QRcode
QRcode.add_data(url)

# generating QR code
QRcode.make()

# taking color name from user
QRcolor = args.color if args.color else "Black"

# adding color to QR code
QRimg = QRcode.make_image(
    fill_color=QRcolor, back_color="white").convert('RGB')

# set size of QR code
pos = ((QRimg.size[0] - logo.size[0]) // 2,
       (QRimg.size[1] - logo.size[1]) // 2)
QRimg.paste(logo, pos)

# save the QR code generated
output_file = args.file if args.file else 'qr.png'
QRimg.save(output_file)

print('QR code generated!')