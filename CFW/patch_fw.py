import struct
import os
import sys
import glob
import subprocess
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

# Patch iBSS
if not os.path.exists("iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak"):
    os.system("cp iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak")
os.system("tools/img4 -i iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p.bak -o iBSS.vresearch101.RELEASE")
fp = open("iBSS.vresearch101.RELEASE", "r+b")
# notice currently what loaded to serial log
patch(0x84349, "Loaded iBSS")
patch(0x843F4, "Loaded iBSS")
# patch image4_validate_property_callback
patch(0x9D10, 0xd503201f)   #nop
patch(0x9D14, 0xd2800000)   #mov x0, #0
# patch not to call generate_nonce; keep apnonce
patch(0x1b544, 0x1400000e)  #b #0x38
fp.close()
os.system("tools/img4tool -c iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBSS.vresearch101.RELEASE.im4p -t ibss iBSS.vresearch101.RELEASE")

# Patch iBEC
if not os.path.exists("iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p.bak"):
    os.system("cp iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p.bak")
os.system("tools/img4 -i iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p.bak -o iBEC.vresearch101.RELEASE")
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
patch(0x24070, "serial=3 -v debug=0x2014e %s")
fp.close()
os.system("tools/img4tool -c iPhone17,3_26.1_23B85_Restore/Firmware/dfu/iBEC.vresearch101.RELEASE.im4p -t ibec iBEC.vresearch101.RELEASE")


# Patch DeviceTree
# if not os.path.exists("iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p.bak"):
#     os.system("cp iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p.bak")
# os.system("tools/img4 -i iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p.bak -o DeviceTree.vphone600ap")
# fp = open("DeviceTree.vphone600ap", "r+b")
# # patch device model to iPhone17,3?
# patch(0x32c, "iPhone17,3\x00") #effect no
# # patch(0x424, "iPhone17,3\x00") #effect yes
# patch(0xcd3c, "iPhone17,3\x00")
# patch(0xce88, "iPhone17,3\x00")
# fp.close()
# os.system("tools/img4tool -c iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/DeviceTree.vphone600ap.im4p -t dtre DeviceTree.vphone600ap")

# Patch LLB
if not os.path.exists("iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/LLB.vresearch101.RESEARCH_RELEASE.im4p.bak"):
    os.system("cp iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/LLB.vresearch101.RESEARCH_RELEASE.im4p iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/LLB.vresearch101.RESEARCH_RELEASE.im4p.bak")
os.system("tools/img4 -i iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/LLB.vresearch101.RESEARCH_RELEASE.im4p.bak -o LLB.vresearch101.RESEARCH_RELEASE")
fp = open("LLB.vresearch101.RESEARCH_RELEASE", "r+b")
# notice currently what loaded to serial log
patch(0x86809, "Loaded LLB")
patch(0x868B4, "Loaded LLB")
# patch image4_validate_property_callback
patch(0xA0D8, 0xd503201f)   #nop
patch(0xA0DC, 0xd2800000)   #mov x0, #0
# patch boot-args with "serial=3 -v debug=0x2014e %s"
patch(0x12888, 0xD0000082)  #adrp x2, #0x12000
patch(0x1288C, 0x91264042)  #add x2, x2, #0x990
patch(0x24990, "serial=3 -v debug=0x2014e %s")
# make possible load edited rootfs (needed to command snaputil -n later)
patch(0x2BFE8, 0x1400000b)
patch(0x2bca0, 0xd503201f)
patch(0x2C03C, 0x17ffff6a)
patch(0x2fcec, 0xd503201f)
patch(0x2FEE8, 0x14000009)
# some unknown patch, bypass panic
patch(0x1AEE4, 0xd503201f)  #nop
fp.close()
os.system("tools/img4tool -c iPhone17,3_26.1_23B85_Restore/Firmware/all_flash/LLB.vresearch101.RESEARCH_RELEASE.im4p -t illb LLB.vresearch101.RESEARCH_RELEASE")



# 6. Grab & Patch TXM
if not os.path.exists("iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p.bak"):
    os.system("cp iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p.bak")
os.system("pyimg4 im4p extract -i iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p.bak -o txm.raw")
# patch 
fp = open("txm.raw", "r+b")

