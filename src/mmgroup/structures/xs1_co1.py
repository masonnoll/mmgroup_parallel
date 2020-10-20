

from __future__ import absolute_import, division, print_function
from __future__ import  unicode_literals

import re
import numpy as np

from mmgroup.structures.auto_group import AbstractGroupWord
from mmgroup.structures.auto_group import AbstractGroup
from mmgroup.structures.parse_atoms import AtomDict, ihex     

from mmgroup.structures.ploop import Cocode, PLoop
from mmgroup.structures.autpl import StdAutPlGroup, AutPL ,autpl_from_obj



from mmgroup.clifford12 import xp2co1_elem_to_qs, xp2co1_qs_to_elem 
from mmgroup.clifford12 import xp2co1_chain_short_3 
from mmgroup.clifford12 import xp2co1_neg_elem
from mmgroup.clifford12 import error_string, chk_qstate12
from mmgroup.clifford12 import xp2co1_unit_elem, xp2co1_elem_delta_pi
from mmgroup.clifford12 import xp2co1_elem_x_delta
from mmgroup.clifford12 import xp2co1_mul_elem
from mmgroup.clifford12 import xp2co1_copy_elem
from mmgroup.clifford12 import xp2co1_reduce_elem
from mmgroup.clifford12 import xp2co1_elem_y

from mmgroup.structures.qs_matrix import QStateMatrix

from mmgroup.mm_group import gen_atom, MMGroupWord

FORMAT_REDUCED = True



py_xi = None


###########################################################################
# Word class for the group G_{x0}
###########################################################################



class Xs12_Co1_Word(AbstractGroupWord):
    """Model an element the subgroup :math:`G_{x0}` of the Monster

    See class ``Xs12_Co1`` for the definition of that group.   

    The constructor of this class returns the neutral element of
    the group :math:`G_{x0}`. 

    :var group:
        This attribute contains the group to which the element belongs.
        That group is an instance of class Xs12_Co1.

    .. warning::
       The constructor of this class is not for public use! You
       may call an instance ``M`` of class Xs12_Co1 for
       constructing elements of the instance ``M`` of the monster 
       group.
  
    """
    MIN_LEN = 16
    __slots__ =  "_data" 
    def __init__(self, atoms = [], **kwds):
        self.group = kwds['group']
        self._data = np.zeros(26, dtype = np.uint64) 
        if len(atoms) ==  0:
            xp2co1_unit_elem(self._data)
            return
        elem = self._data
        while len(atoms):
            tag = atoms[0] >> 28 
            if tag == 1:
                if len(atoms) > 1 and  atoms[1] >> 28  == 2:    
                    xp2co1_elem_delta_pi(elem, atoms[0] & 0xfff,
                        atoms[1] & 0xfffffff)  
                    atoms = atoms[2:]
                else:  
                    xp2co1_elem_delta_pi(elem, atoms[0] & 0xfff, 0)
                    atoms = atoms[1:]
            elif tag == 2:           
                xp2co1_elem_delta_pi(elem, 0, atoms[0] & 0xfffffff) 
                atoms = atoms[1:]                
            elif tag == 3:           
                if len(atoms) > 1 and  atoms[1] >> 28  == 1:    
                    xp2co1_elem_x_delta(elem, atoms[0] & 0x1fff, 
                        atoms[1] & 0xfff)  
                    atoms = atoms[2:]
                else:  
                    xp2co1_elem_x_delta(elem, atoms[0] & 0x1fff, 0)
                    atoms = atoms[1:]
            elif tag == 4:           
                xp2co1_elem_y(elem, atoms[0] & 0x1fff)
                atoms = atoms[1:]
            elif tag == 6:  
                try:
                    1/0
                except:
                    if py_xi is None:
                        create_py_xi(verbose = 0)                     
                    new_elem = py_xi[(atoms[0] & 0xfffffff) % 3]
                    for i in range(26):
                        elem[i] = new_elem._data[i]
                atoms = atoms[1:]
            else:
                raise ValueError("Bad element of group G_{x1}") 
            if not elem is self._data:
                xp2co1_mul_elem(self._data, elem, self._data) 
            elif len(atoms):
                elem = np.zeros(26, dtype = np.uint64)   
                
    @property
    def data(self):
        return list(map(int, self._data))

    @property
    def short3(self):
        return int(self._data[0])

    @property
    def qs(self):
        return QStateMatrix(xp2co1_elem_to_qs(self._data))

        
    def order(self, max_order = 119):
        """Return the order of the element of the monster group


        If the argument ``max_order`` is present then the order of the 
        element is checked up to (and including) ``max_order`` only.  
        Then the function returns ``0`` if the order is greater than 
        ``max_order``. By default, the function returns the exact 
        order of the element.
        """
        raise NotImplementedError
        if check_mm_order is None:
            import_mm_order_functions()
        return check_mm_order(self, max_order)




