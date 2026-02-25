#include "krw.h"
#include <stdint.h>
#include <mach/mach.h> 
#include <errno.h>
#include <stdlib.h>
#include <stdio.h>
#include <dlfcn.h>

extern task_t tfp0;
extern void* libkernrw;
uint64_t kbase = 0;
uint64_t kslide = 0;

#ifndef MIN
#    define MIN(a, b) ((a) < (b) ? (a) : (b))
#endif

uint64_t get_sptmbase_via_kext(void) {
    struct {
		uint32_t pri_prot, pri_max_prot, pri_inheritance, pri_flags;
		uint64_t pri_offset;
		uint32_t pri_behavior, pri_user_wired_cnt, pri_user_tag, pri_pages_resident, pri_pages_shared_now_private, pri_pages_swapped_out, pri_pages_dirtied, pri_ref_cnt, pri_shadow_depth, pri_share_mode, pri_private_pages_resident, pri_shared_pages_resident, pri_obj_id, pri_depth;
		uint64_t pri_addr;
		uint64_t pri_sz;
	} pri;

    char kext_name[KMOD_MAX_NAME];
    CFStringRef kext_name_cf;
    CFNumberRef kext_addr_cf;
    CFArrayRef kext_names;
    CFDictionaryRef kexts_info;
    CFDictionaryRef kext_info;
    uint64_t kext_addr;

    for(pri.pri_addr = 0; proc_pidinfo(0, PROC_PIDREGIONINFO, pri.pri_addr, &pri, sizeof(pri)) == sizeof(pri); pri.pri_addr += pri.pri_sz) {
        if(pri.pri_prot == VM_PROT_READ && pri.pri_user_tag == VM_KERN_MEMORY_OSKEXT) {
            break;
        }
    }

    if(kreadbuf(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_NAME_OFF, kext_name, sizeof(kext_name)) != KERN_SUCCESS) return 0;

    if(strcmp(kext_name, "com.apple.sptm") != 0) {
        printf("couldn't find com.apple.sptm\n");
        return 0;
    }
    printf("kext_name: %s\n", kext_name);

    uint64_t kext_addr_slid = kread64(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_ADDR_OFF);
    printf("kext_addr_slid: 0x%llx\n", kext_addr_slid);

    return kext_addr_slid;
}

uint64_t get_txmbase_via_kext(void) {
    struct {
		uint32_t pri_prot, pri_max_prot, pri_inheritance, pri_flags;
		uint64_t pri_offset;
		uint32_t pri_behavior, pri_user_wired_cnt, pri_user_tag, pri_pages_resident, pri_pages_shared_now_private, pri_pages_swapped_out, pri_pages_dirtied, pri_ref_cnt, pri_shadow_depth, pri_share_mode, pri_private_pages_resident, pri_shared_pages_resident, pri_obj_id, pri_depth;
		uint64_t pri_addr;
		uint64_t pri_sz;
	} pri;

    char kext_name[KMOD_MAX_NAME];
    CFStringRef kext_name_cf;
    CFNumberRef kext_addr_cf;
    CFArrayRef kext_names;
    CFDictionaryRef kexts_info;
    CFDictionaryRef kext_info;
    uint64_t kext_addr;

    for(pri.pri_addr = 0; proc_pidinfo(0, PROC_PIDREGIONINFO, pri.pri_addr, &pri, sizeof(pri)) == sizeof(pri); pri.pri_addr += pri.pri_sz) {
        if(pri.pri_prot == VM_PROT_READ && pri.pri_user_tag == VM_KERN_MEMORY_OSKEXT) {
            break;
        }
    }

    if(kreadbuf(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_NAME_OFF + LOADED_KEXT_SUMMARY_HDR_STRUCTURE_SIZE, kext_name, sizeof(kext_name)) != KERN_SUCCESS) return 0;
    if(strcmp(kext_name, "com.apple.txm") != 0) {
        printf("couldn't find com.apple.txm\n");
        return 0;
    }
    printf("kext_name: %s\n", kext_name);

    uint64_t kext_addr_slid = kread64(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_ADDR_OFF + LOADED_KEXT_SUMMARY_HDR_STRUCTURE_SIZE);
    printf("kext_addr_slid: 0x%llx\n", kext_addr_slid);

    return kext_addr_slid;
}

