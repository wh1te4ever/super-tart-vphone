import struct
import os
import sys
import subprocess
import plistlib

fp = None

def patch(offset, data):
    file_offset = offset
    
    if isinstance(data, int):
        data = struct.pack('<I', data)
    if isinstance(data, str):
        data = data.encode()

    fp.seek(file_offset)
    fp.write(data)
    fp.flush()


def check_remote_file_exists(remote_path):
    status = os.system(f"tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -q -p 2222 root@localhost 'test -f {remote_path}'")
    return status == 0

def remote_cmd(my_command):
     os.system(f"tools/sshpass -p 'alpine' ssh -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -q -p2222 root@localhost {my_command}")

# ========= INSTALL CRYPTEX(SystemOS, AppOS) =========
# Grab and Decrypt Cryptex(SystemOS) AEA
key = subprocess.check_output("ipsw fw aea --key iPhone17,3_26.1_23B85_Restore/043-54303-126.dmg.aea", shell=True, text=True).strip()
print(f"key: {key}")
os.system(f"aea decrypt -i iPhone17,3_26.1_23B85_Restore/043-54303-126.dmg.aea -o CryptexSystemOS.dmg -key-value '{key}'")

# Grab Cryptex(AppOS)
os.system(f"cp iPhone17,3_26.1_23B85_Restore/043-54062-129.dmg CryptexAppOS.dmg")


# Mount CryptexSystemOS
os.system("mkdir CryptexSystemOS")
os.system("sudo hdiutil attach -mountpoint CryptexSystemOS CryptexSystemOS.dmg -owners off")

# Mount CryptexAppOS
os.system("mkdir CryptexAppOS")
os.system("sudo hdiutil attach -mountpoint CryptexAppOS CryptexAppOS.dmg -owners off")


# Prepare
remote_cmd("/sbin/mount_apfs -o rw /dev/disk1s1 /mnt1")

remote_cmd("/bin/rm -rf /mnt1/System/Cryptexes/App")
remote_cmd("/bin/rm -rf /mnt1/System/Cryptexes/OS")

remote_cmd("/bin/mkdir -p /mnt1/System/Cryptexes/App")
remote_cmd("/bin/chmod 0755 /mnt1/System/Cryptexes/App")
remote_cmd("/bin/mkdir -p /mnt1/System/Cryptexes/OS")
remote_cmd("/bin/chmod 0755 /mnt1/System/Cryptexes/OS")

# send Cryptex files to device
print("Copying cryptexs to vphone! Will take about 3 mintues...")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 CryptexSystemOS/. 'root@127.0.0.1:/mnt1/System/Cryptexes/OS'")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 CryptexAppOS/. 'root@127.0.0.1:/mnt1/System/Cryptexes/App'")

# Thanks nathan for idea
# /System/Library/Caches/com.apple.dyld -> /System/Cryptexes/OS/System/Library/Caches/com.apple.dyld/
remote_cmd("/bin/ln -sf ../../../System/Cryptexes/OS/System/Library/Caches/com.apple.dyld /mnt1/System/Library/Caches/com.apple.dyld")
# /System/DriverKit/System/Library/dyld -> /System/Cryptexes/OS/System/DriverKit/System/Library/dyld
remote_cmd("/bin/ln -sf ../../../../System/Cryptexes/OS/System/DriverKit/System/Library/dyld /mnt1/System/DriverKit/System/Library/dyld")



# ========= PATCH SEPUTIL =========
# remove if already exist
os.system("rm custom_26.1/seputil 2>/dev/null")
os.system("rm custom_26.1/seputil.bak 2>/dev/null")
# backup seputil before patch
file_path = "/mnt1/usr/libexec/seputil.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup {file_path}")
     remote_cmd("/bin/cp /mnt1/usr/libexec/seputil /mnt1/usr/libexec/seputil.bak")
# grab seputil
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/usr/libexec/seputil.bak ./custom_26.1")
os.system("mv custom_26.1/seputil.bak custom_26.1/seputil")
# patch seputil; prevent error "seputil: Gigalocker file (/mnt7/XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX.gl) doesn't exist: No such file or directory"
fp = open("custom_26.1/seputil", "r+b")
patch(0x1B3F1, "AA")
fp.close()
# sign
os.system("tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 -Icom.apple.seputil custom_26.1/seputil")
# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/seputil 'root@127.0.0.1:/mnt1/usr/libexec/seputil'")
remote_cmd("/bin/chmod 0755 /mnt1/usr/libexec/seputil")
# clean
os.system("rm custom_26.1/seputil 2>/dev/null")

# Change gigalocker filename to AA.gl
remote_cmd("/sbin/mount_apfs -o rw /dev/disk1s3 /mnt3")
remote_cmd("/bin/mv /mnt3/*.gl /mnt3/AA.gl")


