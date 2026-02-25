TARGET = litehook_tests

CC = clang

CFLAGS = -framework Foundation -framework CoreServices -framework Security -I../src -I../external/include -isysroot $(shell xcrun --sdk iphoneos --show-sdk-path) -arch armv7 -arch arm64 -arch arm64e -miphoneos-version-min=10.0

sign: $(TARGET)
	@ldid -Sentitlements.plist $<

$(TARGET): $(wildcard *.c ../src/*.c)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

clean:
	@rm -f $(TARGET)