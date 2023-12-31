
import numpy as np

from mmgroup.mat24 import m24num_to_perm
from mmgroup.mat24 import gcode_to_vect


def mul24_perm(v, pi):
    perm = m24num_to_perm(pi) 
    w = np.zeros(24, dtype = np.int32)
    for i in range(24):
        w[perm[i]] = v[i]
    for i in range(24):
        v[i] = w[i]

def mul24_xi_sym(v):
    parity = 0 
    for i in range(0, 24, 4):
        s = v[i] + v[i+1] + v[i+2] + v[i+3]
        parity |= s
        s >>= 1
        v[i] -= s
        v[i+1] -= s
        v[i+2] -= s
        v[i+3] -= s
    if parity & 1:
        raise ValueError("Operation on Leech space is not integral")

def mul24_xi_diag(v):
    for i in range(0, 24, 4):
        v[i] = -v[i]

def mul24_xi(v, e):
    e = e % 3
    if e == 1:
        mul24_xi_sym(v)
        mul24_xi_diag(v)
    elif e == 2:
        mul24_xi_diag(v)
        mul24_xi_sym(v)
  

def mul24_y(v, y):
    y1 = gcode_to_vect(y)
    for i in range(24):
        if (y1 >> i) & 1:
            v[i] = -v[i]

def mul24_id(v, _):
    pass

def mul24_t(v, _):
    err = "Operation of triality element not defined on Leech lattice"
    raise ValueError(err)


g_functions = {
   'd':  mul24_id,
   'p':  mul24_perm,
   'x':  mul24_id,
   'y':  mul24_y,
   'l':  mul24_xi,
   't':  mul24_t,
}


def mul24_mmgroup(v, g):
    """Multiply vector in Leech space with an element of the monster

    Here ``v`` should be a numpy array of ``dtype = np.int32`` and 
    ``shape = (24,)``. ``v`` represents an vector in the underlying
    space of the Leech lattice.
   
    ``g`` is an instance of class |MMGroup| representing an element of
    the monster group. Actually, ``g`` should be in the subgroup of
    the monster generated by tags, ``d, p, x, y, z, l``.

    The function computes ``v = v * g`` inplace and returns the 
    modified vector ``v``.
    
    The function may half some entries of vector v. If the result
    in not a vector of integers, the function raises ValueError.

    Caution:
    
    The operation of ``g`` on ``v`` is defined up to sign only!
    """
    v = np.copy(v)
    for tag, a in g.as_tuples():
        g_functions[tag](v, a)
    return v

