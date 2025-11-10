import base64
from io import BytesIO
from PIL import Image


# Step 1: Path to the base64-encoded output file (update if needed)
b64_path = "loss_curve_b64.txt"  # or the path Azure saved (e.g. downloaded manually)
output_png = "loss_curve.png"

# Step 2: Read and decode the base64 image
with open(b64_path, "r") as f:
    b64_string = f.read()

img_data = base64.b64decode(b64_string)
image = Image.open(BytesIO(img_data))

# Step 3: Save to PNG
image.save(output_png)
print(f"✅ Loss curve saved as {output_png}")

# Step 4: Optional — show image
try:
    image.show()
except OSError:
    # viewer/display not available in this environment
    print("Image saved, but preview not supported in this environment.")
