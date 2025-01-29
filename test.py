from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector

# Path to the image you want to crop
image_path = '1733695040563_Taboo.jpg'  # Replace with the path to your image

# Load the image
img = Image.open(image_path)

# Convert to RGB if needed (for better handling)
img = img.convert('RGB')

# Function to be called when the user selects the region for cropping
def onselect(eclick, erelease):
    # Get the coordinates of the rectangle drawn by the user
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
    
    # Print the coordinates to the terminal
    print(f"Cropping coordinates: left={x1}, upper={y1}, right={x2}, bottom={y2}")
    
    # Optionally, you can crop and show the selected area
    cropped_img = img.crop((x1, y1, x2, y2))
    
    # Show the cropped image
    plt.imshow(cropped_img)
    plt.title(f"Cropped Region: left={x1}, upper={y1}, right={x2}, bottom={y2}")
    plt.show()

# Create a plot to display the image
fig, ax = plt.subplots()
ax.imshow(img)

# Create a RectangleSelector to select the region for cropping
rectangle_selector = RectangleSelector(ax, onselect, useblit=True,
                                      button=[1],  # Left mouse button
                                      minspanx=5, minspany=5, spancoords='pixels',
                                      interactive=True)

plt.show()