###########################################################################
# The class representing the group G_x0
###########################################################################



def cocode_to_xs12co1(g, c):
    res =  g.word_type(group = g)
    chk_qstate12(xp2co1_op_delta_pi(res._data, c.cocode, 0))
    return res

def autpl_to_xs12co1(g, aut):
    res =  g.word_type(group = g)
    chk_qstate12(xp2co1_op_delta_pi(res._data, aut.cocode, aut.perm_num))
    return res

def mmgroup_to_xs12co1(g, mm):
    raise NotImplementedError


class Xs12_Co1_Group(AbstractGroup):
    r"""Model the subgroup :math:`G_{x0}` of the Monster
    
    The group :math:`G_{x0}` is the subgroup of the Monster group
    genertated by the elements with tags ``p, d, x, y, l`` in the  
    class |MMGroup| representing the Monster group.  :math:`G_{x0}`
    has structure :math:`2**(1+24).\mbox{Co}_1` in ATLAS
    notation, see :cite:`Con85`, :cite:`Atlas`.
       

    
    :param \*data:

      A variable number of arguments; each argument describes an
      element of the subgroup ``2**(1+24).Co_1`` of the monster.
      These elements are multiplied.  
        

    Depending on its type each parameter in **\*data** is  
    interpreted as follows:

    .. table:: Legal types for constructor of class ``AutPL``
      :widths: 25 75

      ===================== ==================================================
      type                  Evaluates to
      ===================== ==================================================
      tuple (``tag, data``) Create an element of the monster group as 
                            described in class |MMGroup|. Here legal tags
                            are: ``'p', 'd', 'x', 'y', 'z', 'l'``.  The
                            resulting element must lie in the subgroup
                            :math:`G_{x0}` of the monster.
                            
      class |MMGroup|       Create an element of the Monster group. That                
                            element must lie in the subgroup
                            :math:`G_{x0}` of the monster.

      class |AutPL|         Create an element of the subgroup of
                            :math:`G_{x0}` given by class |AutPL|.
                           
      class ``Xs12_Co1``    Create a copy of an element of this class.
                           
      pair (``qstate, x``)  Deprecated and not implemented!!!!!
                            This kind of construction is for testing and
                            not recommended for public use. Here        
                            ``qstate`` must be an instance of class 
                            ``mmgroup.structures.qs_matrix.QStateMatrix``
                            and ``x`` must be an integer representing a
                            short Leech lattice vector modulo 3.
      ===================== ==================================================

        
    :raise:
        * TypeError if ``type(data)`` is not as expected.
        * ValueError if ``data`` cannot be converted to an
          instance of class  `` Xs12_Co1``.
    
    
    """
    __slots__ = "data"
    STD_V3  = 0x8000004
    word_type = Xs12_Co1_Word
    tags, formats = " dpxyl", [None, ihex, str, ihex, ihex, str]
    atom_parser = {}               # see method parse()
    conversions = {
        Cocode: cocode_to_xs12co1,
        AutPL: autpl_to_xs12co1,
        MMGroupWord: mmgroup_to_xs12co1,
    }
    FRAME = re.compile(r"^M?\<(.+)\>$") # see method parse()
    STR_FORMAT = r"M<%s>"

    def __init__(self):
        """ TODO: Yet to be documented     


        """
        super(Xs12_Co1_Group, self).__init__()
        self.atom_parser = AtomDict(self.atom)
        self.set_preimage(StdAutPlGroup,  tuple)


    def atom(self, tag = None, i = "r"):
        return self.word_type(gen_atom(tag, i), group = self)

    def _imul(self, g1, g2):
        chk_qstate12(xp2co1_mul_elem(g1._data, g2._data, g1._data))
        return g1

    def _invert(self, g1):
        w = self.word_type([], group=self)
        chk_qstate12(xp2co1_inv_elem(g1._data, w._data))
        return w

    def copy_word(self, g1):
        w = self.word_type([], group=self)
        chk_qstate12(xp2co1_copy_elem(g1._data, w._data))
        return w

    def reduce(self, g1, copy = False):
        if copy:
            g1 = self.copy_word(g1)
        chk_qstate12(xp2co1_reduce_elem(g1._data))
        return self
       
    def _equal_words(self, g1, g2):
        chk_qstate12(xp2co1_reduce_elem(g1._data))
        chk_qstate12(xp2co1_reduce_elem(g2._data))
        return (g1._data == g2._data).all()

    def _embed_number(self, n):
        w = self.word_type([], group=self)
        if (n == -1):
            xp2co1_neg_elem(w._data)
            n = 1
        if n == 1:
            return w
        raise TypeError("Cannot convert a number to a group element")
        
    def from_qs(self, qs, x):  
        w = self.word_type([], group=self)
        w0 =  xp2co1_qs_to_elem (qs, x)
        for i in range(26):
             w._data[i] =  w0[i]
        return w             

    def str_word(self, v1):
        return "Xs12_Co1 " + str_xs12_co1(v1._data)
 


