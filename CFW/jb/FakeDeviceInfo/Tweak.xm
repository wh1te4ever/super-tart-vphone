#import <substrate.h>
#import <Foundation/Foundation.h>
#import <UIKit/UIKit.h>
#import <CoreFoundation/CoreFoundation.h>

%hook SBBootDefaults
-(BOOL)dontLockAfterCrash{
    return YES;
}
%end

extern "C" CFPropertyListRef MGCopyAnswer(CFStringRef);

/* step64 and follow_cal functions are taken from: https://github.com/xerub/macho/blob/master/patchfinder64.c */
typedef unsigned long long addr_t;

static addr_t step64(const uint8_t *buf, addr_t start, size_t length, uint32_t what, uint32_t mask) {
	addr_t end = start + length;
	while (start < end) {
		uint32_t x = *(uint32_t *)(buf + start);
		if ((x & mask) == what) {
			return start;
		}
		start += 4;
	}
	return 0;
}

// Modified version of find_call64(), replaced what/mask arguments in the function to the ones for branch instruction (0x14000000, 0xFC000000)
static addr_t find_branch64(const uint8_t *buf, addr_t start, size_t length) {
	return step64(buf, start, length, 0x14000000, 0xFC000000);
}

static addr_t follow_branch64(const uint8_t *buf, addr_t branch) {
	long long w;
	w = *(uint32_t *)(buf + branch) & 0x3FFFFFF;
	w <<= 64 - 26;
	w >>= 64 - 26 - 2;
	return branch + w;
}


static int32_t (*orig_MGGetSInt32Answer)(CFStringRef question, int32_t defaultValue);
int32_t new_MGGetSInt32Answer(CFStringRef question, int32_t defaultValue) {
    if (!question) {
        return orig_MGGetSInt32Answer(question, defaultValue);
    }
    
    NSString *target = (__bridge NSString *)question;
    
    if ([target isEqualToString:@"JwLB44/jEB8aFDpXQ16Tuw"]) {	//HomeButtonType
        int32_t spoofedValue = 2; 
        return spoofedValue;
    }
    
    return orig_MGGetSInt32Answer(question, defaultValue);
}

static CFPropertyListRef (*orig_MGCopyAnswer_internal)(CFStringRef property, uint32_t *outTypeCode);
CFPropertyListRef new_MGCopyAnswer_internal(CFStringRef property, uint32_t *outTypeCode) {
    NSString *target = (__bridge NSString *)property;
    
    if ([target isEqualToString:@"oPeik/9e8lQWMszEjbPzng"]) {	//ArtworkTraits
        CFPropertyListRef origResult = orig_MGCopyAnswer_internal(property, outTypeCode);
        NSMutableDictionary *customDict = nil;
        
        if (origResult) {
            NSDictionary *origDict = (__bridge NSDictionary *)origResult;
            
            if ([origDict isKindOfClass:[NSDictionary class]]) {
                customDict = [origDict mutableCopy];
            }
            
            CFRelease(origResult);
        }
        
        if (!customDict) {
            customDict = [[NSMutableDictionary alloc] init];
        }
        
        customDict[@"ArtworkDeviceSubType"] = @2556;
        
        return (__bridge_retained CFPropertyListRef)customDict;
    }

	return orig_MGCopyAnswer_internal(property, outTypeCode);
}

static Boolean (*orig_MGGetBoolAnswer)(CFStringRef question);
Boolean new_MGGetBoolAnswer(CFStringRef question) {
    if (!question) {
        return orig_MGGetBoolAnswer(question);
    }
    
    NSString *target = (__bridge NSString *)question;
    
    if ([target isEqualToString:@"DeviceSupportsDynamicIsland"]) {
        return true; 
    }
    return orig_MGGetBoolAnswer(question);
}

