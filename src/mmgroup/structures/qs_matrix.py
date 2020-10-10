

from __future__ import absolute_import, division, print_function
from __future__ import  unicode_literals


import re
from collections.abc import Iterable
from numbers import Integral, Complex
import math
from random import randint

import numpy as np
from mmgroup.clifford12 import QState12 
from mmgroup.clifford12 import qstate12_unit_matrix 
from mmgroup.clifford12 import qstate12_column_monomial_matrix
from mmgroup.clifford12 import qstate12_row_monomial_matrix
from mmgroup.clifford12 import qstate12_pauli_matrix
from mmgroup.clifford12 import error_string
from mmgroup.clifford12 import qstate12_pauli_vector_mul
from mmgroup.clifford12 import qstate12_pauli_vector_exp


FORMAT_REDUCED = True

class QStateMatrix(QState12):
    r"""This class models a quadratic state matrix
       
    Quadratic state matrices are described in the *guide* at

    https://mmgroup.readthedocs.io/en/latest/guide.html#module-mmgroup.dev.clifford12.qstate12  .   
    
    :param rows:
    
        * Binary logarithm of the number of rows of the matrix
 
        * or an instance of class ``QStateMatrix``. Then a deep copy
          of that instance is created.
    
    :type rows: 
    
        ``int`` or and instance of class ``QStateMatrix``
    
    :param cols:
    
        Binary logarithm of the number of columns of the matrix
    
    :type cols: 
    
        A nonnegative ``int``, if parameter ``rows`` is an ``int``
    
    :param data:
    
        The data of the matrix as described below
        
    :param mode:
    
        Evaluated according as described below
        
    :raise:
        * TypeError if ``type(data)`` is not as expected.
        * ValueError if ``data`` cannot be converted to an
          instance of class  ``QStateMatrix``.
    
    
    In terms of the theory of quantum computing, ``rows, cols = 0, n`` 
    creates a column vector or a *-ket* ``|v>`` corresponding to a 
    state of of ``n`` qubits, and ``rows, cols = n, 0`` creates a 
    row vector or a *-bra* ``<v|`` corresponding to a linear function
    on a state of ``n`` qubits.

    If ``rows == cols == n`` and the created ``2**n`` times ``2**n``
    matrix is invertible, then the matrix is (a scalar multiple of) 
    an element of the complex Clifford :math:`\mathcal{X}_{12}` of 
    ``n`` qubits described in :cite:`NRS01`.

    If ``rows`` is an instance of this class then a copy of 
    that instance is created.

    If ``rows`` and ``cols`` are integers then ``data``  may be:

      * ``None`` (default). Then the zero matrix is created.

      * A list of integers. Then that list of integers must encode 
        a valid pair ``(A, Q)`` of bit matrices that make up a 
        state, as dscribed in the *guide*. 
        In this case parameter ``mode`` is evaluated as follows:
              
          * 1: create matrix ``Q`` from lower triangular part
              
          * 2: create matrix ``Q`` from upper triangular part
               
          * Anything else: matrix ``Q`` must be symmetric.

      * An integer ``v``. Then one of the values ``rows`` and 
        ``cols`` must be zero and the unit (row or column) 
        vector with index ``v`` is created. Here a row vector
        is an ``1`` times ``2**cols`` and a column vector is a
        ``2**rows`` times ``1`` matrix.  
          
    As in ``numpy``, matrix multiplication of quadratic state 
    matrices is done with the ``@`` operator and elementwise
    multiplication of such matrices is done with the ``*``
    operator. A quadratic state matrix may also be multiplied 
    by a scalar. Here the scalar must be zero or of the form:

    .. math::
        2^{e/2} \cdot w \, , \quad  e \in \mathbb{Z}, \;
        w \in \mathbb{C}, \, w^8 = 1   \; .
   
    A matrix of type ``QStateMatrix`` may be indexed with square
    brackets as in ``numpy`` in order to obtain entries, rows, 
    columns or submatrices. Then a complex ``numpy`` array (or a 
    complex number) is returned as in ``numpy``. It is  not 
    possible to change the matrix via item assignment. So the 
    easiest way to obtain a complex version of an instance ``qs`` 
    of type ``QStateMatrix`` is to write ``qs[:,:]``.
    
    A row or coulumn index has a natural interpretation as a
    bit vector. In the theory of quantum computation a bit of
    such a bit vector corresponds to a *qubit*. Let ``qs`` be
    a quadratic state matrix of shape ``(m, n)`` and 
    
    .. math::
        x = \sum_{k=0}^{m-1} 2^k x_k, \; y = \sum_{k=0}^{n-1} 2^k y_k, 
        \, x_k, y_k \in \{0, 1 \}.
        
    Then ``qs[x,y]`` is the entry of matrix ``qs`` with row index 
    corresponding to the bit vector :math:`(x_{m-1},\ldots,x_0)` 
    and column index corresponding to the bit vector 
    :math:`(y_{n-1},\ldots,y_0)`.     
    
    Officially, we support matrices with ``rows, cols <= 12``
    only. Methods of this class might work for slightly 
    larger matrices. Any attempt to constuct a too large
    matrix raises ValueError.
    """
    UNDEF_ROW = 255

    #########################################################################
    # Constructors
    
    def __init__(self, rows, cols = None, data = None, mode = 0):
        super(QStateMatrix, self).__init__(rows, cols, data, mode)

    #########################################################################
    # Elementary operations
        
    def conjugate(self):
        """Compute complex conjugate of the matrix
        
        :return: instance of class ``QStateMatrix``.
        """
        m = QStateMatrix(self) 
        return super(QStateMatrix, m).conjugate()   

    conj = conjugate        

    @property 
    def T(self):
        """Return transposed matrix as in numpy"""   
        return self.copy().transpose()

    @property 
    def H(self):
        """Return conjugate transposed matrix as in numpy"""   
        m = self.copy().transpose()
        return super(QStateMatrix, m).conjugate()    
     
    @property 
    def shape(self):
        """Get shape of the complex matrix represented by the state 
        
        The function returns a pair ``(rows, cols)`` meaning
        that the state corresponds to a complex
        ``2**nrows`` times ``2**ncols`` matrix.         
        """
        return super(QStateMatrix, self).shape


    def copy(self):
        """Return a deep copy of the matrix"""
        return self.__class__(self)
            
    #########################################################################
    # Reshaping a state matrix

    def reshape(self, new_shape, copy = True):
        r"""Reshape matrix to given shape
                        
        :param new_shape:
    
            This shape of the reshaped matrix. It must be a pair of
            integers. A pair ``(n0, n1)`` correponds to a complex
            ``2**n0`` times ``2**n1`` matrix.            
    
        :type new_shape: 
        
            tuple of two integers
    
        :param copy:
        
            A deep copy of the reshaped  matrix is returned if   
            ``copy`` is True (default). Otherwise the matrix is
            reshaped in place.
            
        :type copy: ``bool``
    

        ``new_shape[0] + new_shape[1] = self.shape[0] + self.shape[0]`` 
        must hold.

        If one of the values ``new_shape[0]``, ``new_shape[1]``  
        is ``-1`` then the other value is calculated from the sum 
        ``self.shape[0] + self.shape[1]``. 
        """  
        c = self.copy() if copy else self
        super(QStateMatrix, c).reshape(*new_shape)  
        return c

    #########################################################################
    # Permuting the qubits of the state matrix

       
    def rot_bits(self, rot, nrot, start = 0):    
        r"""Rotate qubit indices of the state matrix ``qs`` in place

        If the state matrix ``qs`` has shape ``(0,n)`` or ``(n,0)`` 
        we rotate  the qubits of ``qs`` in place as follows:
        
        For ``n0 <= i < n0 + nrot``  we map qubit ``i`` to qubit  
        ``n0 + (i + rot) % nrot``. E.g. ``nrot = 3, rot = 1, n0 = 0``
        means qubits are mapped as ``0->1, 1->2, 2->0``.

        Here the entries of the state matrix are labelled by bit 
        vectors of length ``n``. Let ``qs(x[0],...,x[n-1])`` be the 
        entry of the state matrix corresponding to the bit vector
        ``(x[n-1],...,x[0])``.
                
        Then the function changes ``qs to qs'`` with
        ``qs'(...,x[start+nrot],y[nrot-1],...,y[0],x[start-1],...)`` =
        ``qs(...,x[start+nrot],z[nrot-1],...,z[0],x[start-1],...)``,
        where ``z[j] = y[j - rot (mod 3)]``.

        If the state matrix ``qs`` has shape ``(n0, n1)`` then we
        label the entries of state matrix by bit vectors of 
        length ``n0 + n1``, with the ``n1`` highest bits corresponding 
        to  the rows of the matrix, and the ``n0`` lowest bits 
        corresponding to the columns of the matrix.
        """
        return super(QStateMatrix, self).rot_bits(rot, nrot, start)   
        
    def xch_bits(self, sh, mask):    
        r"""Exchange qubit arguments the state  ``qs`` in place

        We label the entries of the state matrix ``qs`` by bit vectors
        and define ``qs(x[n-1],...,x[0])``, with  ``n = n0 + n1``, 
        ``(n0, n1) = qs.shape`` as in method ``rot_bits``.
        
        We exchange qubit ``j`` with argument qubit ``j + sh``
        of the state, if bit ``j`` of ``mask`` is set. If bit ``j``
        of ``mask`` is set then bit ``j + sh`` of ``mask`` must not 
        be set. No ``mask`` bit at  position >= ``n - sh``
        may be set.
        
        E.g.  ``qs.qstate12_xch_bits(1, 0x11)`` changes the 
        state matrix ``qs``  to a state matrix ``qs'``  with
        ``qs'(...,x6,x5,x4,x3,x2,x1,x0.)``  =
        ``qs(...,x6,x4,x5,x3,x2,x0,x1)``.
        """
        return super(QStateMatrix, self).xch_bits(sh, mask)   
   
 
    #########################################################################
    # Applying qubit gates

    def gate_not(self,v):
        r"""Apply not gates to a state
        

        Change the state ``qs``  to a state ``qs'`` with
        ``qs'(x) = qs(x (+) v)``, where ``'(+)'`` is the bitwise 
        xor operation.
        The result is reduced if the input is reduced.
        Computing ``qs.gate_not(1 << j)`` corresponds to
        negating qubit ``j``.
        """
        return super(QStateMatrix, self).gate_not(v)

    def gate_ctrl_not(self, vc, v):
        r"""Apply controlled not gates to a state
               
        Change the state ``qs`` to a state ``qs'``
        with ``qs'(x) = qs(x (+) <vc,x> * v)``  where ``'(+)'`` is 
        the bitwise  xor operation, and ``<.,.>`` is the scalar 
        product of bit vectors.  The result is not reduced. The 
        scalar product of the bit vectors ``j`` and ``jc`` must
        be zero. Otherwise the ``ctrl not`` operation is not
        unitary.
        
        Computing ``qs.gate_ctrl_not(1 << jc, 1 << j)``, 
        for ``jc != j``, corresponds to applying a controlled not  
        gate  to qubit ``j``  contolled by qubit ``jc``. 
        This operation is unitary if and only if the scalar
        product of ``j`` and ``jc`` is zero.
        """
        return super(QStateMatrix, self).gate_ctrl_not(vc, v)

    def gate_phi(self, v, phi):
        r"""Apply phase gate to a state
               
        Change the state ``qs``  to a state ``qs'``
        with ``qs'(x) = qs(x) * sqrt(-1)**(phi * <v,x>)``, where
        ``<.,.>`` is the scalar product of bit vectors and ``'**'`` 
        denotes exponentiation.
        The result is reduced if the input is reduced.
        Computing ``qs.gate_phi(1 << j, phi)`` 
        corresponds to applying a  phase ``(phi * pi/2)``  gate 
        to qubit ``j``. 
        """
        return super(QStateMatrix, self).gate_phi(v, phi)

    def gate_ctrl_phi(self, v1, v2):
        r"""Apply controlled phase gates to a state
               
        Change the state ``qs`` to a state ``qs'``
        with ``qs'(x) = qs(x) * (-1)**(<v1,x>*<v2,x>)``, where 
        ``<.,.>``  is the scalar product of bit vectors and ``'**'``
        denotes exponentiation.
        The result is reduced if the input is reduced.
        Computing ``qs.gate_ctrl_phi(1 << j1, 1 << j2)``
        corresponds to applying a  phase ``pi`` gate to 
        qubit ``j2`` controlled by qubit ``j1``. 
        """
        return super(QStateMatrix, self).gate_ctrl_phi(v1, v2)

    def gate_h(self, v):
        r"""Apply Hadamard gates to a state
            
        Apply a Hadamard gate to all qubits ``j`` of the state ``qs``
        (referred by ``self``) with  ``v & (1 << j) == 1``.
        Aplying a Hadamard gate to gate ``j`` changes a state ``qs``
        to a state ``1/sqrt(2) * qs'``, where
        ``qs'(..,x[j+1],x_j,x[j-1],..)`` = 
        ``qs(..,x[j+1],0,x[j-1],..)``
        + ``(-1)**(x_j) * qs(..,x[j+1],1,x[j-1],..)`` .
        The result is not reduced.
        """
        return super(QStateMatrix, self).gate_h(v)


    #########################################################################
    # Extending and restricting a state
       
    def extend_zero(self, j, nqb, copy = True):    
        r"""Insert ``nqb`` zero qubits at position ``j``. 
         
        Let ``qs`` be the state of shape ``(n0+n1)``, and let 
        ``n = n0 + n1`. We change ``qs`` to the following 
        state ``qs'`` depending on ``n + nqb`` qubits:
        
        ``qs'(x[n-1],...,x[j],y[nqb-1],...,y[0],x[j-1]...,x[0])`` 
        is equal to ``qs(x[n-1],...,x[j],x[j-1]...,x[0])`` if
        ``y[0] = ... = y[nqb-1] = 0`` and equal to zero otherwise.
                
        The function returns *ket*, i.e. a column vector
        of shape ``(n + nqb, 0)``. 
        
        If the input is reduced then the result is also reduced.
        
        If parameter ``copy`` is True (default) then a copy
        of the matrix is modified and returned.
        """
        m = QStateMatrix(self) if copy else self
        super(QStateMatrix, m).extend_zero(j, nqb) 
        return m   

    def extend(self, j,nqb, copy = True):    
        r"""Insert ``nqb`` qubits at position ``j``. . 
              
        Let ``qs`` be the state of shape ``(n0+n1)``, and let 
        ``n = n0 + n1`. We change ``qs`` to the following 
        state ``qs'`` depending on ``n + nqb`` qubits:
        
        ``qs'(x[n-1],...,x[j],y[nqb-1],...,y[0],x[j-1]...,x[0])`` 
        = ``qs(x[n-1],...,x[j],x[j-1]...,x[0])`` .
        
        The function returns *ket*, i.e. a column vector
        of shape ``(n + nqb, 0)``. 
        
        If the input is reduced then the result is also reduced.
        
        If parameter ``copy`` is True (default) then a copy
        of the matrix is modified and returned.
        """
        m = QStateMatrix(self) if copy else self
        super(QStateMatrix, m).extend(j, nqb) 
        return m   


    def restrict_zero(self, j, nqb, copy = True):    
        r"""Restrict ``nqb`` qubits starting at postion ``j`` to ``0``.
               
        Let ``qs`` be the state of shape ``(n0+n1)``, and let 
        ``n = n0 + n1`. We change ``qs`` to the following 
        state ``qs'`` depending on ``n`` qubits:
       
        ``qs'(x[n-1],...,x[0]) is equal to qs(x[n-1],...,x[0])`` if 
        ``x[j] = ... = x[j+nqb-1] = 0`` and equal to zero otherwise.
        We do not change the shape of ``qs``.
        
        The output is reduced if the input is reduced.
        
        If parameter ``copy`` is True (default) then a copy
        of the matrix is modified and returned.
        """
        m = QStateMatrix(self) if copy else self
        super(QStateMatrix, m).restrict_zero(j, nqb) 
        return m   

    def restrict(self, j,nqb, copy = True):    
        r"""This is method ``restrict_zero`` with deletion.
        
        Let ``qs`` be the state of shape ``(n0+n1)``, and let 
        ``n = n0 + n1`. We change ``qs`` to the following 
        state ``qs'`` depending on ``n - nqv`` qubits:

        ``qs'(x[n'-1],...,x[0])`` is equal to 
        ``qs(x[n'-1],...,x[j],0,...,0,x[-1],...,x[0])``.
        
        The function returns *ket*, i.e. a column vector
        of shape ``(n - nqb, 0)``. 
        
        If the input is reduced then the result is also reduced.
        
        If parameter ``copy`` is True (default) then a copy
        of the matrix is modified and returned.
        """
        m = QStateMatrix(self) if copy else self
        super(QStateMatrix, m).restrict(j, nqb) 
        return m   

    def sumup(self, j,nqb, copy = True):    
        r"""Sum up ``nqb`` qubits  starting at position ``j``. 
        
        Let ``qs`` be the state of shape ``(n0+n1)``, and let 
        ``n = n0 + n1``. We change ``qs`` to the following 
        state ``qs'`` depending on ``n - nqb`` qubits:
        
        ``qs'(x[n-1],...,x[j+nqb],x[j-1],...,x[0])`` =
        ``sum_{x[j+nqb-1],...,x[j]}  qs1(x[nn1-1],...,x[0])`` .
        
        The function returns *ket*, i.e. a column vector
        of shape ``(n - nqb, 0)``. 
        
        If the input is reduced then the result is also reduced.
        
        If parameter ``copy`` is True (default) then a copy
        of the matrix is modified and returned.
        """
        m = QStateMatrix(self) if copy else self
        super(QStateMatrix, m).sumup(j, nqb) 
        return m   

    #########################################################################
    # Matrix operations
       
    def lb_norm2(self):    
        r"""Return binary logarithm of squared operator norm.
        
        The operator norm is the largest absolute singular value
        of the matrix.
        
        Return -1 if the matrix is zero.
        """
        m = self.copy().reduce()
        if m.nrows == 0:
            return -1
        return m.factor[0] + m.nrows - 1 - m.lb_rank() 

    def inv(self):
        r"""Return inverse matrix
     
        Returns an instance of class ``QStateMatrix``.
        Raise ValueError if matrix is not invertible.
        """
        return self.copy()._mat_inv()

    def power(self, e):
        """Return the ``e``-th power of the matrix
        
        For a matrix ``m`` the power with exponent
        ``e = 2``  is ``m @ m``, and the power with 
        ``e = -1`` is the inverse matrix of ``m``.                
        """
        if isinstance(e, Integral):
            if e > 1:
                mask = 1 << (e.bit_length() - 2)
                acc = self.copy()
                while mask:
                    acc @= acc
                    if (e & mask):
                        acc @= self
                    mask >>= 1
                return acc
            elif e >= 0:
                nqb = self.shape[0]
                if nqb == self.shape[1]:
                    return self.reduce() if e else qs_unit_matrix(nqb)
                self @ self  # raise shape error
            else:
                return self.inv().power(-e)
        elif isinstance(e, QStateMatrix):
            return e.inv() @ self @ e
        else:
            err = "Illegal exponent type for QStateMatrix"
            raise TypeError(err)


    def order(self, max_order):
        """Try to find the order of a matrix 
        
        If the matrix ``m`` has order ``e`` for ``e <= max_order``,
        i.e. ``m.power(e)`` is the unit matrix, then ``e`` is 
        returned. Otherwise ``ValueError`` is raised.
        
        The function might also succeed if ``e`` is slighty larger
        than ``max_order``. It has run time ``O(max_order**0.5)``.        
        """
        def as_tuple(matrix):
             return tuple(matrix.data) + matrix.factor
        nqb = self.shape[0]
        if not self.lb_rank() == nqb == self.shape[1]:
            err = "QStateMatrix object is not invertible"
            raise ValueError(err)       
        if self.lb_norm2():
            err = "QStateMatrix object has infinite order"
            raise ValueError(err)
        unit = qs_unit_matrix(nqb)
        d = {as_tuple(unit):0}
        n = int(math.sqrt(max_order)) + 2
        m = self.copy()
        for i in range(1, n):
            if m == unit:
                return i
            d[as_tuple(m)] = i 
            m @= self
        m = m.inv()
        acc = m.copy()
        for i in range(1, n):
            t = as_tuple(acc)
            if t in d:
                return i * n + d[t]
            acc @= m
        err = "Order of QStateMatrix object not found" 
        raise ValueError(err)

    #########################################################################
    # Dealing with the Pauli subgroup of the Clifford group
     
    def pauli_vector(self):
        try:
            return super(QStateMatrix,self).pauli_vector()
        except ValueError:
            err = "QStateMatrix object is not in the Pauli group"
            print("\n%s:\n%s\n" % (err, str(self)))
            raise            
            
        
    #########################################################################
    # Obtaining (complex) entries and submatrices
        
        
    def __getitem__(self, item):
        if not isinstance(item, tuple):
            item = (item,)
        while len(item) < 2:
            item = item + (None,)
        a0, f0 = _as_index_array(item[0], self.shape[0]) 
        a1, f1 = _as_index_array(item[1], self.shape[1])
        if f0 & f1:
            return self.complex()
        a0 = a0 << self.shape[1]
        shape_ =  a0.shape + a1.shape 
        a = np.ravel(a0)[:, np.newaxis] + np.ravel(a1)[ np.newaxis, :] 
        if a.dtype != np.uint32:
            a = np.array(a, dtype = np.uint32)
        a = np.ravel(a, order = "C")
        c = self.entries(a)  
        if len(shape_):        
            return c.reshape(shape_)
        return c[0]

    #########################################################################
    # Formatting a quadratic state matrix

    def __str__(self):
        if FORMAT_REDUCED:
            qs = self.copy()
            qs.reduce_matrix()
            return _format_state(qs, True)
        return _format_state(qs, False)




