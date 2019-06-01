# We now do not want to use /dev/shm or /run/shm and no ramfs paths
# If /run/user/{uid} is available, we prefer it to /tmp
# And we want to try /var/run as a last resort
# If all fails, fallback to platform's tmp dir

from memory_tempfile import MemoryTempfile
import memory_tempfile

# By the way, all paths with string {uid} will have it replaced with the user id
tempfile = MemoryTempfile(preferred_paths=['/run/user/{uid}'], remove_paths=['/dev/shm', '/run/shm'],filesystem_types=['tmpfs'], fallback=True)

if tempfile.found_mem_tempdir():
    print('We could use any of the followig paths: {}'.format(tempfile.get_usable_mem_tempdir_paths()))
    print('And we are using now: {}'.format(tempfile.gettempdir()))

with tempfile.NamedTemporaryFile(delete=False) as ntf:
    # use it as usual...
    pass