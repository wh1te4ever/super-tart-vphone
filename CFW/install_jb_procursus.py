import struct
import os
import sys
import subprocess
import plistlib
import glob
from pathlib import Path

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

def get_bootManifestHash():
    cmd = "tools/sshpass -p 'alpine' ssh -o StrictHostKeyChecking=no -q -p 2222 root@localhost '/bin/ls /mnt5'"
    output = subprocess.getoutput(cmd).split()
    
    return next((f for f in output if len(f) == 96), None)

remote_cmd("/sbin/mount_apfs -o rw /dev/disk1s5 /mnt5")
bootManifestHash = get_bootManifestHash()

# ============ send procursus bootstrap and unpack ============
os.system("zstd -d jb/bootstrap-iphoneos-arm64.tar.zst -o jb/bootstrap-iphoneos-arm64.tar")
os.system(f"tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/bootstrap-iphoneos-arm64.tar 'root@127.0.0.1:/mnt5/{bootManifestHash}'")
os.system(f"tools/sshpass -p 'alpine' scp -q -r -ostricthostkeychecking=false -ouserknownhostsfile=/dev/null -o StrictHostKeyChecking=no -P 2222 jb/org.coolstar.sileo_2.5.1_iphoneos-arm64.deb 'root@127.0.0.1:/mnt5/{bootManifestHash}'")

remote_cmd(f"/bin/mkdir -p /mnt5/{bootManifestHash}/jb-vphone")
remote_cmd(f"/bin/chmod 0755 /mnt5/{bootManifestHash}/jb-vphone")
remote_cmd(f"/usr/sbin/chown 0:0 /mnt5/{bootManifestHash}/jb-vphone")

remote_cmd(f"/usr/bin/tar --preserve-permissions -xkf /mnt5/{bootManifestHash}/bootstrap-iphoneos-arm64.tar -C /mnt5/{bootManifestHash}/jb-vphone/")
remote_cmd(f"/bin/mv /mnt5/{bootManifestHash}/jb-vphone/var /mnt5/{bootManifestHash}/jb-vphone/procursus")
remote_cmd(f"/bin/mv /mnt5/{bootManifestHash}/jb-vphone/procursus/jb/* /mnt5/{bootManifestHash}/jb-vphone/procursus")
remote_cmd(f"/bin/rm -rf /mnt5/{bootManifestHash}/jb-vphone/procursus/jb")

# clean 
remote_cmd(f"/bin/rm /mnt5/{bootManifestHash}/bootstrap-iphoneos-arm64.tar")
os.system("rm jb/bootstrap-iphoneos-arm64.tar")