####################################################################
# Formatting a QStateMatrix object
####################################################################


PHASE = [ ("",""),  (""," * (1+1j)"),  (""," * 1j"), ("-"," * (1-1j)"),
          ("-",""), ("-"," * (1+1j)"), ("-"," * 1j"), (""," * (1-1j)"), 
]

def _format_scalar(e, phase):
    if (phase & 1): e -= 1
    prefix, suffix = PHASE[phase]
    if 0 <= e <= 12 and not e & 1:
        s_exp = str(int(2**(e/2)))
    else:
        s_exp = ("2**%.1f" if e & 1 else "2**%d") % (e/2)
        if prefix:
            s_exp = "(" + s_exp + ")"
    return prefix + s_exp + suffix  
  
BRACKETS = { 
   (0,0):("  <","scalar",">"),   # a scalar
   (0,1):("  <","","|"),         # a row vector or a  *bra-*
   (1,0):("  |","",">"),         # a column vector or a  *-ket*
   (1,1):("  |", "><","|")       # a matrix
}


def binary(n, start, length, leading_zeros = False):
    if length == 0:
        return ""
    n = (n >> start) & ((1 << length) - 1)
    b = format(n, "b")
    c = "0" if leading_zeros else " "
    return c * (length - len(b)) + b


D_PM = { '0':'+', '1':'-'}
D_J = { '+':'.', '-':'j'}


