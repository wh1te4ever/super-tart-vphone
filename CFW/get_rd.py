import struct
import os
import sys
import glob
import subprocess
from pathlib import Path

if not os.path.exists("vphone.shsh"):
    print("vphone.shsh not exist, please put this location")
    sys.exit()

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

os.system("rm -rf Ramdisk")
os.system("mkdir Ramdisk")

os.system("pyimg4 im4m  extract -i vphone.shsh -o vphone.im4m")

# 1. Grab & Patch iBSS 
if not os.path.exists("iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak"):
    os.system("cp iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak")
os.system("tools/img4 -i iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak -o iBSS.vresearch101.RELEASE")
fp = open("iBSS.vresearch101.RELEASE", "r+b")
# notice currently what loaded to serial log
patch(0x84349, "Loaded iBSS")
patch(0x843F4, "Loaded iBSS")
# patch image4_validate_property_callback
patch(0x9D10, 0xd503201f)   #nop
patch(0x9D14, 0xd2800000)   #mov x0, #0
fp.close()

os.system("tools/img4tool -c iBSS.vresearch101.RELEASE.im4p -t ibss iBSS.vresearch101.RELEASE")
os.system("tools/img4 -i iBSS.vresearch101.RELEASE.im4p -o ./Ramdisk/iBSS.vresearch101.RELEASE.img4 -M ./vphone.im4m")



# 2. Grab & Patch iBEC
if not os.path.exists("iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p.bak"):
    os.system("cp iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p.bak")
os.system("tools/img4 -i iPhone17\\,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p -o iBEC.vresearch101.RELEASE")
fp = open("iBEC.vresearch101.RELEASE", "r+b")
# notice currently what loaded to serial log
patch(0x84349, "Loaded iBEC")
patch(0x843F4, "Loaded iBEC")
# patch image4_validate_property_callback
patch(0x9D10, 0xd503201f)   #nop
patch(0x9D14, 0xd2800000)   #mov x0, #0
# patch boot-args with "serial=3 -v debug=0x2014e %s"
patch(0x122d4, 0xd0000082)  #adrp x2, #0x12000
patch(0x122d8, 0x9101c042)  #add x2, x2, #0x70
patch(0x24070, "serial=3 rd=md0 debug=0x2014e -v wdt=-1 %s\x00")
fp.close()
os.system("tools/img4tool -c iBEC.vresearch101.RELEASE.im4p -t ibec iBEC.vresearch101.RELEASE")
os.system("tools/img4 -i iBEC.vresearch101.RELEASE.im4p -o Ramdisk/iBEC.vresearch101.RELEASE.img4 -M vphone.im4m")

# 3. Grab SPTM
os.system("tools/img4 -i iPhone17\\,3_26.1_23B85_Restore/Firmware/sptm.vresearch1.release.im4p -o Ramdisk/sptm.vresearch1.release.img4 -M vphone.im4m -T sptm")

# 4. Grab devicetree
os.system("tools/img4 -i iPhone17\\,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p -o Ramdisk/DeviceTree.vphone600ap.img4 -M vphone.im4m -T rdtr")

# 5. Grab sep
os.system("tools/img4 -i iPhone17\\,3_26.1_23B85_Restore/Firmware/all_flash/sep-firmware.vresearch101.RELEASE.im4p -o Ramdisk/sep-firmware.vresearch101.RELEASE.img4 -M vphone.im4m -T rsep")



# 6. Grab & Patch TXM
if not os.path.exists("iPhone17\\,3_26.1_23B85_Restore/Firmware/txm.iphoneos.release.im4p.bak"):
    os.system("cp iPhone17\\,3_26.1_23B85_Restore/Firmware/txm.iphoneos.release.im4p iPhone17\\,3_26.1_23B85_Restore/Firmware/txm.iphoneos.release.im4p.bak")
os.system("pyimg4 im4p extract -i iPhone17\\,3_26.1_23B85_Restore/Firmware/txm.iphoneos.release.im4p.bak -o txm.raw")
# patch 
fp = open("txm.raw", "r+b")
patch(0x2c1f8, 0xd2800000)
fp.close()
#create im4p
os.system("pyimg4 im4p create -i txm.raw -o txm.im4p -f trxm --lzfse")
# preserve payp structure
txm_im4p_data = Path('iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.release.im4p.bak').read_bytes()
payp_offset = txm_im4p_data.rfind(b'PAYP')
if payp_offset == -1:
    print("Couldn't find payp structure !!!")
    sys.exit()

