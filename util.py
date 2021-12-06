import threading
import termios
import struct
import fcntl


def addToLibrary(l, x):
    """ Insert video into sorted list of videos by date. """
    lo, hi = 0, len(l)
    while lo < hi:
        mid = (lo+hi)//2
        if x.id == l[mid].id:
            return
        if x.date > l[mid].date:
            hi = mid
        else:
            lo = mid+1
    l.insert(lo, x)


def getFontDimensions():
    """ Find height/width aspect ratio of terminal font. """
    farg = struct.pack("HHHH", 0, 0, 0, 0)
    fretint = fcntl.ioctl(1, termios.TIOCGWINSZ, farg)
    rows, cols, xpixels, ypixels = struct.unpack("HHHH", fretint)
    #return ypixels/rows / xpixels/cols
    return ypixels*cols/rows/xpixels


# From https://github.com/salesforce/decorator-operations/blob/master/decoratorOperations/debounce_functions/debounce.py
def debounce(wait_time):
    """
    Decorator that will debounce a function so that it is called after wait_time seconds
    If it is called multiple times, will wait for the last call to be debounced and run only this one.
    See the test_debounce.py file for examples
    """

    def decorator(function):
        def debounced(*args, **kwargs):
            def call_function():
                debounced._timer = None
                return function(*args, **kwargs)

            if debounced._timer is not None:
                debounced._timer.cancel()

            debounced._timer = threading.Timer(wait_time, call_function)
            debounced._timer.start()

        debounced._timer = None
        return debounced

    return decorator
