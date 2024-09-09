import sys
import qrcode

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img.save("qr_code.png")
    print("QR code generated and saved as qr_code.png")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python link2qr.py <URL>")
    else:
        url = sys.argv[1]
        generate_qr_code(url)
# By EFXTv
# Update V1 15 Aug 2024
