import numpy as np

PI = np.pi


def moduloAB(x, a, b):
    """
    Maps a real number onto the unit circle identified with the interval [a,b), b - a = 2*PI
    """
    if a >= b:
        raise ValueError('Incorrect interval ends')
    
    y = (x - a) % (b - a)
    return y + b if y < 0 else y + a