def binary_q(n, start, length, pos, reduced = True):
    def pm_repl(m):
        return "-" if  m.group(0) == "1" else "+"
    def j_repl(m):
        return "j" if  m.group(0) == "1" else "."
    if length < 2:
        return ""
    s =  binary(n, start, length, leading_zeros = True) 
    s = [D_PM[x] for x in s[::-1]]
    s[pos] = D_J[s[pos]] if pos else '.'
    s = "".join(s)
    if reduced:
        return s[:pos+1] + " " * (length - pos - 1)
    return s

                      
def _format_data(data, rows, cols, reduced = False):
    s = ""
    nrows = len(data)
    if len(data) < 2 and  rows + cols == 0:
        return s
    if len(data) == 0:
         data = [0]
    left, mid, right = BRACKETS[bool(rows), bool(cols)]
    left_bl = " " * len(left)
    mid_bl = " " * len(mid)
    right_bl = " " * len(right)
    nq, nd = len(data) - 1, 0
    for i, d in enumerate(data):
        rc = binary(d, 0, rows + cols, not reduced or i == 0)
        r, c = rc[:rows], rc[rows:]
        q = binary_q(d, rows + cols, len(data), i, reduced)
        sq, sd = "  " + q,  left + r + mid + c + right  + "\n"
        if reduced:
            s += sq[:len(sq) - nq] + "  " + sd[nd:]
            nq, nd = nq - 1, nd + 1
        else:
            s += sq +  "  " + sd
        left, mid, right = left_bl, mid_bl, right_bl
    return s
        

