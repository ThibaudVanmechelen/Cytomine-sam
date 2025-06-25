import os
import urllib.request

WEIGHTS = {
    "weights.pt": "https://github.com/ThibaudVanmechelen/Cytomine-sam/blob/main/weights/weights.pt"
}

os.makedirs("weights", exist_ok = True)

for filename, url in WEIGHTS.items():
    destination = os.path.join("weights", filename)

    if not os.path.exists(destination):
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, destination)

    else:
        print(f"{filename} already exists.")
