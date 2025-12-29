import os
base = "/mnt/v_drive/Codes/SKB/storage/visual_data"
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith(".png"):
            print(os.path.join(root, f))