# ========= TXM PATCH START =========
# Patch TXM for make running binary which is not registered in trustcache
# TXM [Error]: CodeSignature: selector: 24 | 0xA8 | 0x30 | 1
# Some trace: FFFFFFF01702B018->sub_FFFFFFF0170306E4->sub_FFFFFFF01703059C->sub_FFFFFFF01703037C->sub_FFFFFFF017030164->sub_FFFFFFF01702EC70 (base: 0xFFFFFFF017004000)
patch(0x2c1f8, 0xd2800000)      #FFFFFFF0170301F8
patch(0x2bef4, 0xd2800000)      #FFFFFFF01702FEF4
patch(0x2c060, 0xd2800000)      #FFFFFFF017030060

# ========= LEFT THINGS ARE FOR JAILBREAK =========
# TXM [Error]: CodeSignature: selector: 24 | 0xA1 | 0x30 | 1
patch(0x313ec, 0xd503201f)          #FFFFFFF0170353EC
patch(0x313f4, 0xd503201f)          #FFFFFFF0170353F4

# Always make true for get-task-allow / make possible lldb debugging
# TXM [Error]: selector: 41 | 29
patch(0x1f5d4, 0xd2800020)          #FFFFFFF0170235D4 #mov x0, #1
# TXM [Error]: selector: 42 | 29
# patch(0x2717c, 0x1400d8f8)          #FFFFFFF01702B17C; b #0x3623c ~55c
patch(0x2717c, 0x1400d88e)          #FFFFFFF01702B17C; b #0x36238 ~3b4

# 0x5d3b8 (FFFFFFF0170613B8) shellcode
patch(0x5d3b4, 0xd503201f)
patch(0x5d3b8, 0xd2800020)      #mov x0, #1
patch(0x5d3b8+4, 0x3900c280)    #strb w0, [x20, #0x30]
patch(0x5d3b8+8, 0xaa1403e0)      #mov x0, x20
patch(0x5d3b8+12, 0x17ff276f) #b #-0x36244

# always make true for com.apple.private.cs.debugger
# TXM [Error]: selector: 42 | 37
patch(0x1f3b8, 0x52800020)          #mov w0, #1

# always enable developer mode
patch(0x1FA58, 0xd503201f)      #FFFFFFF017023A58
# ========= TXM PATCH END =========

fp.close()
#create im4p
os.system("pyimg4 im4p create -i txm.raw -o txm.im4p -f trxm --lzfse")
# preserve payp structure
txm_im4p_data = Path('iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p.bak').read_bytes()
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
os.system("mv txm.im4p iPhone17,3_26.1_23B85_Restore/Firmware/txm.iphoneos.research.im4p")

# 7. Grab & patch kernelcache
if not os.path.exists("iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak"):
    os.system("cp iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600 iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak")
os.system("pyimg4 im4p extract -i iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600.bak -o kcache.raw")
# patch 
fp = open("kcache.raw", "r+b")

# ========= KERNEL PATCH START =========
# ========= Bypass SSV =========
# _apfs_vfsop_mount: Prevent panic "Failed to find the root snapshot. Rooting from the live fs ..."
patch(0x2476964, 0xd503201f)  #FFFFFE000947A964
# _authapfs_seal_is_broken: Prevent panic "root volume seal is broken ..."
patch(0x23cfde4, 0xd503201f) #FFFFFE00093D3DE4 
# _bsd_init: Prevent panic "rootvp not authenticated after mounting ..."
patch(0xf6d960, 0xd503201f)    #FFFFFE0007F71960

# ========= LEFT THINGS ARE FOR JAILBREAK =========
# __Z24AMFIIsCDHashInTrustCachehPKhPy
patch(0x1633880, 0xD2800020)        # MOV             X0, #1
patch(0x1633880+4, 0xB4000042)      # cbz x2, #8
patch(0x1633880+8, 0xF9000040)      # STR             X0, [X2]
patch(0x1633880+12, 0xD65F03C0)     # RET

# __Z30_proc_check_launch_constraintsP4prociiPvmP22launch_constraint_dataPPcPm
patch(0x163863C, 0x52800000)        # MOV             W0, #0
patch(0x163863C+4, 0xD65F03C0)      # RET

