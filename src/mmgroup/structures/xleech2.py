r"""We deal with an extraspecial group that maps to the Leech lattice mod 2

Let :math:`Q_{x0}` be the group generated by elements :math:`x_d, x_\delta`
with :math:`d \in \mathcal{P}, \delta \in \mathcal{C}^*`. Here 
:math:`\mathcal{P}` is the Parker loop and :math:`\mathcal{C}^*` is the
Golay cocode as in :cite:`Con85`. We take the following relations in
:math:`Q_x` from and :cite:`Seysen20`:


.. math::

    x_d x_e = x_{d \cdot e} x_{A(d,e)}, \,
    x_\delta x_\epsilon = x_{\delta \epsilon}, \,
    [x_d x_\delta] = x_{-1}^{\langle d, \delta \rangle}, \,
    d, e \in \mathcal{P},
    \delta , \epsilon \in \mathcal{C}^* \, .

Here :math:`A(d,e)` is the associator between :math:`d` and :math:`e`,
i.e. the element of :math:`\mathcal{C}^*` corresponding to the vector 
:math:`d \cap e`. :math:`[.,.]` is the commutator in :math:`Q_{x0}`.
Then :math:`Q_{x0}` is an extraspecal group of structure 
:math:`2_+^{1+24}`.

An element of the group :math:`Q_x` is modelled as an instance of
class |XLeech2|.

In that class we encode the element 
:math:`x_d \cdot x_\delta` of :math:`Q_{x0}` as an integer 
:math:`x`  as follows:

.. math::

       x = 2^{12} \cdot d \oplus (\delta \oplus \theta(d)) \, .

Here elements of the Parker loop and elements of the cocode 
are encoded as integers as in section :ref:`parker-loop-label`
and :ref:`golay-label`.
:math:`\theta` is the cocycle given in section 
:ref:`basis-golay-label`, and ':math:`\oplus`' means bitwise
addition modulo 2. Note that a  Parker loop element is 13 bits 
long (with the most significant bit denoting the sign) and that 
a cocode element is 12 bits long.

There is a natural homomorphism from :math:`Q_{x0}` to the 
Leech lattice :math:`\Lambda` modulo 2 with kernel 
:math:`\{x_1, x_{-1}\}`, as described in  :cite:`Con85`. This 
homomorphism maps the group operation in  :math:`Q_{x0}`
to vector addition in :math:`\Lambda / 2\Lambda`. With our
numbering in :math:`Q_{x0}` that homomorphism can be realized
by simply dropping the sign bit 25; then vector addition in
:math:`\Lambda / 2\Lambda` corresponds to the :math:`\oplus`
operation on such numbers. The natural quadratic form on
the vector  in :math:`\Lambda / 2\Lambda` with the number
:math:`2^{12} \cdot d + \delta`, :math:`0 \leq d, \delta < 2^{12}`
is the parity of the bit vector :math:`d \oplus \delta`.



"""




from functools import reduce
from operator import __xor__
from numbers import Integral, Number
from random import randint

try:
    # Try importing the fast C function
    from mmgroup import mat24 
except (ImportError, ModuleNotFoundError):
    # Use the slow python function if the C function is not available
    from mmgroup.dev.mat24.mat24_ref import  Mat24
    mat24 = Mat24


from mmgroup.mm import mm_aux_index_sparse_to_leech2
from mmgroup.mm import mm_aux_index_extern_to_sparse


from mmgroup.structures.abstract_group import AbstractGroupWord
from mmgroup.structures.abstract_group import AbstractGroup
from mmgroup.structures.abstract_mm_group import AbstractMMGroupWord
from mmgroup.structures.parity import Parity
from mmgroup.structures.parse_atoms import ihex
from mmgroup.structures.mm_space_indices import tuple_to_sparse


from mmgroup.structures.gcode import GCode, GcVector
from mmgroup.structures.ploop import PLoop
from mmgroup.structures.cocode import Cocode
from mmgroup.structures.autpl import AutPL, AutPlGroup

from mmgroup.generators import gen_xi_mul_leech
from mmgroup.generators import gen_xi_pow_leech
from mmgroup.generators import gen_xi_scalprod_leech
from mmgroup.generators import rand_get_seed, gen_leech2_type

