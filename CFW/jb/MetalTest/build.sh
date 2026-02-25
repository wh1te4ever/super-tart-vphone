xcrun -sdk iphoneos clang \
    -arch arm64 \
    -Weverything main.m \
    -o MetalTest \
    -framework Metal \
    -framework Foundation \
    -framework IOKit \
    -framework CoreFoundation \
    -lcompression -O0

ldid -Sents.plist -M -Ksigncert.p12 ./MetalTest