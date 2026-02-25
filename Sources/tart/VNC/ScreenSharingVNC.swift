import Foundation
import Dynamic
import Virtualization
import Cocoa
import VirtualizationPrivate

// class ScreenSharingVNC: VNC {
//   let vmConfig: VMConfig

//   init(vmConfig: VMConfig) {
//     self.vmConfig = vmConfig
//   }

//   func waitForURL(netBridged: Bool) async throws -> URL {
//     let vmMACAddress = MACAddress(fromString: vmConfig.macAddress.string)!
//     let ip = try await IP.resolveIP(vmMACAddress, resolutionStrategy: netBridged ? .arp : .dhcp, secondsToWait: 60)

//     if let ip = ip {
//       return URL(string: "vnc://\(ip)")!
//     }

//     throw IPNotFound()
//   }

//   func stop() throws {
//     // nothing to do
//   }
// }

enum TouchPhase: Int {
    case begin = 0      // UITouchPhase.began
    case moving = 1     // UITouchPhase.moved
    case stationary = 2 // UITouchPhase.stationary
    case end = 3        // UITouchPhase.ended
    case cancelled = 4  // UITouchPhase.cancelled
}

struct NormalizedResult {
    var point: CGPoint
    var isInvalid: Bool // 어셈블리의 W2에 해당
}

struct TouchSwipeAim {
    var edge: Int    // offset +0 (STR X0)
    var isInvalid: Bool // offset +8 (STRB W9)
}

class VirtualMachineView: VZVirtualMachineView {
    var currentTouchSwipeAim: Int64 = 0
    var isSwipeAimActive: Bool = false

    //1
    override func mouseDragged(with event: NSEvent) {
        handleMouseDraggedInternal(event)
        
        super.mouseDragged(with: event)
    }

