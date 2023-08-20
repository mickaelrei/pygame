import pygame, math, os.path

# File that will have ascii text
OUTPUT_FILE = "../output.txt"

# Image to read
IMAGE_FILE = "mario.png"

# List of characters to represent brightness
CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

##################################################################
##################################################################
##################################################################
dirName = os.path.dirname(__file__)

# Load image
imageSurf = pygame.image.load(os.path.join(dirName, f"img/{IMAGE_FILE}"))

# Output text
outputText = ""

for y in range(imageSurf.get_height()):
    for x in range(imageSurf.get_width()):
        # Pixel color
        color = imageSurf.get_at((x, y))

        # Value from 0 to 1 of how bright
        # luminosity = (color.r / 255 + color.g / 255 + color.b / 255) / 3
        luminosity = color.hsla[2] / 100

        # Get correspondent char for this color (inverse)
        charIdx = math.floor(luminosity * (len(CHARS) - 1))

        # Add to output text
        outputText += CHARS[charIdx]

    # End of line
    outputText += "\n"

# Write to file
with open(os.path.join(dirName, OUTPUT_FILE), 'w', encoding='utf-8') as file:
    file.write(outputText)