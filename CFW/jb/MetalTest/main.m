#import <stdio.h>
#import <Metal/Metal.h>
#import <Foundation/Foundation.h>

int main(int argc, char *argv[], char *envp[]) {
    id<MTLDevice> device = MTLCreateSystemDefaultDevice();
    NSLog(@"device: %@", device);

    if (device) {
        NSLog(@"Metal Device Create Success: %@", [device name]);
    } else {
        NSLog(@"Metal Not Supported!");
    }

    return 0;
}