    private func handleMouseDraggedInternal(_ event: NSEvent) {
        let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

        let locationInWindow = event.locationInWindow
        let normalizedPoint = normalizeCoordinate(locationInWindow)
        
        let swipeAim = self.getCurrentTouchSwipeAim()

        if (multiTouchDevices.count as Int > 0) {
            guard let touch = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 0,
            phase: 1,
            location: normalizedPoint.point, // 이제 CGPoint를 그대로 넘겨도 안전합니다!
            swipeAim: Int(swipeAim),
            timestamp: event.timestamp
            ) else {
                return
            }
            // let touch = Dynamic._VZTouch(view: self.virtualMachine, index: 0, phase: 1, location: normalizedPoint.point, swipeAim: Int(swipeAim), timestamp: event.timestamp).asObject
            let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch]).asObject

            let multiTouchDevice = multiTouchDevices.object(at: 0)
            Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
        }
    }

    //2
    override func mouseDown(with event: NSEvent) {
        handleMouseDownInternal(event)
        
        super.mouseDown(with: event)
    }

    private func handleMouseDownInternal(_ event: NSEvent) {
        let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

        let locationInWindow = event.locationInWindow
        let normalizedPoint = normalizeCoordinate(locationInWindow)
        
        let localPoint = self.convert(locationInWindow, from: nil)
        let edgeResult = hitTestEdge(at: localPoint)
        self.currentTouchSwipeAim = Int64(edgeResult);

        if (multiTouchDevices.count as Int > 0) {
            let locationValue = NSValue(point: normalizedPoint.point)

            guard let touch = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 0,
            phase: 0,
            location: normalizedPoint.point, // 이제 CGPoint를 그대로 넘겨도 안전합니다!
            swipeAim: edgeResult,
            timestamp: event.timestamp
            ) else {
                return
            }

            let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch] as NSArray).asObject

            let multiTouchDevice = multiTouchDevices.object(at: 0)
            Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
        }
    }

    //3 
    override func rightMouseDown(with event: NSEvent) {
        handleRightMouseDownInternal(event)
        
        super.rightMouseDown(with: event)
    }

    private func handleRightMouseDownInternal(_ event: NSEvent) {
        let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

        let locationInWindow = event.locationInWindow
        let normalizedPoint = normalizeCoordinate(locationInWindow)
        
        guard !normalizedPoint.isInvalid else {
            print("normalizeCoordinate error, result.isInvalid")
            return 
        }

        let localPoint = self.convert(locationInWindow, from: nil)
        let edgeResult = hitTestEdge(at: localPoint)

        self.currentTouchSwipeAim = Int64(edgeResult);

        if (multiTouchDevices.count as Int > 0) {
            guard let touch = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 0,
            phase: 0,
            location: normalizedPoint.point, // 이제 CGPoint를 그대로 넘겨도 안전합니다!
            swipeAim: Int(edgeResult),
            timestamp: event.timestamp
            ) else {
                return
            }

            guard let touch2 = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 1,
            phase: 0,
            location: normalizedPoint.point, // 이제 CGPoint를 그대로 넘겨도 안전합니다!
            swipeAim: Int(edgeResult),
            timestamp: event.timestamp
            ) else {
                return
            }

            let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch, touch2]).asObject

            let multiTouchDevice = multiTouchDevices.object(at: 0)
            Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
        }
    }

    //4
    override func mouseUp(with event: NSEvent) {
        handleMouseUpInternal(event)
        
        super.mouseUp(with: event)
    }

    private func handleMouseUpInternal(_ event: NSEvent) {
        let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

        let locationInWindow = event.locationInWindow
        let normalizedPoint = normalizeCoordinate(locationInWindow)
    
        let swipeAim = self.getCurrentTouchSwipeAim()

        if (multiTouchDevices.count as Int > 0) {
            guard let touch = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 0,
            phase: 3,
            location: normalizedPoint.point,
            swipeAim: Int(swipeAim),
            timestamp: event.timestamp
            ) else {
                return
            }
            let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch]).asObject

            let multiTouchDevice = multiTouchDevices.object(at: 0)
            Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
        }
    }

    //5. 
    override func rightMouseUp(with event: NSEvent) {
        handleRightMouseUpInternal(event)
        
        super.rightMouseUp(with: event)
    }

    private func handleRightMouseUpInternal(_ event: NSEvent) {
        let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

        let locationInWindow = event.locationInWindow
        let normalizedPoint = normalizeCoordinate(locationInWindow)
        
        guard !normalizedPoint.isInvalid else {
            print("normalizeCoordinate error, result.isInvalid")
            return 
        }

        let localPoint = self.convert(locationInWindow, from: nil)
        let edgeResult = hitTestEdge(at: localPoint)

        let swipeAim = self.getCurrentTouchSwipeAim()

        if (multiTouchDevices.count as Int > 0) {
            guard let touch = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 0,
            phase: 3,
            location: normalizedPoint.point,
            swipeAim: Int(swipeAim),
            timestamp: event.timestamp
            ) else {
                return
            }

            guard let touch2 = VZTouchHelper.createTouch(
            withView: self.virtualMachine,
            index: 1,
            phase: 3,
            location: normalizedPoint.point,
            swipeAim: Int(swipeAim),
            timestamp: event.timestamp
            ) else {
                return
            }
            let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch, touch2]).asObject

            let multiTouchDevice = multiTouchDevices.object(at: 0)
            Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
        }
    }

    private func getCurrentTouchSwipeAim() -> Int64 {
        var value: Int64 = 0
        if let ivar = class_getInstanceVariable(type(of: self), "_currentTouchSwipeAim") {
            let ptr = UnsafeRawPointer(Unmanaged.passUnretained(self).toOpaque())
            value = ptr.advanced(by: ivar_getOffset(ivar)).assumingMemoryBound(to: Int64.self).pointee
        }
        return value
    }

    private func convertToNormalizedPoint(_ point: NSPoint) -> CGPoint {
        let localPoint = self.convert(point, from: nil)
        let bounds = self.bounds
        
        if bounds.width == 0 || bounds.height == 0 {
            return .zero
        }
        
        let x = Double(localPoint.x / bounds.width)
        let y = Double(localPoint.y / bounds.height)
        
        return CGPoint(x: x, y: y)
    }

    func normalizeCoordinate(_ point: CGPoint) -> NormalizedResult {
        let bounds = self.bounds
        
        if bounds.size.width <= 0 || bounds.size.height <= 0 {
            return NormalizedResult(point: .zero, isInvalid: true)
        }
        
        let localPoint = self.convert(point, from: nil)
        
        var nx = Double(localPoint.x / bounds.size.width)
        var ny = Double(localPoint.y / bounds.size.height)
        
        nx = max(0.0, min(1.0, nx))
        ny = max(0.0, min(1.0, ny))
        
        if !self.isFlipped {
            ny = 1.0 - ny
        }
        
        return NormalizedResult(point: CGPoint(x: nx, y: ny), isInvalid: false)
    }

    func getNormalizedCoordinate(for view: NSView, point: CGPoint) -> (x: CGFloat, y: CGFloat, isError: Bool) {
        // 1. view.bounds 호출 (selRef_bounds)
        let bounds = view.bounds
        let width = bounds.width
        let height = bounds.height

        // 2. bounds의 너비나 높이가 0인지 검사 (TST X8, #0x7FFFFFFFFFFFFFFF)
        // 부동소수점 0.0 (또는 -0.0)을 비트 단위로 검사하는 어셈블리 로직과 동일
        if width == 0 || height == 0 {
            return (x: 0.0, y: 0.0, isError: true) // loc_10001A3A0 분기 (W2 = 1)
        }

        // 3. convertPoint:fromView: 호출 (fromView가 nil이므로 Window/Screen 좌표계에서 변환)
        let convertedPoint = view.convert(point, from: nil)

        // 4. X 좌표 정규화 및 Clamping (0.0 ~ 1.0)
        var normalizedX = convertedPoint.x / width
        if normalizedX >= 1.0 {
            normalizedX = 1.0
        } else if normalizedX < 0.0 || normalizedX.isNaN {
            // 어셈블리의 복잡한 조건문(CCMP, AND 등)은 NaN(Not a Number) 및 음수를 처리해 0.0으로 만듭니다.
            normalizedX = 0.0
        }

        // 5. Y 좌표 정규화 및 Clamping (0.0 ~ 1.0)
        var normalizedY = convertedPoint.y / height
        if normalizedY >= 1.0 {
            normalizedY = 1.0
        } else if normalizedY < 0.0 || normalizedY.isNaN {
            normalizedY = 0.0
        }

        // 6. view.isFlipped 검사 및 Y 좌표 보정
        // iOS(UIView)는 기본적으로 true, macOS(NSView)는 false가 기본값입니다.
        #if canImport(AppKit)
        let isFlipped = view.isFlipped
        #else
        // UIView는 isFlipped 속성이 없지만 CoreGraphics 좌표계 관점에서 항상 뒤집혀 있다고 취급됨
        let isFlipped = true 
        #endif

        if !isFlipped {
            normalizedY = 1.0 - normalizedY // FSUB D0, D0, D8
        }

        // 7. 최종 반환 (X0 = D9, X1 = D0, W2 = 0)
        return (x: normalizedX, y: normalizedY, isError: false)
    }

    private func isValid(_ point: CGPoint) -> Bool {
        return !point.x.isNaN && !point.y.isNaN
    }

    func hitTestEdge(at point: CGPoint) -> Int {
        let bounds = self.bounds
        let clickX = point.x
        let clickY = point.y
        
        let width = bounds.size.width
        let height = bounds.size.height
        
        let distLeft = clickX
        let distRight = width - clickX
        
        var minDist: Double
        var edgeCode: Int
        
        if distRight < distLeft {
            minDist = distRight
            edgeCode = 4 // Right
        } else {
            minDist = distLeft
            edgeCode = 8 // Left
        }
        
        let topCode = self.isFlipped ? 2 : 1
        let bottomCode = self.isFlipped ? 1 : 2
        
        let distTop = clickY
        if distTop < minDist {
            minDist = distTop
            edgeCode = topCode
        }
        
        let distBottom = height - clickY
        if distBottom < minDist {
            minDist = distBottom
            edgeCode = bottomCode
        }
        
        if minDist < 32.0 {
            return edgeCode
        } else {
            return 0 // VMViewEdge.none
        }
    }




    
    // override func mouseDown(with event: NSEvent) {
    //     print("Mouse Down at: \(event.locationInWindow)")

    //     let point: NSPoint = self.convert(event.locationInWindow, to:nil)

    //     let touch = Dynamic._VZTouch(view: self.virtualMachine, index: 0, phase: TouchPhase.begin, location: point, swipeAim: 0.0, timestamp: event.timestamp).asObject
    //     let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch]).asObject

    //     let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

    //     if (multiTouchDevices.count as Int > 0) {
    //         print("multiTouchDevices.count: \(multiTouchDevices.count as Int)") // 1 (expected)
    //         let multiTouchDevice = multiTouchDevices.object(at: 0)
    //         Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
    //         print("Sent multi-touch event")
    //     }
    // }

    // override func mouseDragged(with event: NSEvent) {
    //     let point: NSPoint = self.convert(event.locationInWindow, to: nil)
    //     print("Mouse drag at: (\(point.x), \(point.y))")

    //     let touch = Dynamic._VZTouch(view: self.virtualMachine, index: 0, phase: TouchPhase.moving, location: point, swipeAim: 0.0, timestamp: event.timestamp).asObject
    //     let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch]).asObject

    //     let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

    //     if (multiTouchDevices.count as Int > 0) {
    //         print("multiTouchDevices.count: \(multiTouchDevices.count as Int)") // 1 (expected)
    //         let multiTouchDevice = multiTouchDevices.object(at: 0)
    //         Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
    //         print("Sent multi-touch event")
    //     }
    // }

    // override func mouseUp(with event: NSEvent) {
    //     let point: NSPoint = self.convert(event.locationInWindow, to: nil)
    //     print("Mouse up at: (\(point.x), \(point.y))")

    //     let touch = Dynamic._VZTouch(view: self.virtualMachine, index: 0, phase: TouchPhase.end, location: point, swipeAim: 0.0, timestamp: event.timestamp).asObject
    //     let touchEvent = Dynamic._VZMultiTouchEvent(touches: [touch]).asObject

    //     let multiTouchDevices: NSArray = Dynamic(self.virtualMachine)._multiTouchDevices.asArray!

    //     if (multiTouchDevices.count as Int > 0) {
    //         print("multiTouchDevices.count: \(multiTouchDevices.count as Int)") // 1 (expected)
    //         let multiTouchDevice = multiTouchDevices.object(at: 0)
    //         Dynamic(multiTouchDevice).sendMultiTouchEvents([touchEvent] as NSArray)
    //         print("Sent multi-touch event")
    //     }
    // }
}

