r"""This module implements Norton's generators of the Monster.

Norton :cite:`Nor02` has given a presentation of the Monster group
that greatly simplifies a mapping from the *projecive plane*
presentation of the Monster to the representation of the Monster
in :cite:`Gri82` and :cite:`Con85`. Our implemention of the 
Monster is based on the representation in :cite:`Con85`. So we may
use the presentation in :cite:`Nor02` to construct a homomorphism
from the  *projecive plane* represetation of the Monster into our
implementation of the Monster that can be computed in practice.

TODO: Details are yet to be documented!!


"""
import os
import sys
from numbers import Integral
from random import randint, sample, choice

import numpy as np

if not r"." in sys.path:
    sys.path.append(r".")


from mmgroup import XLeech2, Cocode, PLoop, MM
from mmgroup.bitfunctions import bitparity
from mmgroup.clifford12 import xsp2co1_elem_from_mapping

import_done = False

try:
    import inc_p3
    from inc_p3 import incidences
    from inc_p3 import P3_point_set_type
    from inc_p3 import AutP3
    import_done = True
except (ImportError, ModuleNotFoundError):
    # The usual Sphinx and Readthedocs nuisance: We have to survive
    # for the sake of documentation if we could not import this stuff
    print("Warning: could not import module inc_p3")


#####################################################################
# Constructing 'Points' and 'Stars' in the Monster
#####################################################################


precomputation_pending = True

DICT_POINT_MOG = {
    2:13,  6:17,  7:21,  
    8:14, 11:18,  4:22,
   12:15, 10:19,  5:23,  
}

DICT_POINT_MOG_COLUMN = {1:0, 3:4, 9:8}





def make_P(x = 0, delta = 0):
    return XLeech2(PLoop(x), Cocode(delta))
    #return MM([('x', PLoop(x)), ('d', Cocode(delta))])



P0_DICT = {}
def compute_P0(x):
    if x == 0: return MM()
    if x in (1, 3, 9):
        c = DICT_POINT_MOG_COLUMN[x]
        octad = [0, 4, 8, 12, 16, 20, c+1, c+2, c+3]
        return make_P(octad)
    return make_P(0, [DICT_POINT_MOG[x]])


def PointP3(x):
    if precomputation_pending:
        precompute_all()
    assert len(x) & 1 == 0
    p = XLeech2() 
    for x_i in  x:
       p *= P0_DICT[x_i % 13]
    return MM(p)


def ord_PointP3(x):
    if precomputation_pending:
        precompute_all()
    assert len(x) & 1 == 0
    p = XLeech2() 
    for x_i in  x:
       p *= P0_DICT[x_i % 13]
    return p.ord


DICT_LINE_MOG = {
    1:12,  3:16,  9:20,
   12: 1, 11: 5,  7: 9,
    8: 2,  6: 6,  5:10,
    2: 3, 10: 7,  4:11, 
}



PSTAR_DICT = {}

def compute_StarP3(x):
   if x == 0:
      return make_P(~PLoop(), [0,1,2,3])
   if x in (1,3,9):
        return make_P(0,  [1,2,3,4,8, DICT_POINT_MOG_COLUMN[x]])
   lines = [DICT_LINE_MOG[y % 13] for y in incidences(x)]
   octad = [0 ,4 ,8, x] + lines
   point =  DICT_POINT_MOG[x]
   col = point & (-4)
   cocode = [x for x in range(col+1, col+4) if x != point]
   return make_P(octad, cocode)




def StarP3(x):
    if precomputation_pending:
        precompute_all()
    if isinstance(x, Integral):
        return MM(PSTAR_DICT[x % 13])
    p = XLeech2() 
    for x_i in  x:
        p *= PSTAR_DICT[x_i % 13]
    return MM(p) 

def ord_StarP3(x):
    if precomputation_pending:
        precompute_all()
    if isinstance(x, Integral):
        return PSTAR_DICT[x % 13].ord
    p = XLeech2() 
    for x_i in  x:
        p *= PSTAR_DICT[x_i % 13]
    return p.ord 




def precompute_all():
    global precomputation_pending
    global P0_DICT, PSTAR_DICT
    if not import_done:
        err = "Failed to imprt module inc_p3" 
        raise ImportError(err)
    for x in range(13):
        P0_DICT[x] = compute_P0(x)
    for x in range(13):
        PSTAR_DICT[x] = compute_StarP3(x)
    precomputation_pending = False



    

