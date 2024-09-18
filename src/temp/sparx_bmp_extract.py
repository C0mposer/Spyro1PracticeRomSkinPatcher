from PIL import Image

# RGB pixel values in hex format
pixels_hex = [
    "7B5A00FF", "CFA114FF", "644809FF", "4C2259FF", "92690DFF", "976C0FFF", "FF9FFFFF", "AE3EBFFF", "FFDA00FF",
    "FFF400FF", "E75AFFFF", "8A2BABFF", "FFC300FF", "594200FF", "E79FFFFF", "FFDA00FF", "FFF400FF", "CE5AFFFF",
    "8E2CB0FF", "FFC300FF", "FFDD00FF", "4B4100FF", "9870B2FF", "9B45B6FF", "A57312FF", "C99F00FF", "FFE56CFF",
    "645500FF", "5A4609FF", "FFBCFFFF", "C99D8CFF", "D9D934FF", "B59412FF", "FFF352FF", "FCD351FF", "E7DAFFFF",
    "A347C9FF", "8C6400FF", "5A5800FF", "977F00FF", "FFFF73FF", "F7C323FF", "5A4300FF", "976F00FF", "C974B5FF",
    "FCEA51FF", "8757ABFF", "FFFFFFFF", "CAC4FFFF", "FFDD30FF", "CAC3FEFF", "FFFFCBFF", "FFFFA2FF"
]

# Convert the hex values to RGBA tuples
pixels = [(int(px[0:2], 16), int(px[2:4], 16), int(px[4:6], 16), int(px[6:8], 16)) for px in pixels_hex]

# Define the image dimensions (width, height)
width, height = 9, 6  # 9 * 6 = 54 pixels

# Create a new image with RGBA mode
image = Image.new('RGBA', (width, height))

# Put the pixel data into the image
image.putdata(pixels)

# Save the image as BMP
image.save('output_image.bmp')
print("BMP file has been created successfully.")