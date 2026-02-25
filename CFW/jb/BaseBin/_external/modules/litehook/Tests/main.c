#include "litehook.h"

#include <sys/socket.h>
#include <mach-o/dyld.h>
#include <dyld_cache_format.h>

int bind_hook(int a1, const struct sockaddr *a2, socklen_t a3)
{
	return 0;
}

int main(int argc, const char *argv[])
{
	uint32_t executablePathSize = 0;
	_NSGetExecutablePath(NULL, &executablePathSize);
	char executablePath[executablePathSize];
	_NSGetExecutablePath(executablePath, &executablePathSize);
	
	const struct mach_header *mainBinHeader = NULL;
	for (uint32_t i = 0; i < _dyld_image_count(); i++) {
		const char *name = _dyld_get_image_name(i);
		if (!strcmp(name, executablePath)) {
			mainBinHeader = _dyld_get_image_header(i);
		}
	}

	printf("About to test rebind...\n");

	litehook_rebind_symbol((mach_header*)mainBinHeader, bind, bind_hook, NULL);

	//getchar();

	if (bind(0, NULL, 0) != 0) {
		printf("Failed rebind\n");
		return -1;
	}
	else {
		printf("Rebind success!!!\n");
	}

	return 0;
}