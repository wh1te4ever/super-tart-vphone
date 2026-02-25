# litehook
Lightweight *OS hooking library with no dependencies except for libsystem

## Supported Functionality
Since this is a lightweight library, only very basic functionality is supported, this includes:
- Finding `<redacted>` symbols by parsing the dyld_shared_cache (`litehook_find_dsc_symbol`)
- Replacing a function with a branch to some other location/function, with no ability to call the original function (`litehook_hook_function`)
- Rebinding a symbol in the GOT of an image, similar to fishhook and dyld_dynamic_interpose (`litehook_rebind_symbol`)

## Supported Environments:
Architectures:
- arm64e
- arm64
- armv7s
- armv7

litehook is intended to work on iOS 10 and up.