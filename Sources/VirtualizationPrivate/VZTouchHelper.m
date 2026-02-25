#import "include/VirtualizationPrivate.h"

@implementation VZTouchHelper

+ (id)createTouchWithView:(id)view index:(NSInteger)index phase:(NSInteger)phase location:(CGPoint)location swipeAim:(NSInteger)swipeAim timestamp:(NSTimeInterval)timestamp {
    Class touchClass = NSClassFromString(@"_VZTouch");
    if (!touchClass) {
        return nil;
    }
    
    id touch = [[touchClass alloc] init];


    [touch setValue:@((unsigned char)index) forKey:@"_index"];
    [touch setValue:@(phase) forKey:@"_phase"];
    [touch setValue:@(swipeAim) forKey:@"_swipeAim"];
    [touch setValue:@(timestamp) forKey:@"_timestamp"];
    
    [touch setValue:[NSValue valueWithPoint:location] forKey:@"_location"];

    return touch;
}

@end