typedef struct {
	BOOL itemIsEnabled[46];
	char timeString[64];
	char shortTimeString[64];
	char dateString[256];
	int gsmSignalStrengthRaw;
	int secondaryGsmSignalStrengthRaw;
	int gsmSignalStrengthBars;
	int secondaryGsmSignalStrengthBars;
	char serviceString[100];
	char secondaryServiceString[100];
	char serviceCrossfadeString[100];
	char secondaryServiceCrossfadeString[100];
	char serviceImages[2][100];
	char operatorDirectory[1024];
	unsigned serviceContentType;
	unsigned secondaryServiceContentType;
	unsigned cellLowDataModeActive : 1;
	unsigned secondaryCellLowDataModeActive : 1;
	int wifiSignalStrengthRaw;
	int wifiSignalStrengthBars;
	unsigned wifiLowDataModeActive : 1;
	unsigned dataNetworkType;
	unsigned secondaryDataNetworkType;
	int batteryCapacity;
	unsigned batteryState;
	char batteryDetailString[150];
	int bluetoothBatteryCapacity;
	int thermalColor;
	unsigned thermalSunlightMode : 1;
	unsigned slowActivity : 1;
	unsigned syncActivity : 1;
	char activityDisplayId[256];
	unsigned bluetoothConnected : 1;
	unsigned displayRawGSMSignal : 1;
	unsigned displayRawWifiSignal : 1;
	unsigned locationIconType : 2;
	unsigned voiceControlIconType : 2;
	unsigned quietModeInactive : 1;
	unsigned tetheringConnectionCount;
	unsigned batterySaverModeActive : 1;
	unsigned deviceIsRTL : 1;
	unsigned lock : 1;
	char breadcrumbTitle[256];
	char breadcrumbSecondaryTitle[256];
	char personName[100];
	unsigned electronicTollCollectionAvailable : 1;
	unsigned radarAvailable : 1;
	unsigned announceNotificationsAvailable : 1;
	unsigned wifiLinkWarning : 1;
	unsigned wifiSearching : 1;
	double backgroundActivityDisplayStartDate;
	unsigned shouldShowEmergencyOnlyStatus : 1;
	unsigned emergencyOnly : 1;
	unsigned secondaryCellularConfigured : 1;
	char primaryServiceBadgeString[100];
	char secondaryServiceBadgeString[100];
	char quietModeImage[256];
	char quietModeName[256];
} SCD_Struct_SB65;

@interface SBStatusBarStateAggregator : NSObject {
	SCD_Struct_SB65 _data;
}
@end


%hook SBStatusBarStateAggregator
-(void)_updateBatteryItems {
	%orig;
	SCD_Struct_SB65 *dataPtr = &(MSHookIvar<SCD_Struct_SB65>(self, "_data"));
	dataPtr->batteryCapacity = 100;	//battery percent 100%
	dataPtr->batteryState = 1;	//charging now
}
%end


%ctor{
		MSImageRef libGestalt = MSGetImageByName("/usr/lib/libMobileGestalt.dylib");
		if (libGestalt) {
			// Get "_MGCopyAnswer" symbol
			void *MGCopyAnswerFn = MSFindSymbol(libGestalt, "_MGCopyAnswer");
			/*
			 * get address of MGCopyAnswer_internal by doing symbol + offset (should be 8 bytes)
			 * note: hex implementation of MGCopyAnswer: 01 00 80 d2 01 00 00 14 (from iOS 9+)
			 * so address of MGCopyAnswer + offset = MGCopyAnswer_internal. MGCopyAnswer_internal *always follows MGCopyAnswer (*from what I've checked)
			 */
			const uint8_t *MGCopyAnswer_ptr = (const uint8_t *)((uint64_t)MGCopyAnswerFn & 0xfffffffff);
			addr_t branch = find_branch64(MGCopyAnswer_ptr, 0, 8);
			addr_t branch_offset = follow_branch64((MGCopyAnswer_ptr), branch);
			MSHookFunction(((void *)((const uint8_t *)MGCopyAnswerFn + branch_offset)), (void *)new_MGCopyAnswer_internal, (void **)&orig_MGCopyAnswer_internal);

			void *MGGetSInt32AnswerFn = MSFindSymbol(libGestalt, "_MGGetSInt32Answer");
			MSHookFunction((void*)MGGetSInt32AnswerFn, (void*)new_MGGetSInt32Answer, (void**)&orig_MGGetSInt32Answer);

			void *MGGetBoolAnswerFn = MSFindSymbol(libGestalt, "_MGGetBoolAnswer");
			MSHookFunction((void*)MGGetBoolAnswerFn, (void*)new_MGGetBoolAnswer, (void**)&orig_MGGetBoolAnswer);
		}
	
}

