#!/bin/zsh
irecovery -f Ramdisk/iBSS.vresearch101.RELEASE.img4
irecovery -f Ramdisk/iBEC.vresearch101.RELEASE.img4
irecovery -c go

sleep 1;
irecovery -f Ramdisk/sptm.vresearch1.release.img4
irecovery -c firmware

irecovery -f Ramdisk/txm.img4
irecovery -c firmware

irecovery -f Ramdisk/trustcache.img4
irecovery -c firmware
irecovery -f Ramdisk/ramdisk.img4
irecovery -c ramdisk
irecovery -f Ramdisk/DeviceTree.vphone600ap.img4
irecovery -c devicetree
irecovery -f Ramdisk/sep-firmware.vresearch101.RELEASE.img4
irecovery -c firmware
irecovery -f Ramdisk/krnl.img4
irecovery -c bootx
