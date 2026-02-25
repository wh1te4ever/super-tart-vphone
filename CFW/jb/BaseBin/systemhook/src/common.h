#include <stdbool.h>
#include <unistd.h>
#include <spawn.h>
#include <signal.h>

#define HOOK_DYLIB_PATH "/cores/systemhook.dylib"
#define JB_ENV_COUNT 4 //systemHookAlreadyInserted, JB_SANDBOX_EXTENSIONS, JB_ROOT_PATH, JB_TWEAKLOADER_PATH
extern char *JB_SandboxExtensions;
extern char *JB_RootPath;
extern char *JB_TweakLoaderPath;

#define JB_ROOT_PATH(path) ({ \
	char *outPath = alloca(PATH_MAX); \
	strlcpy(outPath, JB_RootPath, PATH_MAX); \
	strlcat(outPath, path, PATH_MAX); \
	(outPath); \
})

#define SHOOK_EXPORT __attribute__((visibility ("default")))

bool stringStartsWith(const char *str, const char* prefix);
bool stringEndsWith(const char* str, const char* suffix);

int resolvePath(const char *file, const char *searchPath, int (^attemptHandler)(char *path));
SHOOK_EXPORT int spawn_hook_common(pid_t *restrict pid, const char *restrict path,
					   const posix_spawn_file_actions_t *restrict file_actions,
					   const posix_spawnattr_t *restrict attrp,
					   char *const argv[restrict],
					   char *const envp[restrict],
					   void *pspawn_org);

typedef struct {
    uint32_t platform;
    uint32_t version;
} DyldBuildVersion;


#define CONSTRUCT_V(major, minor, subminor) ((major & 0xffff) << 16) | ((minor & 0xff) << 8) | (subminor & 0xff)