uint64_t get_kbase_via_kext(void) {
    struct {
		uint32_t pri_prot, pri_max_prot, pri_inheritance, pri_flags;
		uint64_t pri_offset;
		uint32_t pri_behavior, pri_user_wired_cnt, pri_user_tag, pri_pages_resident, pri_pages_shared_now_private, pri_pages_swapped_out, pri_pages_dirtied, pri_ref_cnt, pri_shadow_depth, pri_share_mode, pri_private_pages_resident, pri_shared_pages_resident, pri_obj_id, pri_depth;
		uint64_t pri_addr;
		uint64_t pri_sz;
	} pri;

    char kext_name[KMOD_MAX_NAME];
    CFStringRef kext_name_cf;
    CFNumberRef kext_addr_cf;
    CFArrayRef kext_names;
    CFDictionaryRef kexts_info;
    CFDictionaryRef kext_info;
    uint64_t kext_addr;

    for(pri.pri_addr = 0; proc_pidinfo(0, PROC_PIDREGIONINFO, pri.pri_addr, &pri, sizeof(pri)) == sizeof(pri); pri.pri_addr += pri.pri_sz) {
        if(pri.pri_prot == VM_PROT_READ && pri.pri_user_tag == VM_KERN_MEMORY_OSKEXT) {
            break;
        }
    }

    if(kreadbuf(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_NAME_OFF + LOADED_KEXT_SUMMARY_HDR_STRUCTURE_SIZE*2, kext_name, sizeof(kext_name)) != KERN_SUCCESS) return 0;

    if(strcmp(kext_name, "com.apple.kec.corecrypto") != 0) {
        printf("couldn't find com.apple.kec.corecrypto\n");
        return 0;
    }
    printf("kext_name: %s\n", kext_name);

    uint64_t kext_addr_slid = kread64(pri.pri_addr + LOADED_KEXT_SUMMARY_HDR_ADDR_OFF + LOADED_KEXT_SUMMARY_HDR_STRUCTURE_SIZE*2);
    printf("kext_addr_slid: 0x%llx\n", kext_addr_slid);

    if((kext_name_cf = CFStringCreateWithCStringNoCopy(kCFAllocatorDefault, kext_name, kCFStringEncodingUTF8, kCFAllocatorNull)) == NULL) return 0;

    if((kext_names = CFArrayCreate(kCFAllocatorDefault, (const void **)&kext_name_cf, 1, &kCFTypeArrayCallBacks)) == NULL) return 0;

    if((kexts_info = OSKextCopyLoadedKextInfo(kext_names, NULL)) == NULL) return 0;

    if(CFGetTypeID(kexts_info) != CFDictionaryGetTypeID())  return 0;

    if(CFDictionaryGetCount(kexts_info) != 1)   return 0;

    if((kext_info = CFDictionaryGetValue(kexts_info, kext_name_cf)) == NULL)   return 0;

    if(CFGetTypeID(kext_info) != CFDictionaryGetTypeID())   return 0;

    if((kext_addr_cf = CFDictionaryGetValue(kext_info, CFSTR(kOSBundleLoadAddressKey))) == NULL)  return 0;

    if(CFGetTypeID(kext_addr_cf) != CFNumberGetTypeID())    return 0;

    if(!(CFNumberGetValue(kext_addr_cf, kCFNumberSInt64Type, &kext_addr)))  return 0;

    if(!(kext_addr_slid > kext_addr))   return 0;

    uint64_t kbase = 0xFFFFFE0007004000 + (kext_addr_slid - kext_addr);

    return kbase;
}

int get_kbase(uint64_t *addr)
{
    uint64_t kbase = get_kbase_via_kext();
    if(kbase != 0) {
        *addr = kbase;
        kslide = kbase - 0xFFFFFE0007004000;
    }
    return 0;
}

kern_return_t
kreadbuf(uint64_t kaddr, void *buf, size_t sz) {
    mach_vm_address_t p = (mach_vm_address_t)buf;
    mach_vm_size_t read_sz, out_sz = 0;

    while(sz != 0) {
        read_sz = MIN(sz, vm_kernel_page_size - (kaddr & vm_kernel_page_mask));
        if(mach_vm_read_overwrite(tfp0, kaddr, read_sz, p, &out_sz) != KERN_SUCCESS || out_sz != read_sz) {
            return KERN_FAILURE;
        }
        p += read_sz;
        sz -= read_sz;
        kaddr += read_sz;
    }
    return KERN_SUCCESS;
}

kern_return_t
kwritebuf(uint64_t kaddr, const void *buf, size_t sz) {
    vm_machine_attribute_val_t mattr_val = MATTR_VAL_CACHE_FLUSH;
    mach_vm_address_t p = (mach_vm_address_t)buf;
    mach_msg_type_number_t write_sz;

    while(sz != 0) {
        write_sz = (mach_msg_type_number_t)MIN(sz, vm_kernel_page_size - (kaddr & vm_kernel_page_mask));
        if(mach_vm_write(tfp0, kaddr, p, write_sz) != KERN_SUCCESS || mach_vm_machine_attribute(tfp0, kaddr, write_sz, MATTR_CACHE, &mattr_val) != KERN_SUCCESS) {
            return KERN_FAILURE;
        }
        p += write_sz;
        sz -= write_sz;
        kaddr += write_sz;
    }
    return KERN_SUCCESS;
}