# ========= INSTALL AppleParavirtGPUMetalIOGPUFamily =========
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/AppleParavirtGPUMetalIOGPUFamily.tar 'root@127.0.0.1:/mnt1'")
remote_cmd("/usr/bin/tar --preserve-permissions --no-overwrite-dir -xvf /mnt1/AppleParavirtGPUMetalIOGPUFamily.tar  -C /mnt1")
remote_cmd("/usr/sbin/chown -R 0:0 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle")
remote_cmd("/bin/chmod 0755 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle")
remote_cmd("/bin/chmod 0755 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/libAppleParavirtCompilerPluginIOGPUFamily.dylib")
remote_cmd("/bin/chmod 0755 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/AppleParavirtGPUMetalIOGPUFamily")
remote_cmd("/bin/chmod 0755 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/_CodeSignature")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/_CodeSignature/CodeResources")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/Info.plist")
remote_cmd("/bin/rm /mnt1/AppleParavirtGPUMetalIOGPUFamily.tar")


# ========= INSTALL iosbinpack64 =========
# Send to rootfs
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/iosbinpack64.tar 'root@127.0.0.1:/mnt1'")
# Unpack 
remote_cmd("/usr/bin/tar --preserve-permissions --no-overwrite-dir -xvf /mnt1/iosbinpack64.tar  -C /mnt1")
remote_cmd("/bin/rm /mnt1/iosbinpack64.tar")
# Setup initial dropbear after normal boot
'''
/iosbinpack64/bin/mkdir -p /var/dropbear
/iosbinpack64/bin/cp /iosbinpack64/etc/profile /var/profile
/iosbinpack64/bin/cp /iosbinpack64/etc/motd /var/motd
'''


# ========= PATCH launchd_cache_loader (patch required if modifying /System/Library/xpc/launchd.plist) =========
# remove if already exist
os.system("rm custom_26.1/launchd_cache_loader 2>/dev/null")
os.system("rm custom_26.1/launchd_cache_loader.bak 2>/dev/null")
# backup launchd_cache_loader before patch
file_path = "/mnt1/usr/libexec/launchd_cache_loader.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup {file_path}")
     remote_cmd("/bin/cp /mnt1/usr/libexec/launchd_cache_loader /mnt1/usr/libexec/launchd_cache_loader.bak")
# grab launchd_cache_loader
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/usr/libexec/launchd_cache_loader.bak ./custom_26.1")
os.system("mv custom_26.1/launchd_cache_loader.bak custom_26.1/launchd_cache_loader")
# patch to apply launchd_unsecure_cache=1
fp = open("custom_26.1/launchd_cache_loader", "r+b")
patch(0xB58, 0xd503201f)
fp.close()
# sign
os.system("tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 -Icom.apple.launchd_cache_loader custom_26.1/launchd_cache_loader")
# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/launchd_cache_loader 'root@127.0.0.1:/mnt1/usr/libexec/launchd_cache_loader'")
remote_cmd("/bin/chmod 0755 /mnt1/usr/libexec/launchd_cache_loader")
# clean
os.system("rm custom_26.1/launchd_cache_loader 2>/dev/null")


# ========= PATCH mobileactivationd (bypass activation lock) =========
# remove if already exist
os.system("rm custom_26.1/mobileactivationd 2>/dev/null")
os.system("rm custom_26.1/mobileactivationd.bak 2>/dev/null")
# backup mobileactivationd before patch
file_path = "/mnt1/usr/libexec/mobileactivationd.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup {file_path}")
     remote_cmd("/bin/cp /mnt1/usr/libexec/mobileactivationd /mnt1/usr/libexec/mobileactivationd.bak")
# grab mobileactivationd
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/usr/libexec/mobileactivationd.bak ./custom_26.1")
os.system("mv custom_26.1/mobileactivationd.bak custom_26.1/mobileactivationd")
# hackivation patch; always return true from bool __cdecl -[DeviceType should_hactivate]
fp = open("custom_26.1/mobileactivationd", "r+b")
patch(0x2F5F84, 0xD2800020) #mov x0, #1
fp.close()
# sign
os.system("tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 custom_26.1/mobileactivationd")
# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/mobileactivationd 'root@127.0.0.1:/mnt1/usr/libexec/mobileactivationd'")
remote_cmd("/bin/chmod 0755 /mnt1/usr/libexec/mobileactivationd")
# clean
os.system("rm custom_26.1/mobileactivationd 2>/dev/null")


# ========= PATCH launchd (prevent jetsam panic?) =========
'''
apfs_log_op_with_proc:3297: disk3s1 mount-complete volume Xcode_iOS_DDI, requested by: MobileStorageMounter (pid 323); parent: launchd (pid 1)
panic(cpu 0 caller 0xfffffe00431a59c8):  initproc exited -- exit reason namespace 7 subcode 0x1 description: jetsam property category (Daemon) is not initialized
'''
# Make sure mount mnt1 before doing this!
# remove if already exist
os.system("rm custom_26.1/launchd 2>/dev/null")
os.system("rm custom_26.1/launchd.bak 2>/dev/null")
# backup launchd before patch
file_path = "/mnt1/sbin/launchd.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup {file_path}")
     remote_cmd("/bin/cp /mnt1/sbin/launchd /mnt1/sbin/launchd.bak")
