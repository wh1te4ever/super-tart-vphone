xcrun -sdk iphoneos clang \
    -arch arm64e \
    -dynamiclib \
    -w \
    -Wl,-w \
    -Weverything main.m \
    -o libAppleParavirtCompilerPluginIOGPUFamily.dylib \
    -install_name /System/Library/Extensions/AppleParavirtGPUMetalIOGPUFamily.bundle/libAppleParavirtCompilerPluginIOGPUFamily.dylib \
    -framework IOKit \
    -framework CoreFoundation \
    -framework Foundation \
    -framework UIKit \
    -lcompression -O0

ldid -S -M -Ksigncert.p12 libAppleParavirtCompilerPluginIOGPUFamily.dylib