with open('txm.im4p', 'ab') as f:
    f.write(txm_im4p_data[(payp_offset-10):])

payp_sz = len(txm_im4p_data[(payp_offset-10):])
print(f"payp sz: {payp_sz}")

txm_im4p_data = bytearray(open('txm.im4p', 'rb').read())
txm_im4p_data[2:5] = (int.from_bytes(txm_im4p_data[2:5], 'big') + payp_sz).to_bytes(3, 'big')
open('txm.im4p', 'wb').write(txm_im4p_data)

# sign
os.system("pyimg4 img4 create -p txm.im4p -o Ramdisk/txm.img4 -m vphone.im4m")





# 7. Grab & patch kernelcache
if not os.path.exists("iPhone17\\,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak"):
    os.system("cp iPhone17\\,3_26.1_23B85_Restore/kernelcache.research.vphone600 iPhone17\\,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak")
os.system("pyimg4 im4p extract -i iPhone17\\,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak -o kcache.raw")
# patch 
fp = open("kcache.raw", "r+b")

# other patches are for jailbreak! might not be needed!
# __Z30_proc_check_launch_constraintsP4prociiPvmP22launch_constraint_dataPPcPm
patch(0x163863c, 0x52800000) 
patch(0x163863c+4, 0xd65f03c0) 

#_PE_i_can_has_debugger
patch(0x12c8138, 0xd2800020)
patch(0x12c8138+4, 0xd65f03c0)

# __ZL14postValidationP8LazyPathP7cs_blobjP12OSDictionaryhbjPKcPPcPm
patch(0x16405ac, 0x6B00001F) 
# __ZL27_check_dyld_policy_internalP4procyPy
patch(0x16410bc, 0x52800020) 
patch(0x16410c8, 0x52800020) 
# _apfs_graft
patch(0x242011c, 0x52800000) 
# _apfs_vfsop_mount
patch(0x2475044, 0xeb00001f) 
# _apfs_mount_upgrade_checks
patch(0x2476c00, 0x52800000) 
# _handle_fsioc_graft
patch(0x248c800, 0x52800000) 
# skip 2 patches; "_syscallmask_apply_to_proc"  (trace: 18, 19; 0x23fa3e0, 0x23fa40a)
# skip 1 patch; (trace: 20; 0x2943944)
# _hook_file_check_mmap
patch(0x23ac528, 0xD2800000)
patch(0x23ac528+4, 0xd65f03c0)
# _hook_mount_check_mount
patch(0x23aab58, 0xD2800000)
patch(0x23aab58+4, 0xd65f03c0)
# _hook_mount_check_remount
patch(0x23aa9a0, 0xD2800000)
patch(0x23aa9a0+4, 0xd65f03c0)
# _hook_mount_check_umount (trace: 24)
patch(0x23aa80c, 0xD2800000)
patch(0x23aa80c+4, 0xd65f03c0)
# _hook_vnode_check_rename (trace: 25)
patch(0x23a5514, 0xD2800000)
patch(0x23a5514+4, 0xd65f03c0)

fp.close()

#create im4p
os.system("pyimg4 im4p create -i kcache.raw -o krnl.im4p -f rkrn --lzfse")

# preserve payp structure
kernel_im4p_data = Path('iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak').read_bytes()
payp_offset = kernel_im4p_data.rfind(b'PAYP')
if payp_offset == -1:
    print("Couldn't find payp structure !!!")
    sys.exit()

with open('krnl.im4p', 'ab') as f:
    f.write(kernel_im4p_data[(payp_offset-10):])

payp_sz = len(kernel_im4p_data[(payp_offset-10):])
print(f"payp sz: {payp_sz}")

kernel_im4p_data = bytearray(open('krnl.im4p', 'rb').read())
kernel_im4p_data[2:5] = (int.from_bytes(kernel_im4p_data[2:5], 'big') + payp_sz).to_bytes(3, 'big')
open('krnl.im4p', 'wb').write(kernel_im4p_data)

