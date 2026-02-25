CC = clang

CHOMA_DYLIB_PATH ?= 0
CHOMA_PATH       ?= external/ChOma
CFLAGS            = -O2 -framework Foundation -I$(CHOMA_PATH)/include
CFLAGS_MACOS      = $(CFLAGS)
CFLAGS_IOS        = $(CFLAGS) -isysroot $(shell xcrun --sdk iphoneos --show-sdk-path) -miphoneos-version-min=15.0 -arch arm64 -arch arm64e
LDFLAGS           = -lcompression

all: output/macos/libxpf.dylib output/ios/libxpf.dylib output/macos/xpf_test output/ios/xpf_test

ifneq ($(CHOMA_DYLIB_PATH), 0)
CHOMA_DEP = 
LDFLAGS  += -L$(CHOMA_DYLIB_PATH) -lchoma
else
CHOMA_DEP = $(CHOMA_PATH)/src/*.c
endif 

output/macos/libxpf.dylib: $(wildcard src/*.c) $(CHOMA_DEP)
	@mkdir -p $(shell dirname $@)
	$(CC) $(CFLAGS_MACOS) $(LDFLAGS) -dynamiclib -install_name @loader_path/libxpf.dylib -o $@ $^

output/ios/libxpf.dylib: $(wildcard src/*.c) $(CHOMA_DEP)
	@mkdir -p $(shell dirname $@)
	$(CC) $(CFLAGS_IOS) $(LDFLAGS) -dynamiclib -install_name @loader_path/libxpf.dylib -o $@ $^
	ldid -S $@

output/macos/xpf_test: $(wildcard src/cli/*.c)
	@mkdir -p $(shell dirname $@)
	$(CC) $(CFLAGS_MACOS) $(LDFLAGS) -L$(shell dirname $@) -lxpf -o $@ $^

output/ios/xpf_test: $(wildcard src/cli/*.c)
	@mkdir -p $(shell dirname $@)
	$(CC) $(CFLAGS_IOS) $(LDFLAGS) -L$(shell dirname $@) -lxpf -o $@ $^
	@ldid -S $@

clean:
	@rm -rf output