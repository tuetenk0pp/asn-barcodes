try:
    import sys
    import argparse
    import barcode
    from barcode import Code128
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
except:
    print("Unable to load libraries. Install them with 'pip install python-barcode reportlab'")
    sys.exit(1)

# Define arguments

def check_positive(value):
    try:
        value = int(value)
        if value <= 0:
            raise argparse.ArgumentTypeError("{} is not a positive integer".format(value))
    except:
        raise argparse.ArgumentTypeError("{} is not an integer".format(value))
    return value

parser = argparse.ArgumentParser(prog="asn-barcodes.py", description="This tool can be used to generate ASN Barcodes for paperless-ngx.")
parser.add_argument("--version", action="version", version="%(prog)s 1.0")
parser.add_argument("position", help="number of the first ASN-barcode to generate", metavar="POSITION", type=check_positive)
parser.add_argument("count", help="number of ASN-barcodes to generate", metavar="COUNT", type=check_positive)
parser.add_argument("--prefix", default="ASN", dest="prefix", help="ASN Prefix", metavar=None)
parser.add_argument("--output", default="asn-barcodes", dest="output", help="destination file name", metavar=None)
args = parser.parse_args()

start = int(args.position)
end = int(args.position) + int(args.count)

# Generate barcodes
barcodes = []
for i in range(start, end):
    barcode_value = args.prefix + str(i).zfill(4)
    barcode_image = Code128(barcode_value, writer=barcode.writer.ImageWriter()).render()
    barcodes.append((barcode_value, barcode_image))

# Create PDF document with barcodes formatted for Avery L7871 Labels
pdf_file = args.output + ".pdf"
c = canvas.Canvas(pdf_file, pagesize=A4)
width, height = A4
page_left_margin = 16.1 * mm
page_bottom_margin = 13.5 * mm
label_width = 25.4 * mm
label_height = 10 * mm
horizontal_gap = 0.25 * mm
vertical_gap = 0 * mm
rows = 27
columns = 7
x = page_left_margin
y = height - page_bottom_margin
for i, (barcode_value, barcode_image) in enumerate(barcodes):
    if i > 0 and i % (rows * columns) == 0:
        c.showPage()
        x = page_left_margin
        y = height - page_bottom_margin
    # Convert barcode image to BytesIO object
    barcode_image_file = BytesIO()
    barcode_image.save(barcode_image_file, format="PNG")
    barcode_image_file.seek(0)
    # Draw barcode image on label
    img = ImageReader(barcode_image_file)
    c.drawImage(img, x, y - label_height, width=label_width, height=label_height)
    x += label_width + horizontal_gap
    if i % columns == columns - 1:
        x = page_left_margin
        y -= label_height + vertical_gap
c.save()
print(f"Generated {i + 1} barcodes with ASN from {start} to {end-1} in ./{pdf_file}")