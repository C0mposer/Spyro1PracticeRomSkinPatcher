from PIL import Image

# Open the BMP file
image_path = 'output_image.bmp'  # Replace with your BMP file path
image = Image.open(image_path)

# Ensure the image is in RGBA format
image = image.convert('RGBA')

# Extract pixel data
pixels = list(image.getdata())

# Convert each pixel to a hex string
pixels_hex = [f'{r:02X}{g:02X}{b:02X}{a:02X}' for r, g, b, a in pixels]

# Print out the hex values
for hex_value in pixels_hex:
    print(hex_value)