// modified from WTF/wtf/spi/darwin/XPCSPI.h
// Most values searched from Apple OSS
#ifndef __XPC_PRIVATE_H__
#define __XPC_PRIVATE_H__

#ifndef __BLOCKS__
#error "XPC private APIs require Blocks support."
#endif // __BLOCKS__

#include <dispatch/dispatch.h>
#include <uuid/uuid.h>
#include <os/object.h>
#include <xpc/xpc.h>
#include <xpc/base.h>
#include <mach/std_types.h>

#define XPC_ENV_SANDBOX_CONTAINER_ID "APP_SANDBOX_CONTAINER_ID"

#define XPC_PIPE_FLAG_PRIVILEGED (1 << 5)

#if !defined(XPC_NOESCAPE)
#define XPC_NOESCAPE
#endif

typedef xpc_object_t xpc_bundle_t;

typedef struct {
	char *stream;
	uint64_t token;
} xpc_event_publisher_t;

typedef int xpc_event_publisher_action_t;
typedef boolean_t (*xpc_array_applier_func_t)(size_t, xpc_object_t, void *);
typedef boolean_t (*xpc_pipe_mig_call_t)(mach_msg_header_t *request, mach_msg_header_t *reply);
typedef int64_t xpc_service_type_t;

//XPC_ASSUME_NONNULL_BEGIN
__BEGIN_DECLS

#define XPC_TYPE_MACH_SEND (&_xpc_type_mach_send)
__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_EXPORT
XPC_TYPE(_xpc_type_mach_send);

#define XPC_TYPE_MACH_RECV (&_xpc_type_mach_recv)
__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_EXPORT
XPC_TYPE(_xpc_type_mach_recv);

#define XPC_TYPE_POINTER (&_xpc_type_pointer)
__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT
XPC_TYPE(_xpc_type_pointer);

#define XPC_TYPE_PIPE (&_xpc_type_pipe)
__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT
XPC_TYPE(_xpc_type_pipe);
XPC_DECL(xpc_pipe);

XPC_EXPORT
const char* xpc_strerror(int);

#pragma mark Bundle

XPC_EXPORT
xpc_bundle_t
xpc_bundle_create(const char *bundle, int mode);

XPC_EXPORT
const char *
xpc_bundle_get_executable_path(xpc_object_t bundle);

XPC_EXPORT
xpc_object_t
xpc_bundle_get_info_dictionary(xpc_bundle_t bundle);

#pragma mark Dictionary

XPC_EXPORT XPC_NONNULL_ALL
mach_port_t
xpc_dictionary_copy_mach_send(xpc_object_t xdict, const char *key);

XPC_EXPORT XPC_NONNULL_ALL
boolean_t
xpc_dictionary_expects_reply(xpc_object_t xdict);

XPC_EXPORT XPC_NONNULL1 XPC_NONNULL2
void
xpc_dictionary_extract_mach_recv(xpc_object_t xdict, const char *key);

XPC_EXPORT XPC_NONNULL_ALL
void
xpc_dictionary_get_audit_token(xpc_object_t xdict, audit_token_t *token);

XPC_EXPORT XPC_NONNULL_ALL
pointer_t
xpc_dictionary_get_pointer(xpc_object_t xdict, const char *key);

XPC_EXPORT XPC_NONNULL1 XPC_NONNULL2
void
xpc_dictionary_set_mach_recv(xpc_object_t xdict, const char *key, mach_port_t value);

XPC_EXPORT XPC_NONNULL1 XPC_NONNULL2
void
xpc_dictionary_set_mach_send(xpc_object_t xdict, const char *key, mach_port_t value);

XPC_EXPORT
void
xpc_dictionary_set_pointer(xpc_object_t xdict, const char *key, pointer_t value);

#pragma mark Mach

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_EXPORT XPC_MALLOC XPC_RETURNS_RETAINED XPC_WARN_RESULT
xpc_object_t
xpc_mach_send_create(mach_port_t value);

XPC_EXPORT XPC_NONNULL_ALL
mach_port_t
xpc_mach_send_get_right(xpc_object_t xsend);

XPC_EXPORT XPC_NONNULL_ALL
mach_port_t
xpc_mach_send_copy_right(xpc_object_t xsend);

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_EXPORT XPC_MALLOC XPC_RETURNS_RETAINED XPC_WARN_RESULT
xpc_object_t
xpc_mach_recv_create(mach_port_t value);

XPC_EXPORT XPC_NONNULL_ALL
mach_port_t
xpc_mach_recv_extract_right(xpc_object_t xrecv);