#####################################################################
# Testing the 'Points' and 'Stars' 
#####################################################################
   
    

def test_P_Pstar():
    def not_commuting(a, b):
       return  (a**(-1))**b * a  != MM() 
    
   
    assert StarP3(range(13)) == MM()
    P0_list = [PointP3([0,i]) for i in range(13)]
    Pstar_list = [StarP3(i) for i in range(13)]
    for i, P in enumerate(P0_list):
        if i: assert XLeech2(P).type == 2
        i_bitlist = 1 ^ (1 << i)
        for istar, Pst in enumerate(Pstar_list):
            istar_bitlist = 1 << istar
            ncomm = bitparity(i_bitlist & istar_bitlist)
            assert ncomm == not_commuting(P, Pst), (i, istar, ncomm, P, Pst)

        for P2 in P0_list:
            assert not_commuting(P, P2) == 0

    for i, Pst in enumerate(Pstar_list):
        if i: assert XLeech2(Pst).type == 4, i
        for Pst2 in Pstar_list:
            assert not_commuting(Pst, Pst2) == 0









def test_P_sets(N = 1000, verbose = False):
    types = {}
    star_types = {}
    s ="""Test that the types of the products of the points and of the stars
(as elements of 2**{1+24}) are consistent with the geometry of P3."""
    print(s)
    for i in range(2,13,2):
        for n in range(N):
            s = sample(range(13), i)
            set_type = P3_point_set_type(s)
            type_ = XLeech2(PointP3(s)).type
            if set_type in types:
                 assert types[set_type] == type_
            else:
                 if (verbose): print(set_type, type_)
                 types[set_type] = type_
 

    for i in range(1, 13):
        for n in range(N):
            s = sample(range(13), i)
            set_type = P3_point_set_type(s)
            star_type = XLeech2(StarP3(s)).type
            if set_type in star_types:
                 assert star_types[set_type] == star_type
            else:
                 if verbose: print("*", set_type, star_type)
                 star_types[set_type] = star_type

    print("Test passed")
   

#####################################################################
# class Precomputed_AutP3 
#####################################################################






def MM_from_perm(perm, verbose = 0):
    a_src = np.zeros(24, dtype = np.uint32)
    a_dest = np.zeros(24, dtype = np.uint32)
    a = np.zeros(10, dtype = np.uint32)
    pi0 = perm[0]
    for i in range(12):
       d_src = [0,i+1]
       d_dest = [pi0, perm[i+1]]
       a_src[i] = ord_PointP3(d_src)
       a_src[i + 12] = ord_StarP3(d_src)
       a_dest[i] = ord_PointP3(d_dest)
       a_dest[i + 12] = ord_StarP3(d_dest)
    res = xsp2co1_elem_from_mapping(a_src, a_dest, a)
    if res < 0:
        err = "xsp2co1_elem_from_mapping returns %d"
        raise ValueError(err % res)
    g = MM('a', a[:res & 0xff])
    order = (res >> 8) & 0xff
    special = (res >> 16) & 1
    if verbose and not special:
        print("Ambiguous element of order %d found" % order)
    return g, order, special