STATE_TYPE = { (0,0) : ("QState scalar"), 
               (0,1) : ("QState row vector"), 
               (1,0) : ("QState column vector"),
               (1,1) : ("QState matrix")
}    
        
    
def _format_state(q, reduced = False):
    """Return  a ``QStateMatrix`` object as a string."""
    rows, cols = q.shape
    try:
        data = q.data
    except ValueError:
        print("\nError: Bad instance of class QStateMatrix:\n") 
        print(_format_state_raw(q))        
        raise    
        
    e = q.factor
    str_e = _format_scalar(*e) if len (data) else "0"
    str_data = _format_data(data, rows, cols, reduced)   
    qtype = STATE_TYPE[bool(rows), bool(cols)]
    s = "<%s %s" % (qtype, str_e)
    if len(str_data):
       s += " *\n" + str_data 
    s += ">\n"                  
    return s

def _format_state_raw(q):
    s = ("QStateMatrix, shape = %s, factor = %s, nrows = %s, cols = %s\n"
        % (q.shape, q.factor, q.nrows, q.ncols))
    s += "data:\n"
    length = q.nrows + q.ncols
    for d in q.raw_data[:q.nrows]:
        s += binary(d, 0, length) + "\n"
    return s
        

####################################################################
# Computing an array of indices
####################################################################
        
        
def _as_index_array(data, nqb):
    """Convert an index ``data`` to an array of indices.
    
    ``data`` in an object for indexing a one-dimesnional numpy
    array of length ``nqb``. 
    
    Return a pair ``(a, full)`` where ``a`` is a numpy array 
    containing the indices and ``full`` is True iff
    ``a`` contains the data ``range(1 << nqb)``.
    """
    mask = (1 << nqb) - 1
    if isinstance(data, Integral):
        return np.array(data & mask, dtype = np.uint32), False
    if data is None:
        return np.arange(1 << nqb, dtype = np.uint32), True
    if isinstance(data, slice):
        ind = data.indices(1 << nqb)
        full = ind == (0, 1 << nqb, 1) 
        return np.arange(*ind, dtype = np.uint32), full
    ind = np.array(data, dype = np.uint32, copy = False) 
    if len(ind.shape) > 1:
        err = "Bad index type for QState12 array"
        raise TypeError(err)
    return  ind & mask, False 
    
    
    

    
