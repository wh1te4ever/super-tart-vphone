xcrun -sdk macosx clang \
    -arch arm64 \
    -Weverything main.m \
    -o MetalTest \
    -framework Metal \
    -framework Foundation \
    -framework IOKit \
    -framework CoreFoundation \
    -lcompression -O0