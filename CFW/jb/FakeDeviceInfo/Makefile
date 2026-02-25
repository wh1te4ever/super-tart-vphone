GO_EASY_ON_ME = 1
DEBUG = 0
FINALPACKAGE = 1

THEOS_PACKAGE_SCHEME = rootless

THEOS_DEVICE_IP = 192.168.64.77 -p22

TARGET := iphone:clang:26.1:26.1
ARCHS = arm64 arm64e
INSTALL_TARGET_PROCESSES = SpringBoard


include $(THEOS)/makefiles/common.mk

TWEAK_NAME = FakeDeviceInfo

FakeDeviceInfo_FILES = Tweak.xm
FakeDeviceInfo_LIBRARIES = MobileGestalt
FakeDeviceInfo_CFLAGS = -fobjc-arc

include $(THEOS_MAKE_PATH)/tweak.mk