####################################################################
# Creating specific state matrices of type QStateMatrix
####################################################################



def qs_unit_matrix(nqb):
    """Return unit matrix as an instance of class ``QStateMatrix``
    
    The returned unit matrix has shape ``(nqb, nqb)``. So it
    represents a ``2**nqb`` times ``2**nqb`` unit matrix.
    """
    qs = QStateMatrix(nqb, nqb) 
    qstate12_unit_matrix(qs, nqb)
    return qs
    
def qs_rand_matrix(rows, cols, data_rows):
    limit = (1 << (rows  + cols + data_rows)) - 1 
    data = [randint(0, limit) for i in range(data_rows)]
    return QStateMatrix(rows, cols, data, mode = 1)
          
def qs_column_monomial_matrix(data):
    nqb = len(data) - 1
    qs = QStateMatrix(nqb, nqb) 
    qstate12_column_monomial_matrix(qs, nqb, data)
    return qs
    
def qs_row_monomial_matrix(data):
    nqb = len(data) - 1
    qs = QStateMatrix(nqb, nqb) 
    qstate12_row_monomial_matrix(qs, nqb, data)
    return qs


def qs_pauli_matrix(nqb, v):
    qs = QStateMatrix(nqb, nqb)
    qstate12_pauli_matrix(qs, nqb, v)    
    return qs
    