class Precomputed_AutP3:
    r"""Auxiliary class for storing images of class ``AutP3`` in class ``MM``

    This class contains class methods only. Its purpose is to compute
    a (fixed) mapping of the automorphism group of the projectve plane
    ``P3`` into the subgroup :math:`G_{x0}` of 
    structure :math:`2^{1+24}.\mabox{Co}_1` of the Monster. Any such
    image computed by method ``as_MM`` of this class is remembered
    for reusing it.
    """
    good_orders = {    # dict of 'good' orders where elements can be
                       # distinguished from their negatives
        1:1, 3:1, 13:1
    }
    bad_orders = {}    # dict of 'bad' orders where elements cannot
                       # be distinguished from their negatives
    known_MM = {}      # Mappings AutP3 |-> MM that will be kept
    transversal = {}   # transversal[(x0,x1)] is (p, pi), such that
                       # p maps (0,1) to (x0, x1) and pi == p**(-1) 
    n_splits = 0       # No of calls to method _split_into_good_orders
    n_split_trials = 0 # No of trials in method _split_into_good_orders


    @classmethod
    def _split_into_good_orders(cls, h):
        cls.n_splits += 1
        while (1):
            h1 = AutP3('r')
            h2 = h1**(-1) * h
            cls.n_split_trials += 1
            if (h1.order() in cls.good_orders  and
                h2.order() in cls.good_orders):
                    return h1, h2
    @classmethod
    def as_MM(cls, h):
        r"""Store an element of AutP3 as an element of the Monster group

        The function maps the instance ``h`` of class ``AutP3`` to an 
        element :math:`g` of the
        subgroup :math:`G_{x0} = 2^{1.24}.\mbox{Co}_1` f the  Monster. 
        It returns the result as an instance of class ``MM``.

        The function remembers all such arrays ``a`` already computed in
        dictionary ``cls.known_MM``.
        """
        if precomputation_pending:
            precompute_all()
        # Compute hash value ``t`` of permutation perm
        t = h.__hash__()
        # Return image of element in ``G_x0`` if found in dictionary
        if t in cls.known_MM:
            return cls.known_MM[t]
        # Let ``order`` be the order of ``h``
        order = h.order()
        # If we know how embed an element of that order into ``G_x0``,
        # then just do so. Store result in dictionary and return it.
        if order in cls.good_orders:
            g, _, _1 = MM_from_perm(h.perm)
            if cls.good_orders[order] == 0:
                g *= MM('x', 0x1000)
            g_data = g.mmdata
            cls.known_MM[t] = g_data
            return g_data 
        # Else decompose ``g`` as a (random) a product ``g = h1 h2``.
        # such that we can deal with elements of the orders of ``h1``
        # and `h2`. Compute the images of ``h1`` and ``h2`` as in the
        # previous case. Store product of these images in dictionary.
        h1, h2 = cls._split_into_good_orders(h)
        g =  MM_from_perm(h1.perm)[0] * MM_from_perm(h2.perm)[0]
        g_data = g.mmdata 
        cls.known_MM[t] = g_data
        # Try to deal with the order of input ``perm``. If we already
        # know that we cannot do so, we simply return the image.
        if order in cls.bad_orders:
            return g_data
        # If we can distinguish the image of ``perm`` from its
        # negative (via character theory) then remember the sign of
        # the character of the correct image for the order of 
        # ``perm``.  If we cannot do so, mark that order as bad.
        g1, _, special = MM_from_perm(h.perm)
        if not special:
            cls.bad_orders[order] = True
        else:
            if g1 == g:
                cls.good_orders[order] = 1       
            else:
                assert g1 == g *  MM('x', 0x1000)
                cls.good_orders[order] = 0
        return g_data       
       

def AutP3_MM(h):    
    r"""Embed  the element ``h`` of AutP3 into the Monster

    The function computes the image of the automorphism ``h`` of the
    projective plane ``P3`` in the Monster group, and returns the
    result as an instance of class ``MM``.

    Parameter ``h`` must be an instance of class ``AutP3``. We use
    a fixed embedding of the automorphsm group of ``P3`` into 
    the Monster.
    """
    # In order to save storage, we split the element into a 
    # product of two factors that are (to be) precomputed. 
    f1, f2 = h._split_transveral()
    # Return (precomputed) product of images of these factors
    data = np.hstack((Precomputed_AutP3.as_MM(f1), 
                 Precomputed_AutP3.as_MM(f2)))
    return MM('a', data)
        
           





#####################################################################
# Test stuff
#####################################################################


def test_construction_P3(ntests = 500, verbose = 0):
    print("Test construction of AutP3")
    for i in range(10):
        #print("Test", i+1)
        p = AutP3('r', zip([0,1,3],[0,1,9]))
        #print(p)

    p = AutP3(zip(range(13,25), range(14,26)))
    #print(p)
    #print(p.order())


    orders = np.zeros(14, dtype = np.uint32)
    AutP3_ONE = AutP3()
    for i in range(ntests):
        if verbose:
            print("Test", i+1)
        p = AutP3('r')
        p1 = AutP3(zip(p.point_map(), range(13)))
        assert p*p1 == AutP3_ONE
        orders[p.order()] += 1
        m = AutP3_MM(p)
    print('  Orders of elements of AutP3 [1,...,13], %d samples:' % ntests)
    print('    %s' % orders[1:])
    print('  Good orders:', Precomputed_AutP3.good_orders)
    print('  Difficult orders:', list(Precomputed_AutP3.bad_orders.keys()))
    print('  %d elements of AutP3 have been split with %d trials.' %
           (Precomputed_AutP3.n_splits, Precomputed_AutP3.n_split_trials))
    print('  Number of stored elements of AutP3:', 
            len(Precomputed_AutP3.known_MM))
    print("Test construction of AutP3 passed")
   