Xs12_Co1 = Xs12_Co1_Group()




_dict_pm3 = {0: '0', 1:'+', 0x1000000:'-', 0x1000001:'0'}
def str_leech3(x):
    x = int(x)
    lst = [_dict_pm3[(x >> i) & 0x1000001] for i in range(24)]
    return "(" + "".join(lst) + ")"

def str_xs12_co1(data, factor = 1):
    qs0 = xp2co1_elem_to_qs(data)
    qs = QStateMatrix(qs0) / factor
    return str_leech3(data[0]) + " (x) " + str(qs)


try:
    from mmgroup.clifford12 import xp2co1_error_pool
    def get_error_pool(length):
        assert length > 0
        a = np.zeros(length, dtype = np.uint64)
        length = xp2co1_error_pool(a, length)
        return list(map(int, a[:length])) 
except:
    def get_error_pool(length):        
        return []    



def create_py_xi(verbose = 0):
    global py_xi
    from mmgroup.structures.qs_matrix import qs_unit_matrix
    print("create_py_xi")
    py_xi = [ Xs12_Co1()]
    
    xi_sym16 = qs_unit_matrix(12)
    xi_sym16.gate_h(0xf)
    xi_sym16.gate_ctrl_not(0xf, 0xf)
    
    xi_diag16 = -qs_unit_matrix(12)
    for c1, c2 in [(8,7), (4,3), (2,1)]:
        xi_diag16 = xi_diag16.gate_ctrl_phi(c1, c2)
    
    xi_gamma = qs_unit_matrix(12)
    xi_gamma.gate_not(1 << 11)
    xi_gamma.gate_ctrl_not(1 << 10, 1 << 11)
    
    xi_g = qs_unit_matrix(12)
    xi_g.gate_not(1 << 10)
    xi_g.gate_ctrl_not(1 << 11, 1 << 10)
    
    xi_1 = xi_diag16 @ xi_sym16 @ xi_g @ xi_gamma
    xi_2 = xi_sym16 @ xi_diag16 @ xi_gamma @ xi_g
    
    STD_V3  = 0x8000004
    py_xi.append(Xs12_Co1.from_qs(xi_1, STD_V3))   
    py_xi.append(Xs12_Co1.from_qs(xi_2, STD_V3)) 
    if verbose:
        print("Group element 1:\n", py_xi[0])    
        print("Group element xi:\n", py_xi[1])    
        print("Group element xi**2:\n", py_xi[2])    
        
    
   