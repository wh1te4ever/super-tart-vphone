#include <removefile.h>
#include <sys/mount.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <string.h>
#include <dirent.h>
#include <stdbool.h>
#include <sys/utsname.h>
#include <sys/stat.h>

#include "bmhash.h"
#include "prebootpath.h"

int jailbreak_get_prebootPath(char jbPath[150]) {
    struct utsname name;
    int ret = uname(&name);
    if (ret) return errno;
    if (atoi(name.release) < 20) return ENOTSUP;
    char bmhash[97];
    jailbreak_get_bmhash(bmhash);
    snprintf(jbPath, 150, "/private/preboot/%s", bmhash);
    DIR* dir = opendir(jbPath);
    if (!dir) {
        return ENOENT;
    }
    char jbPathName[20];
    bool has_prebootjb = false;
    struct dirent* d;
    while ((d = readdir(dir)) != NULL) {
        if (strncmp(d->d_name, "jb-", 3)) continue;
        if (has_prebootjb == true) {
            closedir(dir);
            return EEXIST;
        }
        snprintf(jbPathName, 20, "%s" ,d->d_name);
        has_prebootjb = true;
    }
    closedir(dir);
    if (!has_prebootjb) return ENOENT;
    snprintf(jbPath, 150, "/private/preboot/%s/%s/procursus", bmhash, jbPathName);
    struct stat st;
    if ((stat(jbPath, &st))) {
        return ENXIO;
    }
    if (!S_ISDIR(st.st_mode)) {
        return ENOTDIR;
    }
    return KERN_SUCCESS;
}

int jailbreak_get_bmhash_path(char jbPath[150]) {
    struct utsname name;
    int ret = uname(&name);
    if (ret) return errno;
    if (atoi(name.release) < 20) return ENOTSUP;
    char bmhash[97];
    jailbreak_get_bmhash(bmhash);
    snprintf(jbPath, 150, "/private/preboot/%s", bmhash);
    return 0;
}