# __Z25_cred_label_update_execveP5ucredS0_P4procP5vnodexS4_P5labelS6_S6_PjPvmPi
# 0xAB1720 -> 0xFFFFFE0007AB5720 shellcode start
# shellcode end ~ 0xfffffe0007ab573f (0xab173f)
patch(0xAB1720, 0xF94007E0)         # LDR             X0, [SP,#8]
patch(0xAB1720+4, 0xB9400001)       # LDR             W1, [X0]
patch(0xAB1720+8, 0x32060021)       # ORR             W1, W1, #0x4000000
patch(0xAB1720+12, 0x32000C21)      # ORR             W1, W1, #0xF
patch(0xAB1720+16, 0x12126421)      # AND             W1, W1, #0xFFFFC0FF
patch(0xAB1720+20, 0xB9000001)      # STR             W1, [X0]
patch(0xAB1720+24, 0xAA1F03E0)      # MOV             X0, XZR
patch(0xAB1720+28, 0xD65F0FFF)      # RETAB
# shellcode end
patch(0x163c11c, 0x17D1D581)        # b #-0xb8a9fc (jump to shellcode)

# __ZL14postValidationP8LazyPathP7cs_blobjP12OSDictionaryhbjPKcPPcPm
patch(0x16405ac, 0x6B00001F)        # CMP             W0, W0

# __ZL27_check_dyld_policy_internalP4procyPy
patch(0x16410BC, 0x52800020)        # MOV             W0, #1
patch(0x16410C8, 0x52800020)        # MOV             W0, #1

# _apfs_graft
patch(0x242011C, 0x52800000)        # MOV             W0, #0

# _apfs_vfsop_mount
patch(0x2475044, 0xEB00001F)        # CMP             X0, X0

# _apfs_mount_upgrade_checks
patch(0x2476C00, 0x52800000)        # MOV             W0, #0

# _handle_fsioc_graft
patch(0x248C800, 0x52800000)        # MOV             W0, #0

# _syscallmask_apply_to_proc
# 0xAB1740 -> 0xFFFFFE0007AB5740 shellcode start
# shellcode end ~ 0xfffffe0007ab57d7 (0xab17d7)
patch(0xAB1740, 0xFFFFFFFF) 
patch(0xAB1740+4, 0xFFFFFFFF) 
patch(0xAB1740+8, 0xFFFFFFFF) 
patch(0xAB1740+12, 0xFFFFFFFF) 
patch(0xAB1740+16, 0xFFFFFFFF) 
patch(0xAB1740+20, 0xFFFFFFFF) 
patch(0xAB1740+24, 0xFFFFFFFF) 
patch(0xAB1740+28, 0xFFFFFFFF) 
patch(0xAB1740+32, 0xFFFFFFFF) 
patch(0xAB1740+36, 0xFFFFFFFF) 
patch(0xAB1740+4*10, 0xB4000362)    # cbz x2, #0x6c
patch(0xAB1740+4*11, 0xD10103FF)    # SUB             SP, SP, #0x40
patch(0xAB1740+4*12, 0xA90153F3)    # STP             X19, X20, [SP,#0x10]
patch(0xAB1740+4*13, 0xA9025BF5)    # STP             X21, X22, [SP,#0x20]
patch(0xAB1740+4*14, 0xA9037BFD)    # STP             X29, X30, [SP,#0x30]
patch(0xAB1740+4*15, 0xAA0003F3)    # MOV             X19, X0
patch(0xAB1740+4*16, 0xAA0103F4)    # MOV             X20, X1
patch(0xAB1740+4*17, 0xAA0203F5)    # MOV             X21, X2
patch(0xAB1740+4*18, 0xAA0303F6)    # MOV             X22, X3
patch(0xAB1740+4*19, 0xD2800108)    # MOV             X8, #8
patch(0xAB1740+4*20, 0xAA1103E0)    # MOV             X0, X17
patch(0xAB1740+4*21, 0xAA1503E1)    # MOV             X1, X21
patch(0xAB1740+4*22, 0xD2800002)    # MOV             X2, #0
patch(0xAB1740+4*23, 0x10FFFD23)    # adr x3, #0xffffffffffffffa4
patch(0xAB1740+4*24, 0x9AC80AC4)    # UDIV            X4, X22, X8
patch(0xAB1740+4*25, 0x9B08D88A)    # MSUB            X10, X4, X8, X22
patch(0xAB1740+4*26, 0xB400004A)    # cbz x10, #8
patch(0xAB1740+4*27, 0x91000484)    # ADD             X4, X4, #1
patch(0xAB1740+4*28, 0x940302AA)    # bl #0xc0aa8 (_zalloc_ro_mut)
patch(0xAB1740+4*29, 0xAA1303E0)    # MOV             X0, X19
patch(0xAB1740+4*30, 0xAA1403E1)    # MOV             X1, X20
patch(0xAB1740+4*31, 0xAA1503E2)    # MOV             X2, X21
patch(0xAB1740+4*32, 0xAA1603E3)    # MOV             X3, X22
patch(0xAB1740+4*33, 0xA94153F3)    # LDP             X19, X20, [SP,#0x10]
patch(0xAB1740+4*34, 0xA9425BF5)    # LDP             X21, X22, [SP,#0x20]
patch(0xAB1740+4*35, 0xA9437BFD)    # LDP             X29, X30, [SP,#0x30]
patch(0xAB1740+4*36, 0x910103FF)    # ADD             SP, SP, #0x40
patch(0xAB1740+4*37, 0x14144693)    # B               #0x511a4c (_proc_set_syscall_filter_mask)
# shellcode end
patch(0x2395530, 0xAA0003F1)        # MOV             X17, X0
patch(0x2395584, 0x179C7079)        # b #-0x18e3e1c (jump to shellcode)