# grab launchd
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/sbin/launchd.bak ./custom_26.1")
os.system("mv custom_26.1/launchd.bak custom_26.1/launchd")
# prevent jetsam panic
'''
apfs_log_op_with_proc:3297: disk3s1 mount-complete volume Xcode_iOS_DDI, requested by: MobileStorageMounter (pid 323); parent: launchd (pid 1)
panic(cpu 0 caller 0xfffffe00431a59c8):  initproc exited -- exit reason namespace 7 subcode 0x1 description: jetsam property category (Daemon) is not initialized
'''
fp = open("custom_26.1/launchd", "r+b")
patch(0xd73c, 0x14000017) #b #0x5c
fp.close()
# sign
os.system("tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 custom_26.1/launchd")
# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/launchd 'root@127.0.0.1:/mnt1/sbin/launchd'")
remote_cmd("/bin/chmod 0755 /mnt1/sbin/launchd")
# clean
os.system("rm custom_26.1/launchd 2>/dev/null")
# ========= END PATCH launchd (prevent jetsam panic?) =========



# ========= MAKE RUN bash, dropbear, trollvnc automatically when boot =========
# Send plist to /System/Library/LaunchDaemons
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/LaunchDaemons/bash.plist 'root@127.0.0.1:/mnt1/System/Library/LaunchDaemons'")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/LaunchDaemons/dropbear.plist 'root@127.0.0.1:/mnt1/System/Library/LaunchDaemons'")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/LaunchDaemons/trollvnc.plist 'root@127.0.0.1:/mnt1/System/Library/LaunchDaemons'")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/LaunchDaemons/bash.plist")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/LaunchDaemons/dropbear.plist")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/LaunchDaemons/trollvnc.plist")

# Edit /System/Library/xpc/launchd.plist 
# remove if already exist
os.system("rm custom_26.1/launchd.plist 2>/dev/null")
os.system("rm custom_26.1/launchd.plist.bak 2>/dev/null")
# backup launchd.plist before patch
file_path = "/mnt1/System/Library/xpc/launchd.plist.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup {file_path}")
     remote_cmd("/bin/cp /mnt1/System/Library/xpc/launchd.plist /mnt1/System/Library/xpc/launchd.plist.bak")
# grab launchd.plist
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/System/Library/xpc/launchd.plist.bak ./custom_26.1")
os.system("mv custom_26.1/launchd.plist.bak custom_26.1/launchd.plist")

# Inject bash, dropbear, trollvnc to launchd.plist
os.system("plutil -convert xml1 custom_26.1/launchd.plist")

# 1. bash
target_file = 'custom_26.1/launchd.plist'
source_file = 'jb/LaunchDaemons/bash.plist'
insert_key  = '/System/Library/LaunchDaemons/bash.plist'

with open(target_file, 'rb') as ft, open(source_file, 'rb') as fs:
    target_data = plistlib.load(ft)
    source_data = plistlib.load(fs)

target_data.setdefault('LaunchDaemons', {})[insert_key] = source_data

with open(target_file, 'wb') as f:
    plistlib.dump(target_data, f, sort_keys=False)

# 2. dropbear
source_file = 'jb/LaunchDaemons/dropbear.plist'
insert_key  = '/System/Library/LaunchDaemons/dropbear.plist'

with open(target_file, 'rb') as ft, open(source_file, 'rb') as fs:
    target_data = plistlib.load(ft)
    source_data = plistlib.load(fs)

target_data.setdefault('LaunchDaemons', {})[insert_key] = source_data

with open(target_file, 'wb') as f:
    plistlib.dump(target_data, f, sort_keys=False)

# 3. trollvnc
source_file = 'jb/LaunchDaemons/trollvnc.plist'
insert_key  = '/System/Library/LaunchDaemons/trollvnc.plist'

with open(target_file, 'rb') as ft, open(source_file, 'rb') as fs:
    target_data = plistlib.load(ft)
    source_data = plistlib.load(fs)

target_data.setdefault('LaunchDaemons', {})[insert_key] = source_data

with open(target_file, 'wb') as f:
    plistlib.dump(target_data, f, sort_keys=False)

# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/launchd.plist 'root@127.0.0.1:/mnt1/System/Library/xpc'")
remote_cmd("/bin/chmod 0644 /mnt1/System/Library/xpc/launchd.plist")
# clean
os.system("rm custom_26.1/launchd.plist 2>/dev/null")
# ========= End of MAKE RUN bash, dropbear, trollvnc automatically when boot =========


# done
remote_cmd("/sbin/umount /mnt1")
remote_cmd("/sbin/umount /mnt3")

#Detach
os.system("sudo hdiutil detach -force CryptexSystemOS")
os.system("sudo hdiutil detach -force CryptexAppOS")

# Clean
os.system("rm -rf CryptexSystemOS")
os.system("rm -rf CryptexSystemOS.dmg")
os.system("rm -rf CryptexAppOS")
os.system("rm -rf CryptexAppOS.dmg")
