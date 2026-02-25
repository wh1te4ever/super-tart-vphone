xcrun -sdk iphoneos clang \
    -arch arm64 \
    -Weverything main.m krw.c \
    -o tfp0test \
    -framework Foundation \
    -framework IOKit \
    -framework CoreFoundation \
    -lcompression -O0

ldid -Sents.plist -M -Ksigncert.p12 ./tfp0test