def qs_ctrl_not_matrix(nqb, vc, v):
    """Return Transformation matrix for ctrl-not gate
    
    ``nqb`` is the rank of the matrix.
    TODO: ``vc, v`` yet to be documented.

    """
    qs = qs_unit_matrix(nqb)
    mask = (1 << nqb) - 1
    qs.gate_ctrl_not(vc & mask, v & mask) 
    return qs.reduce()    

def qs_phi_matrix(nqb, v, phi):
    qs = qs_unit_matrix(nqb)
    qs.gate_phi(v << nqb, phi) 
    return qs    

def qs_ctrl_phi_matrix(nqb, v1, v2):
    qs = qs_unit_matrix(nqb)
    qs.gate_ctrl_phi(v1 << nqb, v2) 
    return qs    

def qs_hadamard_matrix(nqb, v):
    qs = qs_unit_matrix(nqb)
    qs.gate_h(v)    
    return qs.reduce()


####################################################################
# Some wrappers for functions written in C
####################################################################

    
def flat_product(a, b, nqb, nc):
    return a.copy().qstate12_product(b.copy(), nqb, nc)


def pauli_vector_mul(nqb, v1, v2):
    return qstate12_pauli_vector_mul(nqb, v1, v2)

def pauli_vector_exp(nqb, v, e):
    return qstate12_pauli_vector_exp(nqb, v, e)