class ScreenSharingVNC: VNC {
    let vmConfig: VMConfig
    var virtualMachine: VZVirtualMachine?
    
    // 윈도우 참조를 유지하기 위한 프로퍼티
    private var windowController: NSWindowController?

    init(vmConfig: VMConfig) {
        self.vmConfig = vmConfig
    }
    
    // 주입받은 실행 중인 VM 인스턴스를 저장하는 메서드가 필요할 수 있습니다.
    // 기존 코드에는 없었지만, 직접 화면을 그리려면 실행 중인 VZVirtualMachine 객체가 필수입니다.
    func setVirtualMachine(_ vm: VZVirtualMachine) {
        self.virtualMachine = vm
    }

    // 기존: URL을 반환 (VNC 연결용)
    // 변경: 직접 윈도우를 띄우고, 더미 URL 혹은 로컬 URL을 반환하여 흐름 유지
    func waitForURL(netBridged: Bool) async throws -> URL {
        // UI 조작은 메인 스레드에서 실행되어야 함
        try await MainActor.run {
            guard let vm = self.virtualMachine else {
                throw NSError(domain: "ScreenSharingVNC", code: -1, userInfo: [NSLocalizedDescriptionKey: "VM instance not set"])
            }
            
            self.openVMWindow(for: vm)
        }

        // 흐름 유지를 위해 로컬호스트 URL 반환 (호출부에서 에러가 나지 않도록)
        return URL(string: "vm://")!
    }

