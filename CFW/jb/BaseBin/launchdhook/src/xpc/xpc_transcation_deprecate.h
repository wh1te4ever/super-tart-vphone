#ifndef __XPC_TRANSACTION_DEPRECATE_H__
#define __XPC_TRANSACTION_DEPRECATE_H__

#include <Availability.h>
#include <sys/cdefs.h>

#ifndef __XPC_INDIRECT__
#error "Please #include <xpc/xpc.h> instead of this file directly."
#endif // __XPC_INDIRECT__ 

#ifndef XPC_TRANSACTION_DEPRECATED
#define XPC_TRANSACTION_DEPRECATED
#endif

#pragma mark Transactions

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_TRANSACTION_DEPRECATED
void
xpc_transaction_exit_clean(void);

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_TRANSACTION_DEPRECATED
void
xpc_transaction_interrupt_clean_exit(void);

__OSX_AVAILABLE_STARTING(__MAC_10_7, __IPHONE_5_0)
XPC_TRANSACTION_DEPRECATED
void
xpc_transactions_enable(void);

#endif