ERR_RAND = "Illegal string for constricting type %s element" 

ERR_DIV4 = "%s object may be divided by 2 or 4 only"
ERR_DIV2 = "%s object may be divided by 2 only"


#######################################################################
# Import derived classed
#######################################################################

import_pending = True

def complete_import():
    """Internal function of this module

    If you need any of the objects declared above, do the following:

    if import_pending:
        complete_import()
    """
    global import_pending, SubOctad
    from mmgroup.structures.suboctad import SubOctad
    import_pending = False



###########################################################################
# Import functions from module ``mmgroup.mm_order`` on demand
###########################################################################


# Functions to be imported from module mmgroup.mm_order
check_mm_in_g_x0 = None

def import_mm_order_functions():
    """Import functions from module ``mmgroup.mm_order``.

    We import these functions from module ``mmgroup.mm_order``
    on demand. This avoids an infinite recursion of imports.
    """
    global check_mm_in_g_x0
    from mmgroup.mm_order import check_mm_in_g_x0 as f
    check_mm_in_g_x0 = f



#######################################################################
# Auxiliary functions
#######################################################################


ERR_XL_TUPLE = "Cannot convert tuple to XLeech2 object"

ERR_XL_IN_Q = "Monster group element is not in subgroup Q_x0"

ERR_XL_TYPE = "Cannot convert '%s' object to XLeech2 object"

ERR_XL_RAND = "No random object in class XLeech2 found"


def MM_to_Q_x0(g):
    if check_mm_in_g_x0 is None:
        import_mm_order_functions()
    g = MM0('a', g.mmdata)
    if check_mm_in_g_x0(g) is None:
        raise ValueError(ERR_XL_IN_Q)
    g.reduce()
    res = 0;
    for atom in g.mmdata:
        tag = (atom >> 28) & 0x0f
        if res == 0 and tag == 3:
            res = ((atom & 0x1fff) << 12) ^ ploop_theta(atom)
        elif tag == 1:
            res ^= atom & 0xfff
        elif tag:
            raise ValueError(ERR_XL_IN_Q)
    return res


def rand_xleech2_type(vtype):
    if vtype in [3,4]:
        for i in range(1000):
            v = randint(0, 0x1ffffff)
            if gen_leech2_type(v) >> 4 == vtype:
                 return v
        raise ValueError(ERR_XL_RAND)
    if vtype == 0:
        return 0
    if vtype == 2:
        ve = randint(300, 98579)
        vs = mm_aux_index_extern_to_sparse(ve)
        sign = randint(0,1)
        return mm_aux_index_sparse_to_leech2(vs) ^ (sign << 24) 
    raise ValueError(ERR_XL_RAND)


def value_from_ploop(ploop=0, cocode = None, *args):
    c = Cocode(cocode) if cocode else 0
    if isinstance(ploop, Integral):
        d = ploop 
    elif isinstance(ploop, PLoop):
        d = ploop.value & 0x1fff
        d = (d << 12) ^ mat24.ploop_theta(d) 
    elif isinstance(ploop, XLeech2):
        d = ploop.value
    elif isinstance(ploop, SubOctad):
        g = ploop.gcode
        d = (g << 12) ^ mat24.ploop_theta(g) 
        d ^= ploop.sign_ << 24
        d ^= ploop.cocode
    elif isinstance(ploop, Cocode):
        d = ploop.value
    elif isinstance(ploop, AbstractMMGroupWord):
        d = MM_to_Q_x0(g)
    elif isinstance(ploop, str):
        if len(ploop) == 1 and ploop in "BCTXES":
            d = 0
            a = tuple_to_sparse(0xff,  ploop, cocode, *args)
            if len(a) == 1:
                a0 = a[0]
                d = mm_aux_index_sparse_to_leech2(a0)
                a0 &= 0xff
                if a0 == 0xfe:
                    d ^= 0x1000000
                elif a0 != 1:
                    d = 0
            if d:
                return d
        if ploop == "r":
             if cocode is None:
                 return randint(0, 0x1ffffff)
             elif cocode in [0,2,3,4]:
                 return  rand_xleech2_type(cocode)
        raise ValueError(ERR_XL_TUPLE)            
    else:
        return TypeError(ERR_XL_TYPE % type(ploop))
    return d ^ c

        