#pragma mark Pointer

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_MALLOC XPC_RETURNS_RETAINED XPC_WARN_RESULT
xpc_object_t
xpc_pointer_create(pointer_t value);

XPC_EXPORT
pointer_t
xpc_pointer_get_value(xpc_object_t xpointer);

#pragma mark Array

XPC_EXPORT
void
xpc_array_append_value(xpc_object_t xdict, xpc_object_t string);

XPC_EXPORT
boolean_t
xpc_array_apply_f(xpc_object_t xdict, xpc_array_applier_func_t, void *);

XPC_EXPORT
mach_port_t
xpc_array_copy_mach_send(xpc_object_t xarray, size_t index);

XPC_EXPORT
pointer_t
xpc_array_get_pointer(xpc_object_t xarray, size_t index);

XPC_EXPORT XPC_NONNULL1
void
xpc_array_set_mach_send(xpc_object_t xarray, size_t index, mach_port_t value);

XPC_EXPORT
void
xpc_array_set_pointer(xpc_object_t xarray, size_t index, pointer_t value);

#pragma mark Create

XPC_EXPORT
xpc_object_t
xpc_create_from_plist(void *data, size_t size);

XPC_EXPORT
xpc_object_t
xpc_create_with_format(const char * format, ...);

XPC_EXPORT
xpc_object_t
xpc_create_reply_with_format(xpc_object_t original, const char * format, ...);

#pragma mark Tracks

XPC_EXPORT
void
xpc_track_activity(void);

#pragma mark Connections

XPC_EXPORT
xpc_object_t
xpc_connection_copy_entitlement_value(xpc_connection_t connection,
	const char *entitlement);

XPC_EXPORT
void
xpc_connection_get_audit_token(xpc_connection_t, audit_token_t*);

XPC_EXPORT
void
xpc_connection_kill(xpc_connection_t, int);

XPC_EXPORT
void
xpc_connection_set_instance(xpc_connection_t, uuid_t);

XPC_EXPORT
void
xpc_connection_set_target_uid(xpc_connection_t connection, uid_t uid);

XPC_EXPORT
void
xpc_connection_set_bootstrap(xpc_connection_t, xpc_object_t);

XPC_EXPORT
void
xpc_connection_set_oneshot_instance(xpc_connection_t, uuid_t instance);

XPC_EXPORT
xpc_object_t
xpc_copy_bootstrap(void);

XPC_EXPORT
xpc_object_t
xpc_copy_entitlements_for_pid(pid_t pid);

XPC_EXPORT
xpc_object_t
xpc_copy_entitlement_for_token(const char*, audit_token_t*);

XPC_EXPORT
boolean_t
xpc_get_event_name(xpc_event_publisher_t, char *);

XPC_EXPORT
boolean_t
xpc_get_instance(uuid_t);

XPC_EXPORT
void
xpc_event_publisher_activate(xpc_event_publisher_t);

XPC_EXPORT
xpc_event_publisher_t
xpc_event_publisher_create(const char*, dispatch_queue_t);

XPC_EXPORT
int
xpc_event_publisher_fire(xpc_event_publisher_t, uint64_t, int);

XPC_EXPORT
int
xpc_event_publisher_fire_noboost(xpc_event_publisher_t, uint64_t, xpc_object_t);

XPC_EXPORT
void
xpc_event_publisher_set_handler(xpc_event_publisher_t,
	void (^)(xpc_event_publisher_action_t action,
	uint64_t event_token, xpc_object_t descriptor));

XPC_EXPORT
void
xpc_event_publisher_set_error_handler(xpc_event_publisher_t, void (^)(int));

#pragma mark Pipes

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_MALLOC XPC_RETURNS_RETAINED XPC_WARN_RESULT XPC_NONNULL1
xpc_pipe_t
xpc_pipe_create(const char *name, uint64_t flags);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_MALLOC XPC_RETURNS_RETAINED XPC_WARN_RESULT
xpc_pipe_t
xpc_pipe_create_from_port(mach_port_t port, uint64_t flags);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
void
xpc_pipe_invalidate(xpc_pipe_t pipe);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL1 XPC_NONNULL2
kern_return_t
xpc_pipe_routine(xpc_pipe_t pipe, xpc_object_t request, xpc_object_t XPC_GIVES_REFERENCE *reply);