# sign
os.system("pyimg4 img4 create -p krnl.im4p -o Ramdisk/krnl.img4 -m vphone.im4m")






# 8. Grab ramdisk & build custom ramdisk
os.system("pyimg4 im4p extract -i iPhone17,3_26.1_23B85_Restore/043-53775-129.dmg -o ramdisk.dmg")
# sys.stdin.read(1)
os.system("mkdir SSHRD")
os.system("sudo hdiutil attach -mountpoint SSHRD ramdisk.dmg -owners off")
os.system("sudo hdiutil create -size 254m -imagekey diskimage-class=CRawDiskImage -format UDZO -fs APFS -layout NONE -srcfolder SSHRD -copyuid root ramdisk1.dmg")
os.system("sudo hdiutil detach -force SSHRD")
os.system("sudo hdiutil attach -mountpoint SSHRD ramdisk1.dmg -owners off")

#remove unneccessary files for expand space
os.system("sudo tools/gtar -x --no-overwrite-dir -f ssh.tar.gz -C SSHRD/")
os.system("rm SSHRD/usr/bin/img4tool")
os.system("rm SSHRD/usr/bin/img4")
os.system("rm SSHRD/usr/sbin/dietappleh13camerad")
os.system("rm SSHRD/usr/sbin/dietappleh16camerad")
os.system("rm SSHRD/usr/local/bin/wget")
os.system("rm SSHRD/usr/local/bin/procexp")
# sys.stdin.read(1)

#resign all things preserving ents
target_path= [
    "SSHRD/usr/local/bin/*", "SSHRD/usr/local/lib/*",
    "SSHRD/usr/bin/*", "SSHRD/bin/*",
    "SSHRD/usr/lib/*", "SSHRD/sbin/*", "SSHRD/usr/sbin/*", "SSHRD/usr/libexec/*"
]
for pattern in target_path:
    for path in glob.glob(pattern):
        if os.path.isfile(path) and not os.path.islink(path):
            if "Mach-O" in subprocess.getoutput(f"file \"{path}\""):
                os.system(f"tools/ldid_macosx_arm64 -S -M -Ksigncert.p12 \"{path}\"")
# Fix sftp-server not working
os.system(f"tools/ldid_macosx_arm64 -Ssftp_server_ents.plist -M -Ksigncert.p12 SSHRD/usr/libexec/sftp-server")


#8-2. Grab & build custom ramdisk's trustcache while building custom ramdisk
os.system("pyimg4 im4p extract -i iPhone17,3_26.1_23B85_Restore/Firmware/043-53775-129.dmg.trustcache -o trustcache.raw")
os.system("tools/trustcache_macos_arm64 create sshrd.tc SSHRD")
os.system("pyimg4 im4p create -i sshrd.tc -o trustcache.im4p -f rtsc")
# sign
os.system("pyimg4 img4 create -p trustcache.im4p -o Ramdisk/trustcache.img4 -m vphone.im4m")
#8-2. end

os.system("sudo hdiutil detach -force SSHRD")
os.system("sudo hdiutil resize -sectors min ramdisk1.dmg")
# sign
os.system("pyimg4 im4p create -i ramdisk1.dmg -o ramdisk1.dmg.im4p -f rdsk")
os.system("pyimg4 img4 create -p ramdisk1.dmg.im4p -o Ramdisk/ramdisk.img4 -m vphone.im4m")







# Finally,,, clean
os.system("rm trustcache.raw")
os.system("rm trustcache.im4p")
os.system("rm sshrd.tc")
os.system("rm ramdisk.dmg")
os.system("rm ramdisk1.dmg")
os.system("rm ramdisk1.dmg.im4p")
os.system("rm iBEC.vresearch101.RELEASE")
os.system("rm iBEC.vresearch101.RELEASE.im4p")
os.system("rm iBSS.vresearch101.RELEASE")
os.system("rm iBSS.vresearch101.RELEASE.im4p")
os.system("rm vphone.im4m")
os.system("rm txm.raw")
os.system("rm txm.im4p")
os.system("rm krnl.im4p")
os.system("rm kcache.raw")
os.system("rm -rf SSHRD")