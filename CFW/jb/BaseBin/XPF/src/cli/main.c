#include <time.h>
#include <sys/mman.h>
#include "../xpf.h"

int main(int argc, char *argv[]) {
	if (argc == 1) {

	}
	else {
		if (xpf_start_with_kernel_path(argv[1]) == 0) {
			printf("Starting XPF with %s (%s)\n", argv[1], gXPF.kernelVersionString);
			clock_t t = clock();

			printf("Kernel base: 0x%llx\n", gXPF.kernelBase);
			printf("Kernel entry: 0x%llx\n", gXPF.kernelEntry);
			//xpf_print_all_items();

			char *sets[] = {
				"translation",
				"trustcache",
				"physmap",
				"struct",
				"physrw",
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
				NULL,
			};

			uint32_t idx = 0;
			while (sets[idx] != NULL) idx++;

			if (xpf_set_is_supported("sandbox")) {
				sets[idx++] = "sandbox";
			}
			if (xpf_set_is_supported("perfkrw")) {
				sets[idx++] = "perfkrw";
			}
			if (xpf_set_is_supported("devmode")) {
				sets[idx++] = "devmode"; 
			}
			if (xpf_set_is_supported("badRecovery")) {
				sets[idx++] = "badRecovery"; 
			}
			if (xpf_set_is_supported("arm64kcall")) {
				sets[idx++] = "arm64kcall"; 
			}
			if (xpf_set_is_supported("trigon")) {
				sets[idx++] = "trigon"; 
			}

			xpc_object_t serializedSystemInfo = xpf_construct_offset_dictionary((const char **)sets);
			if (serializedSystemInfo) {
				xpc_dictionary_apply(serializedSystemInfo, ^bool(const char *key, xpc_object_t value) {
					if (xpc_get_type(value) == XPC_TYPE_UINT64) {
						printf("0x%016llx <- %s\n", xpc_uint64_get_value(value), key);
					}
					return true;
				});
				xpc_release(serializedSystemInfo);
			}
			else {
				printf("XPF Error: %s\n", xpf_get_error());
			}

			t = clock() - t;
			double time_taken = ((double)t)/CLOCKS_PER_SEC;
			printf("XPF finished in %lf seconds\n", time_taken);
			xpf_stop();
		}
		else {
			printf("Failed to start XPF: %s\n", xpf_get_error());
		}
	}
	return 0;
}