def test_random_relations():
    N = 200
    print("Testing %d random relations in the rep of AutP3 in G_x0" % N)
    for i in range(200):
        g1 = AutP3('r')
        g2 = AutP3('r')
        g3 = g1 * g2
        mg1 = AutP3_MM(g1)
        mg2 = AutP3_MM(g2)
        mg3 = AutP3_MM(g3)
        assert mg3 == mg1 * mg2
    print("Test passed")



#####################################################################
# Norton's generators and relations for the Monster
#####################################################################



def comm(a,b):
    r"""Return commutator of group elements ``a`` and ``b``."""
    return a**(-1) * a**b


def Norton_generators_stuv(check = True):
    r"""Auxiliary function for function ``Norton_generators``"""
    if precomputation_pending:
        precompute_all()
    MM1 = MM()
    # define genertors s, t, u
    s_AutP3 = AutP3(zip([1,2,5,9,8,7], [2,5,9,8,7,1]))
    s = AutP3_MM(s_AutP3)
    t_AutP3 = AutP3(zip([0,12,3,1,2,4], [12,3,0,2,4,1]))
    t = AutP3_MM(t_AutP3)
    u_AutP3 = s_AutP3 * t_AutP3 * s_AutP3**2 * t_AutP3**2
    u = s * t * s**2 * t**2
    v = PointP3(range(1,13))

    if check:
        # A consistency check of generator u, just for fun
        assert u == AutP3_MM(u_AutP3)
        # Check that u acts as  z -> z-1,  as stated in [Nor02]
        assert u_AutP3.point_map() == [12] + list(range(12))

        # Check the relations (1) in [Nor02]
        assert s**6 == t**3 == (s*t)**4 == (s**3 *t)**3 == MM1
        assert comm(s**2, (t * s**2 * t)**2) == MM1

        # Check the relations (2) in [Nor02]
        assert comm(v, u * t**(-1)) == comm(v, u**3 * s * u **(-2)) == MM1
        assert v**2  == comm(v, v**t) == (v*u)**13 == MM1
    return s, t, u, v


# Norton's generator 'x' has the form  MM('t', 1)**EXP_X in our 
# notation, where EXP_X is 1 or 2. We could quickly check the
# relations in these generators for both cases of EXP_X, and we 
# have set EXP_X to the correct value manually.
EXP_X = 1

# List of Norton_generators (if already computed)
NORTON_GENERATORS = None


def Norton_generators(check = False):
    """Return the images of Norton's generators in the Monster

    Norton :cite:`Nor02` defines a presention of the Monster
    with generators :math:`(s,t,u,v,x)` and relations.

    The function returns the images of the presentation of
    these generators in the Monster under a (fixed)
    homomorphism. The result is returned as a quintuple of
    instances of class ``MM``, corresponding to the images of
    these generators in the Monster.

    If parameter ``check`` is ``True`` then we also check the
    relations in this presentation.
    """
    global NORTON_GENERATORS
    if NORTON_GENERATORS and not check:
        return NORTON_GENERATORS
    s, t, u, v = Norton_generators_stuv(check)
    x = MM('t', EXP_X)
    if check:
        MM1 = MM()
        # Check the relations (4) in [Nor02]
        assert comm(v*x, u * t**(-1)) == comm(v*x, s**(u**3)) == MM1

        # Check the relations (5) in [Nor02]
        assert x**3 == (v**u * v * x)**2 == (x**(-1) * x**s)**2 == MM1

        # Check the relations (7) in [Nor02]
        assert (x * (t**-1))**12 == MM1

        # Check the relations (8) in [Nor02]
        assert (x**(u**6) * s)**6 * (s * u * x**(-1) * u**(-1))**6 == s

        # Check the relations (9) in [Nor02]
        assert ((x * v**(u**4) * v**(u**10))**3 * u)**13 == MM1

    NORTON_GENERATORS = s, t, u, v, x
    return NORTON_GENERATORS



#####################################################################
# Test of the module
#####################################################################


def test_all():
    test_P_Pstar()
    test_P_sets()
    test_construction_P3(500)
    test_random_relations()
    generators = Norton_generators(check = True)
    NAMES = "stuvx"
    print("Generators in Norton's construction of the Monster:")
    for name, gen in zip(NAMES, generators):
        print("%s = %s" % (name, gen))


if __name__ == "__main__":
    test_all()