# patch _hook_cred_label_update_execve
# ipad 7,11 18.7.1 FFFFFFF006F87928	0x4	08 9E A5 06 	B0 57 1D 07  (Line 16 of 181)
# 0xAB17D8 -> 0xFFFFFE0007AB57D8 shellcode start
# shellcode end ~ 0xfffffe0007ab588f (0xab188f)
patch(0xAB17D8, 0xd503201f)         # nop
patch(0xAB17D8+4*1,  0xB4000543)    # cbz x3, #0xa8
patch(0xAB17D8+4*2,  0xD11003FF)    # SUB             SP, SP, #0x400
patch(0xAB17D8+4*3,  0xA9007BFD)    # STP             X29, X30, [SP]
patch(0xAB17D8+4*4,  0xA90107E0)    # STP             X0, X1, [SP,#16]
patch(0xAB17D8+4*5,  0xA9020FE2)    # STP             X2, X3, [SP,#32]
patch(0xAB17D8+4*6,  0xA90317E4)    # STP             X4, X5, [SP,#48]
patch(0xAB17D8+4*7,  0xA9041FE6)    # STP             X6, X7, [SP,#64]
patch(0xAB17D8+4*8,  0xd503201f)    # nop
patch(0xAB17D8+4*9,  0x940851AC)    # BL _vfs_context_current; BL #0x2146b0
patch(0xAB17D8+4*10, 0xAA0003E2)    # MOV             X2, X0
patch(0xAB17D8+4*11, 0xF94017E0)    # LDR             X0, [SP,#0x400+var_3D8]
patch(0xAB17D8+4*12, 0x910203E1)    # ADD             X1, SP, #0x400+var_380
patch(0xAB17D8+4*13, 0x52807008)    # MOV             W8, #0x380
patch(0xAB17D8+4*14, 0xA900203F)    # STP             XZR, X8, [X1]
patch(0xAB17D8+4*15, 0xA9017C3F)    # STP             XZR, XZR, [X1,#0x10]
patch(0xAB17D8+4*16, 0xd503201f)    # nop
patch(0xAB17D8+4*17, 0x94085e69)    # BL _vnode_getattr_loc; BL #0x2179a4
patch(0xAB17D8+4*18, 0xB5000260)    # CBNZ            X0, loc_FFFFFFF0071D58B4
patch(0xAB17D8+4*19, 0x52800002)    # MOV             W2, #0
patch(0xAB17D8+4*20, 0xB940CFE8)    # LDR             W8, [SP,#0x400+var_334]
patch(0xAB17D8+4*21, 0x365800A8)    # TBZ             W8, #0xB, loc_FFFFFFF0071D5888
patch(0xAB17D8+4*22, 0xB940C7E8)    # LDR             W8, [SP,#0x400+var_33C]
patch(0xAB17D8+4*23, 0xF9400FE0)    # LDR             X0, [SP,#0x400+var_3E8]
patch(0xAB17D8+4*24, 0xB9001808)    # STR             W8, [X0,#0x18]
patch(0xAB17D8+4*25, 0x52800022)    # MOV             W2, #1
patch(0xAB17D8+4*26, 0xB940CFE8)    # LDR             W8, [SP,#0x400+var_334]
patch(0xAB17D8+4*27, 0x365000A8)    # TBZ             W8, #0xA, loc_FFFFFFF0071D58A0
patch(0xAB17D8+4*28, 0x52800022)    # MOV             W2, #1
patch(0xAB17D8+4*29, 0xB940CBE8)    # LDR             W8, [SP,#0x400+var_338]
patch(0xAB17D8+4*30, 0xF9400FE0)    # LDR             X0, [SP,#0x400+var_3E8]
patch(0xAB17D8+4*31, 0xB9002808)    # STR             W8, [X0,#0x28]
patch(0xAB17D8+4*32, 0x340000A2)    # CBZ             W2, loc_FFFFFFF0071D58B4
patch(0xAB17D8+4*33, 0xF94013E0)    # LDR             X0, [SP,#0x400+var_3E0]
patch(0xAB17D8+4*34, 0xB9445408)    # LDR             W8, [X0,#0x454]
patch(0xAB17D8+4*35, 0x32180108)    # ORR             W8, W8, #0x100
patch(0xAB17D8+4*36, 0xB9045408)    # STR             W8, [X0,#0x454]
patch(0xAB17D8+4*37, 0xA94107E0)    # LDP             X0, X1, [SP,#0x400+var_3F0]
patch(0xAB17D8+4*38, 0xA9420FE2)    # LDP             X2, X3, [SP,#0x400+var_3E0]
patch(0xAB17D8+4*39, 0xA94317E4)    # LDP             X4, X5, [SP,#0x400+var_3D0]
patch(0xAB17D8+4*40, 0xA9441FE6)    # LDP             X6, X7, [SP,#0x400+var_3C0]
patch(0xAB17D8+4*41, 0xA9407BFD)    # LDP             X29, X30, [SP,#0x400+var_400]
patch(0xAB17D8+4*42, 0x911003FF)    # ADD             SP, SP, #0x400
patch(0xAB17D8+4*43, 0xd503201f)    # nop
patch(0xAB17D8+4*44, 0x146420B7)    # B _hook_cred_label_update_execve; B #0x19082dc
patch(0xAB17D8+4*45, 0xd503201f)    # nop
# shellcode end
patch(0xa54518, 0xab17d8)   # 0xFFFFFE0007AB57D8(0xAB17D8) #0xa54518 -> 0xFFFFFE0007A58518


