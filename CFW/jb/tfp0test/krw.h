#include <stdint.h>
#include <mach/mach.h>
#include <CoreFoundation/CoreFoundation.h>

#define PROC_PIDREGIONINFO (7)
#define VM_KERN_MEMORY_OSKEXT (5)

/*
(lldb) type lookup OSKextLoadedKextSummary
struct _loaded_kext_summary {
    char name[64];
    uuid_t uuid;
    uint64_t address;
    uint64_t size;
    uint64_t version;
    uint32_t loadTag;
    uint32_t flags;
    uint64_t reference_list;
    uint64_t text_exec_address;
    size_t text_exec_size;
}
(lldb) p/x offsetof(OSKextLoadedKextSummary, name)
(unsigned long) 0x0000000000000000
(lldb) p/x offsetof(OSKextLoadedKextSummary, address)
(unsigned long) 0x0000000000000050
(lldb) p/x sizeof(OSKextLoadedKextSummary)
(unsigned long) 0x0000000000000088
*/
#define LOADED_KEXT_SUMMARY_HDR_NAME_OFF (0x10)
#define LOADED_KEXT_SUMMARY_HDR_ADDR_OFF (0x60)
#define LOADED_KEXT_SUMMARY_HDR_STRUCTURE_SIZE (0x88)
#define kOSBundleLoadAddressKey "OSBundleLoadAddress"

int
proc_pidinfo(int, int, uint64_t, void *, int);

CFDictionaryRef
OSKextCopyLoadedKextInfo(CFArrayRef, CFArrayRef);

kern_return_t
mach_vm_read_overwrite(vm_map_t, mach_vm_address_t, mach_vm_size_t, mach_vm_address_t, mach_vm_size_t *);

kern_return_t
mach_vm_write(vm_map_t, mach_vm_address_t, vm_offset_t, mach_msg_type_number_t);

kern_return_t
mach_vm_machine_attribute(vm_map_t, mach_vm_address_t, mach_vm_size_t, vm_machine_attribute_t, vm_machine_attribute_val_t *);

kern_return_t mach_vm_allocate(task_t task, mach_vm_address_t *addr, mach_vm_size_t size, int flags);

kern_return_t mach_vm_deallocate(task_t task, mach_vm_address_t addr, mach_vm_size_t size);

uint64_t get_sptmbase_via_kext(void);
uint64_t get_txmbase_via_kext(void);

int get_kbase(uint64_t *addr);
uint64_t kbase;
uint64_t kslide;

kern_return_t
kreadbuf(uint64_t kaddr, void *buf, size_t sz);

kern_return_t
kwritebuf(uint64_t kaddr, const void *buf, size_t sz);

uint16_t kread16(uint64_t where);

uint32_t kread32(uint64_t where);

uint64_t kread64(uint64_t where);

void kwrite16(uint64_t where, uint16_t what);

void kwrite32(uint64_t where, uint32_t what);

void kwrite64(uint64_t where, uint64_t what);

uint64_t kalloc(size_t sz);

void kfree(uint64_t kaddr, size_t sz);

uint64_t kcall10(uint64_t addr, uint64_t a1, uint64_t a2, uint64_t a3, uint64_t a4, uint64_t a5, uint64_t a6, uint64_t a7, uint64_t a8, uint64_t a9, uint64_t a10);

void kmemcpy(uint64_t dest, uint64_t src, uint32_t length);

void khexdump(uint64_t addr, size_t size);

uint64_t get_kbase_via_kext(void);

void khexdump2(uint64_t addr, size_t size);