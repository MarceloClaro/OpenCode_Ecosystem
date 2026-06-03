"""Windows-compatible fcntl stub for cross-process file locking."""
import msvcrt
import os

LOCK_EX = 1
LOCK_UN = 2

def flock(file_handle, operation):
    if operation == LOCK_EX:
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_LOCK, 1)
    elif operation == LOCK_UN:
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