# patch _hook_file_check_mmap
patch(0xA545A8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_mount_check_mount
patch(0xA54740, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_mount_check_remount
patch(0xA54748, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_mount_check_umount
patch(0xA54760, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_rename
patch(0xA54848, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_getattr
patch(0xA54C30, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_proc_check_get_cs_info
patch(0xA54C50, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_proc_check_set_cs_info
patch(0xA54C58, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_proc_check_set_cs_info
patch(0xA54C68, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_chroot
patch(0xA54C78, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_create
patch(0xA54C78+8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_deleteextattr
patch(0xA54C78+8*2, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_exchangedata
patch(0xA54C78+8*3, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_exec
patch(0xA54C78+8*4, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_getattrlist
patch(0xA54C78+8*5, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_getextattr
patch(0xA54C78+8*6, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_ioctl
patch(0xA54C78+8*7, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_link
patch(0xA54CC8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_listextattr
patch(0xA54CD0, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_open ( XXX ALTERNATIVE patch instead of shellcode, 36/181)
patch(0xA54CE0, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_readlink
patch(0xA54CF8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setattrlist
patch(0xA54D20, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setextattr
patch(0xA54D20+8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setflags
patch(0xA54D20+8*2, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setmode
patch(0xA54D20+8*3, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setowner
patch(0xA54D20+8*4, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_setutimes
patch(0xA54D20+8*5, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_stat
patch(0xA54D20+8*6, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_truncate
patch(0xA54D20+8*7, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_unlink
patch(0xA54D20+8*8, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch _hook_vnode_check_fsgetpath
patch(0xA54E68, 0x23b73bc) # 0xFFFFFE00093BB3BC(0x23b73bc): mov x0, #0, ret

# patch string to /scores/ploosh instead of /sbin/launchd ( XXX NOT IMPLEMENTED ; 48/181)
# FFFFFFF00707C7FF	0xe	62 69 6E 2F 6C 61 75 6E 63 68 64 00 65 78 	63 6F 72 65 73 2F 70 6C 6F 6F 73 68 00 65 

# 49 ~ 158 / 181 ( XXX SKIP shellcode patch )

# patch _task_conversion_eval_internal
patch(0xb01194, 0xEB1F03FF)        # cmp xzr, xzr

# patch _proc_security_policy
patch(0x1063148, 0xd2800000)       # mov x0, #0
patch(0x1063148+4, 0xD65F03C0)     # RET

# patch _proc_pidinfo (pid 0 patch)
patch(0x1060a90, 0xd503201f)       # nop
patch(0x1060a98, 0xd503201f)       # nop
# patch(0x10612c0, 0xd503201f)       # nop

# patch _convert_port_to_map_with_flavor (prevent panic 'userspace has control access to a kernel map %p through task %p ... ')
patch(0xb02e94, 0x14000015)         # b #0x54

# patch _vm_fault_enter_prepare
patch(0xBA9E1C, 0xd503201f)         # nop

# patch _vm_map_protect ( XXX SKIP PATCH FFFFFFF0072DF198	0x4	28 FC 4F 36 	E1 FF FF FF  ; 164/181 ; )
patch(0xBC024C, 0x1400000A)         # b #0x28

# patch ___mac_mount
patch(0xCA5D54, 0xd503201f)         # nop
patch(0xCA5D88, 0xAA1F03E8)         # MOV             X8, XZR

# patch _dounmount
patch(0xCA8134, 0xd503201f)         # nop

# patch _bsd_init (prevent panic "rootvp not authenticated after mounting @%s:%d")
patch(0xF6D95C, 0xd2800000)         # mov x0, #0

# patch _spawn_validate_persona
patch(0xfa7024, 0xd503201f)         # nop
patch(0xfa702c, 0xd503201f)         # nop

# XXX SKIP PATCH _load_init_program (FFFFFFF0076902E0	0x3	F2 FD FF 	C2 15 ED ; 171/181)

# patch _task_for_pid
patch(0xfc383c, 0xd503201f)         # nop

# XXX SKIP PATCH _disable_developer_mode (FFFFFFF0076DA818	0x4	28 D4 FF D0 	93 7A 8E 17  ; 173/181)

# XXX _load_dylinker SKIPPED SOME PART OF PATCH (FFFFFFF007728B0C	0xc	E1 CA FF B0 21 14 2A 91 E0 03 14 AA 	44 B4 EA 97 F4 03 00 AA 12 00 00 14  ; 174/181)
patch(0x1052a28, 0x14000011)         # b #0x44

# patch _shared_region_map_and_slide_setup
patch(0x10729cc, 0xeb00001f)         # cmp x0, x0

# patch __ZL16verifyPermission16IONVRAMOperationPKhPKcb
patch(0x1234034, 0xd503201f)         # nop

# XXX SKIP PATCH _IOFindBSDRoot (FFFFFFF0078DF84C	0x2	E1 BD 	A1 C7 ; 177 / 181) (some patch to spartan instead of _PE_parse_boot_argn_internal)

# patch _IOSecureBSDRoot
patch(0x128b598, 0x14000009)        # b #0x24

# kcall10 via syscall (replace SYS_kas_info 439)
# sy_call_t       *sy_call;       /* implementing function */ ---------> 0xFFFFFE0007AB5890
patch(0x73e180, 0xAB1890)
# sy_munge_t      *sy_arg_munge32; /* system call arguments munger for 32-bit process */ ---------> _munge_wwwwwwww
patch(0x73e188, 0xc66d28)
# int32_t         sy_return_type; /* system call return types */ ---------> _SYSCALL_RET_UINT64_T
patch(0x73e190, 0x7)
#int16_t         sy_narg;        /* number of args */ --------> 0x8
#uint16_t        sy_arg_bytes;   /* Total size of arguments in bytes for 32-bit system calls */ ---------> 0x20 (=32, 4*8=32)
patch(0x73e194, 0x200008)
# 0xAB1890 -> 0xFFFFFE0007AB5890 shellcode start
# shellcode end ~ 0xfffffe0007ab590f (0xab190f)
patch(0xAB1890+4*0, 0xF94023EA)     # ldr x10, [sp, #0x40]
patch(0xAB1890+4*1, 0xA9400540)     # ldp x0, x1, [x10, #0]
patch(0xAB1890+4*2, 0xA9410D42)     # ldp x2, x3, [x10, #0x10]
patch(0xAB1890+4*3, 0xA9421544)     # ldp x4, x5, [x10, #0x20]
patch(0xAB1890+4*4, 0xA9431D46)     # ldp x6, x7, [x10, #0x30]
patch(0xAB1890+4*5, 0xA9442548)     # ldp x8, x9, [x10, #0x40]
patch(0xAB1890+4*6, 0xF940294A)     # ldr x10, [x10, #0x50]
patch(0xAB1890+4*7, 0xAA0003F0)     # mov x16, x0
patch(0xAB1890+4*8, 0xAA0103E0)     # mov x0, x1
patch(0xAB1890+4*9, 0xAA0203E1)     # mov x1, x2
patch(0xAB1890+4*10, 0xAA0303E2)     # mov x2, x3
patch(0xAB1890+4*11, 0xAA0403E3)     # mov x3, x4
patch(0xAB1890+4*12, 0xAA0503E4)     # mov x4, x5
patch(0xAB1890+4*13, 0xAA0603E5)     # mov x5, x6
patch(0xAB1890+4*14, 0xAA0703E6)     # mov x6, x7
patch(0xAB1890+4*15, 0xAA0803E7)     # mov x7, x8
patch(0xAB1890+4*16, 0xAA0903E8)     # mov x8, x9
patch(0xAB1890+4*17, 0xAA0A03E9)     # mov x9, x10
patch(0xAB1890+4*18, 0xA9BF7BFD)     # stp x29, x30, [sp, #-0x10]!
patch(0xAB1890+4*19, 0xD63F0200)     # blr x16 #<- problem!!!
patch(0xAB1890+4*20, 0xA8C17BFD)     # ldp x29, x30, [sp], #0x10
patch(0xAB1890+4*21, 0xF94023EB)     # ldr x11, [sp, #0x40]
patch(0xAB1890+4*22, 0xd503201f)     # nop
patch(0xAB1890+4*23, 0xA9000560)     # stp x0, x1, [x11, #0]
patch(0xAB1890+4*24, 0xA9010D62)     # stp x2, x3, [x11, #0x10]
patch(0xAB1890+4*25, 0xA9021564)     # stp x4, x5, [x11, #0x20]
patch(0xAB1890+4*26, 0xA9031D66)     # stp x6, x7, [x11, #0x30]
patch(0xAB1890+4*27, 0xA9042568)     # stp x8, x9, [x11, #0x40]
patch(0xAB1890+4*28, 0xF900296A)     # str x10, [x11, #0x50]
patch(0xAB1890+4*29, 0xd2800000)     # mov x0, #0
patch(0xAB1890+4*30, 0xd65f03c0)     # ret
patch(0xAB1890+4*31, 0xd503201f)     # nop

# patch _thid_should_crash to 0
# https://x.com/patch1t/status/1775695503071855082?s=46
'''
Exception Type:    EXC_GUARD
Exception Subtype: GUARD_TYPE_MACH_PORT
Exception Message:  SET_EXCEPTION_BEHAVIOR on mach port 2147483651 (guarded with 0x00000000000009ce)
Exception Codes:   0x0000000009c00003, 0x00000000000009ce

Termination Reason:  Namespace GUARD, Code 2305843037130981379, 


Thread 0 name:   Dispatch queue: com.apple.main-thread
Thread 0 Crashed:
0   libsystem_kernel.dylib        	       0x22ded9cd4 mach_msg2_trap + 8
1   libsystem_kernel.dylib        	       0x22dedd2f8 mach_msg2_internal + 76
2   libsystem_kernel.dylib        	       0x22dee9504 task_set_exception_ports + 144
'''
patch(0x67EB50, 0x0)
# ========= KERNEL PATCH END =========

fp.close()

#create im4p
os.system("pyimg4 im4p create -i kcache.raw -o krnl.im4p -f krnl --lzfse")

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

os.system("mv krnl.im4p iPhone17,3_26.1_23B85_Restore/kernelcache.research.vphone600")


# Clean
os.system("rm kcache.raw")
os.system("rm txm.raw")
os.system("rm iBSS.vresearch101.RELEASE")
os.system("rm iBEC.vresearch101.RELEASE")
os.system("rm LLB.vresearch101.RESEARCH_RELEASE")