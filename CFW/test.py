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

def remote_cmd(my_command):
     os.system(f"tools/sshpass -p 'alpine' ssh -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -q -p2222 root@localhost {my_command}")

def check_remote_file_exists(remote_path):
    status = os.system(f"tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -q -p 2222 root@localhost 'test -f {remote_path}'")
    return status == 0

# ========= PATCH launchd (optool /cores/launchdhook.dylib) =========
# Make sure mount mnt1 before doing this!
remote_cmd("/sbin/mount_apfs -o rw /dev/disk1s1 /mnt1")


# remove if already exist
os.system("rm custom_26.1/launchd 2>/dev/null")
os.system("rm custom_26.1/launchd.bak 2>/dev/null")
# backup launchd before patch
file_path = "/mnt1/sbin/launchd.bak"
if not check_remote_file_exists(file_path): 
     print(f"Created backup ${file_path}")
     remote_cmd("/bin/cp /mnt1/sbin/launchd /mnt1/sbin/launchd.bak")
# grab launchd
os.system("tools/sshpass -p 'alpine' scp -q -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -P 2222 root@127.0.0.1:/mnt1/sbin/launchd.bak ./custom_26.1")
os.system("mv custom_26.1/launchd.bak custom_26.1/launchd")
# inject launchdhook.dylib 
os.system("tools/optool install -c load -p /cores/launchdhook.dylib -t custom_26.1/launchd")
# sign
os.system("tools/ldid_macosx_arm64 -S -M -Cadhoc custom_26.1/launchd")
# send to apply
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/launchd 'root@127.0.0.1:/mnt1/sbin/launchd'")
remote_cmd("/bin/chmod 0755 /mnt1/sbin/launchd")
# clean
os.system("rm custom_26.1/launchd 2>/dev/null")

# build & upload launchdhook.dylib & systemdhook.dylib & libellekit.dylib

os.system("cd jb/BaseBin/systemhook/ && make")
os.system("cd jb/BaseBin/launchdhook/ && make")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/BaseBin/systemhook/systemhook.dylib 'root@127.0.0.1:/mnt1/cores/systemhook.dylib'")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/BaseBin/launchdhook/launchdhook.dylib 'root@127.0.0.1:/mnt1/cores/launchdhook.dylib'")
os.system("tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 custom_26.1/libellekit.dylib 'root@127.0.0.1:/mnt1/cores/libellekit.dylib'")
# ========= END PATCH launchd (optool /cores/launchdhook.dylib) =========

# ========= halt =========
remote_cmd(f"/sbin/halt")