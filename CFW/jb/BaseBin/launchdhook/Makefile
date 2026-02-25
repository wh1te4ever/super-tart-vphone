TARGET = launchdhook.dylib
CC = clang

CFLAGS = -framework Foundation -framework CoreServices -framework Security -framework IOKit -I../.include -Isrc -isysroot $(shell xcrun --sdk iphoneos --show-sdk-path) -arch arm64 -arch arm64e -miphoneos-version-min=15.0 -Wno-deprecated-declarations -fobjc-arc -O2
LDFLAGS = -dynamiclib

sign: $(TARGET)
	@ldid -S $^

$(TARGET): $(wildcard src/*.m src/*.c)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

clean:
	@rm -f $(TARGET)
