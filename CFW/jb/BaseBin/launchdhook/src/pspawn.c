#include <spawn.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <mach-o/dyld.h>
#include <dlfcn.h>
#include <sys/utsname.h>
#include <substrate.h>
#include <sys/mount.h>
#include <sys/stat.h>
#include <sys/sysctl.h>
#include "crashreporter.h"
#include "pspawn.h"

extern void load_bootstrapped_jailbreak_env(void);

extern void (*MSHookFunction_p)(void *symbol, void *replace, void **result);
extern int (*spawn_hook_common_p)(pid_t *restrict pid, const char *restrict path,
					   const posix_spawn_file_actions_t *restrict file_actions,
					   const posix_spawnattr_t *restrict attrp,
					   char *const argv[restrict],
					   char *const envp[restrict],
					   void *pspawn_org);

static void *posix_spawn_orig;

static int posix_spawn_orig_wrapper(pid_t *restrict pid, const char *restrict path,
					   const posix_spawn_file_actions_t *restrict file_actions,
					   const posix_spawnattr_t *restrict attrp,
					   char *const argv[restrict],
					   char *const envp[restrict])
{
	int (*orig)(pid_t *restrict, const char *restrict, const posix_spawn_file_actions_t *restrict, const posix_spawnattr_t *restrict, char *const[restrict], char *const[restrict]) = posix_spawn_orig;

	// we need to disable the crash reporter during the orig call
	// otherwise the child process inherits the exception ports
	// and this would trip jailbreak detections
	// crashreporter_pause();	
	int r = orig(pid, path, file_actions, attrp, argv, envp);
	// crashreporter_resume();

	return r;
}

static int posix_spawn_hook(pid_t *restrict pid, const char *restrict path,
					   const posix_spawn_file_actions_t *restrict file_actions,
					   const posix_spawnattr_t *restrict attrp,
					   char *const argv[restrict],
					   char *const envp[restrict])
{
	if (path) {
		char executablePath[1024];
		uint32_t bufsize = sizeof(executablePath);
		_NSGetExecutablePath(&executablePath[0], &bufsize);
		if (!strcmp(path, executablePath)) {
			// This spawn will perform a userspace reboot...
			// Instead of the ordinary hook, we want to reinsert this dylib
			// This has already been done in envp so we only need to call the regular posix_spawn

			// Say goodbye to this process
			return posix_spawn_orig_wrapper(pid, path, file_actions, attrp, argv, envp);
		} 
		load_bootstrapped_jailbreak_env();
	}

	return spawn_hook_common_p(pid, path, file_actions, attrp, argv, envp, posix_spawn_orig_wrapper);
}

void initSpawnHooks(void)
{
	MSHookFunction_p(&posix_spawn, (void *)posix_spawn_hook, (void**)&posix_spawn_orig);
}