#######################################################################
# Class XLeech2
#######################################################################





class XLeech2(AbstractGroupWord):
    r"""This class models an element of the group :math:`Q_x0`.

    The group :math:`Q_x0` is an extraspecial 2 group of structure 
    :math:`2^{1+24}`. 
    
    TODO: documentation yet to be updated!!!

    The group operation is written multiplicatively. 
        
    The :math:`2^{1+24}` group elements are numbered from
    ``0`` to ``0x1ffffff``. Elements ``0`` to ``0xffffff`` are
    considered positive. The element with number  ``0x1000000 ^ i`` 
    is the negative of the element with number  ``i``.

    An element is constructed as a product :math:`x_d x_\delta`,
    where :math:`d` is in the Parker loop and :math:`\delta` is in
    the Golay cocode.

    :param ploop:

      This parameter describes the value `d` of the Parker loop 
      element  :math:`x_d`. 

    :param cocode:

      This parameter describes the value `\delta` of the Parker loop 
      element  :math:`x_\delta`. 

    :return: A Parker loop element
    :rtype:  an instance of class |PLoop|

    :raise:
        * ValueError if the input cannot converted to an element of
          the group :math:`Q_{x0}`.
        * TypeError the ype of an input is illegal.


    Depending on its type parameter **value** is  interpreted as follows:

    .. table:: Legal types for constructor of class ``XLeech2``
      :widths: 20 80

      ===================== ================================================
      type                  Evaluates to
      ===================== ================================================
      ``int``               Here the code word with number ``value`` is
                            returned.  ``0 <= value < 0x2000000`` must hold.
                              
      class |XLeech2|       A deep copy of the object **value**
                            is created. 

      class |GCode|         The corresponding Golay code element is
                            converted to a (positive) element of
                            :math:`Q_{x0}`. 

      class |PLoop|         The corresponding Parker loop element is
                            converted to an element of :math:`Q_{x0}`. 

      class |SubOctad|      The |SubOctad| is
                            converted to an element of :math:`Q_{x0}`. 

      ``str``               Create random element depending on the string
                             | ``'r'``: Create arbitrary Parker loop element

      ===================== ================================================



    **Standard operations**

    Let ``q`` be an instance of this class. The multiplication operator 
    ``*`` implements the group operation. Division by an element means
    multiplication by its inverse, and exponentiation means repeated 
    multiplication,  with ``q**(-1)`` the inverse of  ``q``,  as usual. 

    Multiplication with the integer ``1`` or ``-1`` means the 
    multiplication with the neutral element or with the central 
    involution :math:`x_{-1}`.
     
    The opration  ``&`` denotes the scalar product of the vectors
    in the Leech lattice mod 2 obtained from an instance of this
    class, ignoring the sign.

    **Standard functions**
  
    ``abs(a)`` returns the element in the set ``{a, -a}`` which is
    positive.

    .. Caution::
       Although the group  :math:`Q_{x0}` has a natural embedding
       into the subgroup :math:`G_{x0}` of the monster group, we do 
       not consider an instance :math:`q` of class |XLeech2| as an 
       element of :math:`G_{x0}`. We consider :math:`q` as a (possibly
       negated) basis vector of a space on which :math:`G_{x0}` acts
       monomially by right multiplication.

    If an instance :math:`q` of class |XLeech2| maps to a vector of 
    type 2 in the Leech lattice mod 2 then :math:`q` is also a unit 
    vector in the 196884-dimensional representation :math:`\rho` of 
    the monster group.

    One may use :math:`q` in the constructor of class |MM|
    (representing the monster group) for creating the corresponding
    element of the subgroup :math:`Q_{x0}` of the monster group.


    """
    __slots__ = "value",
 
    def __init__(self, ploop = 0, cocode = 0, *args):
        if import_pending:
            complete_import()
        self.value = value_from_ploop(ploop, cocode, *args)


    def __mul__(self, other):
        if isinstance(other, XLeech2):
            return XLeech2(gen_xi_mul_leech(self.value, other.value))
        elif isinstance(other, AbstractMMGroupWord):
            data = other.data
            v = gen_leech2_op_word(self.value, data, len(data))
            return XLeech2(v)
        elif isinstance(other, Integral):
            if abs(other) == 1:
                return XLeech2(self.value ^ ((other & 2) << 23))
            elif other == 0:
                 return XLeech2(0)
            return NotImplemented
        else:           
            return NotImplemented

    def __imul__(self, other):
        self.value = self.__mul__(other).value
        return self

    def __rmul__(self, other):
        if isinstance(other, XLeech2):
            return XLeech2(gen_xi_mul_leech(other.value, self.value))
        elif isinstance(other, Integral):
            if abs(other) == 1:
                return XLeech2(self.value ^ ((other & 2) << 23))
            elif other == 0:
                 return XLeech2(0)
            return NotImplemented
        else:           
            return NotImplemented

    def __abs__(self):
        return  XLeech2(self.value & 0xffffff)

    def __pos__(self):
        return  self

    def __neg__(self):
        return  XLeech2(self.value ^ 0x1000000)

    def __pow__(self, other):
        if isinstance(other, Integral):            
            return XLeech2(gen_xi_pow_leech(self.value, other & 3))
        elif isinstance(other, XLeech2):
            ov = other.value
            v = self.value
            w = gen_xi_mul_leech(gen_xi_pow_leech(ov, 3), v)
            w = gen_xi_mul_leech(w, ov)
            return XLeech2(w)
        else:
            return NotImplemented
        
    def __truediv__(self, other):
        if isinstance(other, XLeech2):
            v = gen_xi_pow_leech(other.value, 3)
            return XLeech2(gen_xi_mul_leech(self.value, other.value))
        elif isinstance(other, Integral):
            if abs(other) == 1:
                v = (other & 2) << 23
            else:
                NotImplemented  
        else:           
            return NotImplemented
        return XLeech2(gen_xi_mul_leech(self.value, v))

    def __itruediv__(self, other):
        self.value = self.__itruediv__(other).value
        return self


                             
    def __rtruediv__(self, other):
        v = gen_xi_pow_leech(other.value, 3)
        if isinstance(other, XLeech2):
            return XLeech2(gen_xi_mul_leech(other.value, v))
        elif isinstance(other, Integral):
            if abs(other) == 1:
                return XLeech2(v ^ ((other & 2) << 23))
            elif other == 0:
                 return XLeech2(0)
            return NotImplemented
        else:           
            return NotImplemented
 
       
    def __and__(self, other):
        if isinstance(other, XLeech2):
            ov = other
        elif isinstance(other, (GCode, PLoop)):
            d = other.value & 0xfff
            ov = (d << 12) ^ mat24.ploop_theta(d) 
        elif isinstance(ploop, Cocode):
            ov = ploop.value & 0xfff
        else:
            return NotImplemented
        return gen_xi_scalprod_leech(self.value, ov)


    __rand__ = __and__

    def __eq__(self, other):
        return (isinstance(other, XLeech2)  
            and (self.value ^ other.value) & 0x1ffffff == 0)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __pos__(self):
        return self
        
    def __neg__(self):
        return  PLoop(self.value ^ 0x1000000)


    @property
    def ord(self):
        """Return the number of the Parker loop element.

        We have ``0 <= i < 0x2000000`` for the returned number ``i``.
        """
        return self.value & 0x1ffffff


    @property
    def sign(self):
        """Return the sign of the Parker loop element.

        This is ``1`` for a positive and ``-1`` for a negative element.
        """
        return 1 - ((self.value >> 23) & 2)


    def split(self):
        """Yet to be documented!!!!

        """
        v = self.value
        x = (v >> 12) & 0x1fff
        d = (mat24.ploop_theta(v >> 12) ^ v) & 0xfff
        return PLoop(x), Cocode(d)
 
     
    def str(self):
        v = self.value
        x = (v >> 12) & 0x1fff
        d = (mat24.ploop_theta(v >> 12) ^ v) & 0xfff
        return "XL2<x_%s*d_%s>" % (ihex(x, 3), ihex(d, 3))
    __repr__  = str


    
    @property
    def type(self):
        return gen_leech2_type(self.value) >> 4

    @property
    def xtype(self):
        return gen_leech2_type(self.value)

    @property
    def subtype(self):
        t =  gen_leech2_type(self.value)
        return t >> 4, t & 15


