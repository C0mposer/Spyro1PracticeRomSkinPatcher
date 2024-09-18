from PIL import Image
import sys
import os

def RGBToClutBGR(colour):
    # Extract the RGB components
    r = colour[0] >> 3  # Bottom 3 bits are lost
    g = colour[1] >> 3  # Bottom 3 bits are lost
    b = colour[2] >> 3  # Bottom 3 bits are lost
    
    # Combine them into a single 16-bit value
    return (b << 10) | (g << 5) | r


def RGBToClutTransparent(colour):
    # Extract the RGB components
    r = colour[0] >> 3  # Bottom 3 bits are lost
    g = colour[1] >> 3  # Bottom 3 bits are lost
    b = colour[2] >> 3  # Bottom 3 bits are lost
    
    # Combine into a 15-bit value
    converted = (b << 10) | (g << 5) | r
    
    converted |= 0x8000  # Set the most significant bit for transparency

    return converted


def ConvertToClutBinFile(path):
    filename = path
    img = Image.open(filename)
        
    width, height = img.size
    
    print('BMP Data:')
    print('Width :', width)
    print('Height:', height)

    rgb_img = img.convert('RGB')

    bmp_data = []
    sixteen_bit_bmp_data = [int]

    for y in range(height):
        for x in range(width):
            pixel = rgb_img.getpixel((x, y))
            #print(pixel)
            r, g, b = pixel
            print(f'| R: {hex(r)} | G: {hex(g)} | B: {hex(b)} |')
            
            # bmp_data.append(r)
            # bmp_data.append(g)
            # bmp_data.append(b)
            
            sixteen_bit_bmp_data.append(RGBToClutBGR(pixel))
            
    with open(filename + "_temp", "wb+") as file:
            for i, data in enumerate(sixteen_bit_bmp_data):
                
                # Needs to be alligned to an int, so place padding after the first section
                if i == 46:
                    file.write(int(0).to_bytes(2, signed=False, byteorder="little"))
                    
                file.write(data.to_bytes(2, signed=False, byteorder='little'))

    with open(filename + "_temp", 'rb') as in_file:
        with open(filename.split(".")[0] + ".bin", 'wb') as out_file:
            out_file.write(in_file.read()[1:])
       
    print("Deleting _temp file")          
    os.remove(filename + "_temp")
    
    return filename.split(".")[0] + ".bin"
            
def ConvertClutBinFileTransparent(path):
    filename = path
    img = Image.open(filename)
        
    width, height = img.size
    
    print('BMP Data:')
    print('Width :', width)
    print('Height:', height)

    rgb_img = img.convert('RGB')

    bmp_data = []
    sixteen_bit_bmp_data = [int]

    for y in range(height):
        for x in range(width):
            pixel = rgb_img.getpixel((x, y))
            #print(pixel)
            r, g, b = pixel
            print(f'| R: {hex(r)} | G: {hex(g)} | B: {hex(b)} |')
            
            # bmp_data.append(r)
            # bmp_data.append(g)
            # bmp_data.append(b)
            
            sixteen_bit_bmp_data.append(RGBToClutTransparent(pixel))
            
    with open(filename + "_temp", "wb+") as file:
            for i, data in enumerate(sixteen_bit_bmp_data):
                
                # Needs to be alligned to an int, so place padding after the first section
                if i == 46:
                    file.write(int(0).to_bytes(2, signed=False, byteorder="little"))
                    
                file.write(data.to_bytes(2, signed=False, byteorder='little'))

    with open(filename + "_temp", 'rb') as in_file:
        with open(filename.split(".")[0] + ".bin", 'wb') as out_file:
            out_file.write(in_file.read()[1:])
    
    print("Deleting _temp file")          
    os.remove(filename + "_temp")
    
def ConvertToRGB(path):

    # Open the BMP file
    image_path = path  # Replace with your BMP file path
    image = Image.open(image_path)

    # Ensure the image is in RGBA format
    image = image.convert('RGBA')

    # Extract pixel data
    pixels = list(image.getdata())

    # Convert each pixel to a hex string
    pixels_hex = [f'{r:02X}{g:02X}{b:02X}{a:02X}' for r, g, b, a in pixels]
    
    with open(image_path.split(".")[0] + ".bin", 'wb') as file:
            for i, data in enumerate(pixels):
                file.write(data[0].to_bytes(1, signed=False, byteorder='little'))
                file.write(data[1].to_bytes(1, signed=False, byteorder='little'))
                file.write(data[2].to_bytes(1, signed=False, byteorder='little'))
                file.write(data[3].to_bytes(1, signed=False, byteorder='little')) 


    # Print out the hex values
    for hex_value in pixels_hex:
        print(hex_value)