    func stop() throws {
        // 윈도우 닫기
        DispatchQueue.main.async {
            self.windowController?.close()
            self.windowController = nil
        }
    }
    
    // MARK: - Private Helpers
    
    private func openVMWindow(for vm: VZVirtualMachine) {
        let vmView: NSView
        // macOS 16.0 (Tahoe) 이상인지 런타임 체크 
        // (만약 타겟 버전이 다르면 16.0을 15.0 등으로 수정하세요)
        if #available(macOS 16.0, *) {
            let view = VZVirtualMachineView()
            view.virtualMachine = vm
            view.capturesSystemKeys = true
            vmView = view
        } else {
            let view = VirtualMachineView()
            view.virtualMachine = vm
            view.capturesSystemKeys = true
            vmView = view
        }
        
        let pixelWidth: CGFloat = 1179
        let pixelHeight: CGFloat = 2556
        let scale: CGFloat = 3.0 

        let windowSize = NSSize(width: pixelWidth, height: pixelHeight)

        let window = NSWindow(
            contentRect: NSRect(origin: .zero, size: windowSize),
            styleMask: [.titled, .closable, .resizable, .miniaturizable], // resizable이 있어야 비율 고정이 먹힘
            backing: .buffered,
            defer: false
        )

        window.contentAspectRatio = windowSize
        
        window.title = "vphone"
        window.contentView = vmView
        window.center()
      
        
        // 3. 윈도우 컨트롤러에 저장 (메모리 해제 방지)
        let controller = NSWindowController(window: window)
        controller.showWindow(nil)
        
        self.windowController = controller

        // 1) NSApplication 인스턴스가 없다면 생성 (CLI 툴 환경 대비)
        if NSApp == nil {
            _ = NSApplication.shared
        }
        
        // 2) 앱의 활성화 정책을 'regular'로 변경 (Dock에 아이콘 표시 및 포커스 획득 가능)
        // 만약 Dock에 아이콘이 생기는 게 싫다면 .accessory 로 설정하세요.
        NSApp.setActivationPolicy(.regular)
        
        // 3) 윈도우를 최상단으로 올리고 키보드 입력을 받을 수 있는 메인 창으로 설정
        window.makeKeyAndOrderFront(nil)
        
        // 4) 터미널을 무시하고 이 앱(윈도우)을 강제로 맨 앞으로 활성화하여 포커스 가져오기
        NSApp.activate(ignoringOtherApps: true)
    }
}