API_AVAILABLE(macos(12.0), ios(15.0), tvos(15.0), watchos(8.0))
XPC_EXPORT XPC_WARN_RESULT XPC_NONNULL1 XPC_NONNULL3 XPC_NONNULL4
int
_xpc_pipe_interface_routine(xpc_pipe_t pipe, uint64_t routine,
	xpc_object_t message, xpc_object_t XPC_GIVES_REFERENCE *reply,
	uint64_t flags);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_simpleroutine(xpc_pipe_t pipe, xpc_object_t request);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_routine_forward(xpc_pipe_t forward_to, xpc_object_t request);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_routine_async(xpc_pipe_t pipe, xpc_object_t request, mach_port_t reply_port);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_receive(mach_port_t port, xpc_object_t *request);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_routine_reply(xpc_object_t reply);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL1 XPC_NONNULL2
kern_return_t
xpc_pipe_routine_with_flags(xpc_pipe_t pipe, xpc_object_t request,
	xpc_object_t *reply, uint32_t flags);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT XPC_NONNULL_ALL
kern_return_t
xpc_pipe_simpleroutine(xpc_pipe_t pipe, xpc_object_t message);

__OSX_AVAILABLE_STARTING(__MAC_10_9, __IPHONE_7_0)
XPC_EXPORT
kern_return_t
xpc_pipe_try_receive(mach_port_t *port, xpc_object_t *request,
	mach_port_t *out_port, xpc_pipe_mig_call_t mig_handler,
	mach_msg_size_t mig_size, uint64_t flags);

XPC_EXPORT
int
xpc_receive_mach_msg(void *a1, void *a2, void *a3,
	void *a4, xpc_object_t *xOut);

XPC_EXPORT
void
xpc_set_event(const char *stream, const char *token, xpc_object_t xdict);

XPC_EXPORT
void
xpc_set_event_state(const char *stream, const char *token, boolean_t state);

XPC_EXPORT
void
xpc_set_event_with_flags(const char *stream, const char *name,
	xpc_object_t descriptor, uint64_t flags);

XPC_EXPORT
void
xpc_set_idle_handler(void);

XPC_EXPORT
xpc_object_t
_xpc_bool_create_distinct(boolean_t value);

XPC_EXPORT
void
_xpc_bool_set_value(xpc_object_t xbool, boolean_t value);

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_EXPORT XPC_NONNULL_ALL
void
_xpc_connection_set_event_handler_f(xpc_connection_t connection,
	xpc_handler_t handler);

XPC_EXPORT
void
_xpc_data_set_value(xpc_object_t xdata, const void* bytes, size_t length);

XPC_EXPORT
xpc_object_t
_xpc_dictionary_create_reply_with_port(mach_port_t port);

XPC_EXPORT
mach_port_t
_xpc_dictionary_extract_mach_send(xpc_object_t xdict, const char* key);

XPC_EXPORT
mach_msg_id_t
_xpc_dictionary_extract_reply_msg_id(xpc_object_t xdict);

XPC_EXPORT
mach_port_t
_xpc_dictionary_extract_reply_port(xpc_object_t xdict);

XPC_EXPORT
mach_msg_id_t
_xpc_dictionary_get_reply_msg_id(xpc_object_t xdict);

XPC_EXPORT
void
_xpc_dictionary_set_remote_connection(xpc_object_t xdict, xpc_connection_t xconn);

XPC_EXPORT
void
_xpc_dictionary_set_reply_msg_id(xpc_object_t xdict, mach_msg_id_t msg_id);

XPC_EXPORT
void
_xpc_double_set_value(xpc_object_t xdouble, double value);

XPC_EXPORT
mach_port_t
_xpc_fd_get_port(xpc_object_t xfd);

__OSX_AVAILABLE_BUT_DEPRECATED(__MAC_10_4, __MAC_10_10, __IPHONE_2_0, __IPHONE_8_0)
XPC_EXPORT
void
_xpc_int64_set_value(launch_data_t, int64_t);

XPC_EXPORT
boolean_t
_xpc_payload_create_from_mach_msg(dispatch_object_t, int mode);

XPC_EXPORT
xpc_object_t
_xpc_runtime_get_entitlements_data(void);

XPC_EXPORT
xpc_object_t
_xpc_runtime_get_self_entitlements(void);

XPC_EXPORT
boolean_t
_xpc_runtime_is_app_sandboxed(void);

XPC_EXPORT
void
_xpc_service_last_xref_cancel(xpc_object_t xref);

XPC_EXPORT
boolean_t
_xpc_service_routine(uint64_t, xpc_object_t xservice, int *buf);

XPC_EXPORT
mach_port_t
_xpc_shmem_get_mach_port(xpc_object_t xshmem);

XPC_EXPORT
void
_xpc_string_set_value(xpc_object_t xstring, const char* new_string);

__END_DECLS
//XPC_ASSUME_NONNULL_END

#endif
