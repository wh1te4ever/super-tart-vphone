// VirtualizationPrivate.h
#import <Virtualization/Virtualization.h>

@interface _VZMacHardwareModelDescriptor : NSObject <NSCopying>
- (id)init;
- (void)setPlatformVersion:(unsigned int)version;
- (void)setBoardID:(unsigned int)boardID;
- (void)setISA:(long long)isa;
- (void)setInitialGuestMacOSVersion:(struct { long long x0; long long x1; long long x2; })osversion;
- (void)setMinimumSupportedHostOSVersion:(struct { long long x0; long long x1; long long x2; })osversion;
- (void)setVariantID:(unsigned int)variantID variantName:(id)name;
@end

@interface VZMacHardwareModel (Private)
+ (instancetype)_hardwareModelWithDescriptor:(id)descriptor NS_SWIFT_NAME(_hardwareModel(withDescriptor:));
@end

@interface VZVirtualMachineConfiguration (Private)
- (void)_setCoprocessors:(id)coprocessors;
- (void)_setMultiTouchDevices:(id)devices;
@end

@interface _VZMacSerialNumber : NSObject <NSCopying> {
    /* instance variables */
    struct AvpSerialNumber { 
        unsigned char _serial_number[10]; 
    } _serialNumber;
}
@property (readonly, copy) NSString *string;
/* instance methods */
- (unsigned long long)hash;
- (_Bool)isEqual:(id)equal;
- (id)copyWithZone:(struct _NSZone *)zone;
- (id)initWithString:(id)string;
@end

@interface VZMacMachineIdentifier (Private)
@property (readonly) unsigned long long _ECID;
@property (readonly) _VZMacSerialNumber *_serialNumber;
@end

@interface VZMacPlatformConfiguration (Private)
@property _Bool _productionModeEnabled;
- (_Bool)_isProductionModeEnabled;
- (void)_setProductionModeEnabled:(_Bool)enabled;
@end

@interface _VZMultiTouchDeviceConfiguration : NSObject <NSCopying>
+ (instancetype)new NS_UNAVAILABLE;
- (instancetype)init NS_UNAVAILABLE;
@end

@interface _VZUSBTouchScreenConfiguration : _VZMultiTouchDeviceConfiguration
- (instancetype)init NS_DESIGNATED_INITIALIZER;
@end

@interface _VZUSBMouseConfiguration : VZPointingDeviceConfiguration
- (id)init;
- (int)_pointingDevice;
- (id)makePointingDeviceForVirtualMachine:(id)machine pointingDeviceIndex:(unsigned long long)index;
@end

@interface VZTouchHelper : NSObject
+ (id)createTouchWithView:(id)view
                    index:(NSInteger)index
                    phase:(NSInteger)phase
                 location:(CGPoint)location
                 swipeAim:(NSInteger)swipeAim
                timestamp:(NSTimeInterval)timestamp;
@end

@interface _VZTouch : NSObject
@property (readonly) unsigned char index;
@property (readonly) long long phase;
@property (readonly) CGPoint location;
@property (readonly) long long swipeAim;
@property (readonly) double timestamp;
- (id)initWithView:(id)view index:(unsigned char)index phase:(long long)phase location:(CGPoint)location swipeAim:(long long)aim timestamp:(double)timestamp;
@end
