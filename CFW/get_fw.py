import requests
import os

def download_file(url):
    local_filename = url.split('/')[-1]

    if os.path.exists(local_filename):
        print(f"Skipping download_file: '{local_filename}' already exists.")
        return

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def unzip_file(zip_path, target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"Created directory: {target_dir}")
    else:
        print(f"Skipping extract '{zip_path}' firmware")
        return

    print(f"Unzipping {zip_path} to {target_dir}...")
    exit_code = os.system(f"unzip -o '{zip_path}' -d '{target_dir}'")

    if exit_code == 0:
        print("Unzip successful.")
    else:
        print(f"Unzip failed with code: {exit_code}")

os.system(f"chmod +x tools/*")

# 1. Download
# iPhone 16 / 26.1 (23B85)
print("Downloading iPhone 16 / 26.1 (23B85)...")
target_url = "https://updates.cdn-apple.com/2025FallFCS/fullrestores/089-13864/668EFC0E-5911-454C-96C6-E1063CB80042/iPhone17,3_26.1_23B85_Restore.ipsw"
download_file(target_url)

# cloudOS 26.1 (23B85)
print("Downloading cloudOS 26.1 (23B85)...")
target_url = "https://updates.cdn-apple.com/private-cloud-compute/399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349"
download_file(target_url)

# 2. extract two things
unzip_file("iPhone17,3_26.1_23B85_Restore.ipsw", "iPhone17,3_26.1_23B85_Restore")
unzip_file("399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349", "399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted")

# 3. Import things from cloudOS
# kernelcache
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/kernelcache.* iPhone17,3_26.1_23B85_Restore")
# agx, all_flash, ane, dfu, pmp...
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/agx/* iPhone17,3_26.1_23B85_Restore/Firmware/agx")
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/all_flash/* iPhone17,3_26.1_23B85_Restore/Firmware/all_flash")
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/ane/* iPhone17,3_26.1_23B85_Restore/Firmware/ane")
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/dfu/* iPhone17,3_26.1_23B85_Restore/Firmware/dfu")
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/pmp/* iPhone17,3_26.1_23B85_Restore/Firmware/pmp")
# sptm, txm, etc...
os.system("cp 399b664dd623358c3de118ffc114e42dcd51c9309e751d43bc949b98f4e31349_extracted/Firmware/*.im4p iPhone17,3_26.1_23B85_Restore/Firmware")


# 4. TODO: parse what things needed from BuildManifest.plist, Restore.plist in cloudOS 26.1
# It will be really complicated, so import things from already parse completed
os.system("sudo cp custom_26.1/BuildManifest.plist iPhone17,3_26.1_23B85_Restore")
os.system("sudo cp custom_26.1/Restore.plist iPhone17,3_26.1_23B85_Restore")

os.system("echo 'Done, grabbed all needed components for restoring'")