uint16_t kread16(uint64_t where) {
    uint16_t out;
    kreadbuf(where, &out, sizeof(uint16_t));
    return out;
}

uint32_t kread32(uint64_t where) {
    uint32_t out;
    kreadbuf(where, &out, sizeof(uint32_t));
    return out;
}

uint64_t kread64(uint64_t where) {
    uint64_t out;
    kreadbuf(where, &out, sizeof(uint64_t));
    return out;
}

void kwrite16(uint64_t where, uint16_t what) {
    uint16_t _what = what;
    kwritebuf(where, &_what, sizeof(uint16_t));
}

void kwrite32(uint64_t where, uint32_t what) {
    uint32_t _what = what;
    kwritebuf(where, &_what, sizeof(uint32_t));
}

void kwrite64(uint64_t where, uint64_t what) {
    uint64_t _what = what;
    kwritebuf(where, &_what, sizeof(uint64_t));
}

uint64_t kalloc(size_t sz) {
    mach_vm_address_t va = 0;
    kern_return_t ret = mach_vm_allocate(tfp0, &va, sz, VM_FLAGS_ANYWHERE);
    if(ret == KERN_SUCCESS) {
        return va;
    }
    return -1;
}

void kfree(uint64_t kaddr, size_t sz) {
    kern_return_t ret = mach_vm_deallocate(tfp0, kaddr, sz);
    if(ret == KERN_SUCCESS)
    {
        return;
    }
    printf("kfree failed\n");
    exit(1);
}

#define	SYS_kas_info       439
uint64_t kcall10(uint64_t addr, uint64_t a1, uint64_t a2, uint64_t a3, uint64_t a4, uint64_t a5, uint64_t a6, uint64_t a7, uint64_t a8, uint64_t a9, uint64_t a10) {

	uint64_t arg_max_cnt = 10;
	uint64_t kdata = kalloc(8*arg_max_cnt);
	kwrite64(kdata, addr);
	kwrite64(kdata+8, a1);
	kwrite64(kdata+8*2, a2);
	kwrite64(kdata+8*3, a3);
	kwrite64(kdata+8*4, a4);
	kwrite64(kdata+8*5, a5);
	kwrite64(kdata+8*6, a6);
	kwrite64(kdata+8*7, a7);
	kwrite64(kdata+8*8, a8);
	kwrite64(kdata+8*9, a9);
	kwrite64(kdata+8*10, a10);

    syscall(SYS_kas_info, kdata);

	uint64_t kret = kread64(kdata);
	a1 = kread64(kdata+8);
	a2 = kread64(kdata+8*2);
	a3 = kread64(kdata+8*3);
	a4 = kread64(kdata+8*4);
	a5 = kread64(kdata+8*5);
	a6 = kread64(kdata+8*6);
	a7 = kread64(kdata+8*7);
	a8 = kread64(kdata+8*8);
	a9 = kread64(kdata+8*9);
	a10 = kread64(kdata+8*10);

	kfree(kdata, 8*arg_max_cnt);
    return kret;
}

const uint64_t kernel_address_space_base = 0xffff000000000000;
void kmemcpy(uint64_t dest, uint64_t src, uint32_t length) {
    if (dest >= kernel_address_space_base) {
      // copy to kernel:
      kwritebuf(dest, (void*) src, length);
    } else {
      // copy from kernel
      kreadbuf(src, (void*)dest, length);
    }
}

void khexdump2(uint64_t addr, size_t size) {
    void *data = malloc(size);
    kreadbuf(addr, data, size);
    char ascii[17];
    size_t i, j;
    ascii[16] = '\0';
    for (i = 0; i < size; ++i) {
        if ((i % 16) == 0)
        {
            printf("[0x%016llx+0x%03zx] ", addr, i);
//            printf("[0x%016llx] ", i + addr);
        }
        
        printf("%02X ", ((unsigned char*)data)[i]);
        if (((unsigned char*)data)[i] >= ' ' && ((unsigned char*)data)[i] <= '~') {
            ascii[i % 16] = ((unsigned char*)data)[i];
        } else {
            ascii[i % 16] = '.';
        }
        if ((i+1) % 8 == 0 || i+1 == size) {
            printf(" ");
            if ((i+1) % 16 == 0) {
                printf("|  %s \n", ascii);
            } else if (i+1 == size) {
                ascii[(i+1) % 16] = '\0';
                if ((i+1) % 16 <= 8) {
                    printf(" ");
                }
                for (j = (i+1) % 16; j < 16; ++j) {
                    printf("   ");
                }
                printf("|  %s \n", ascii);
            }
        }
    }
    free(data);
}