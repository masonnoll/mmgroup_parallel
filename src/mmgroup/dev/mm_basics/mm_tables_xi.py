"""Generate tables for operation xi on the rep 196884x of the monster

Operators xi and xi**2 (with xi**3 == 1) operate on unit vectors with 
tags B, C, T, X as defined in mm_aux.py. We divide the 759 octads 
occuring as indices for tag T into three groups:

 TG:  octad   0 ...  15,   15 grey even octads
 T0:  octad  15 ... 374,  360 even octads which are not grey
 T1:  octad 375 ..  758,  384 odd octads

Octads are Golay code elements. Odd, even and grey Golay code elements 
are defined in [Seys19]. In the numbering of our octads and basis
vectorv, octads are ordered as in the table above. Similarly, we divide 
the basis vectors with tag T into two blocks with tags T0 and T1. 
Basis vectors in T0 are indexed by even and are indexed by odd Golay 
code vectors.

The unit vectors for each tag have a natural matrix structure.
Let BC the union of the basis vectors with tags B, C and TG Then
Operator xi permutes tags BC, T0, T1, X0 and X1 as described in the
following table. 


Tag     Matrix      Blocks     Block    Total     Common   xi(tag)
        structure              size     size     tag name
 B      24  x  24   \
 C      24  x  24    >   1      2496(*)  2496       BC       BC
 TG     15  x  64   /
 T0    360  x  64       45    8 x 64    23040       T0       T0
 T1    384  x  64       64    6 x 64    24576       T1       X0
 X0   1024  x  24       64   16 x 24    24576       X0       X1
 X1   1024  x  24       64   16 x 24    24576       X1       T1

(*) The block sizes for tags B and C have been computed under the
    assumption that 32 contiguous locations are reserved for 
    the 24 entries of a row, as described below.

The entries corresponding to a tag are stored in row-major order,
so that e.g. T0[i,j] and T0[i,j+1] are contiguous. If a tag has
stucture I x 24 then 32 instead of 24 entries are reserved for 
each row. The order of tags is as in the table. 

The entries corresponding to tags T0, T1, X0, X1 can be divided
into 45 or 64 contiguous blocks as indicated in the table. Then 
the image of the i-th block of a tag I under the operator xi is 
the i-th block of tag xi(I). We will use this local structure of
operator xi in our implementation of operators xi and xi**2.

Tables for the monomial operation of xi can be generated by
class mat24fast.Mat24Xi. Class Pre_MM_TablesXi provides
updated version of these tables suitable for the implementation
of operator xi. Class MM_TablesXi puts these tables into an
order suitable for that implementation.

TODO: continue documentation!!!
"""

#234567890123456789012345678901234567890123456789012345678901234567890

from __future__ import absolute_import, division, print_function
from __future__ import  unicode_literals



import os
import sys
import numpy as np
from itertools import product

from mmgroup.generate_c import UserDirective

try:
    # Try importing the fast C function
    from mmgroup import generators as gen 
except (ImportError, ModuleNotFoundError):
    # Use the slow python function if the C function is not available
    print("\nUsing slow Python functions for table generation!!!\n")
    from mmgroup.dev.generators.gen_xi_ref import GenXi 
    gen = GenXi




def make_table_bc_symmetric(table):
    def b(i, j):
        return 32 * i + j
    def c(i, j):
        return 32 * (i + 24) + j
    for i in range(24):
        for j in range(i):
            table[b(j,i)] = table[b(i,j)] 
            table[c(j,i)] = table[c(i,j)] 
        table[b(i,i)] = b(i,i)
        table[c(i,i)] = c(i,i)


def cut24(table):
    table = table.reshape(-1, 32)
    #assert sum(table[:,24:].reshape(-1)) == 0, (table.shape, table[:,24:])
    table = table[:,:24]
    table = table.reshape(-1)
    return table



def check_table(table, blocks, row_length):
    assert row_length in (24, 32)
    if row_length == 24:
        table = cut24(np.copy(table))
    length = len(table)
    image_length = (max(table & 0x7fff) + 31) & -32
    blocklen, r0 = divmod(length, blocks)
    image_blocklen, r1 = divmod(image_length, blocks)
    assert r0 == r1 == 0
    for i, start in enumerate(range(0, length, blocklen)):
         part = table[start:start+blocklen] & 0x7fff
         t_min, t_max = i*image_blocklen, (i+1)*image_blocklen
         assert t_min <= min(part) <= max(part) < t_max



class Pre_MM_TablesXi: 
    def __init__(self):
        BCT, T0 = 24*32, 72*32 + 15*64
        T1, X0  = 72*32 + 375*64,  72*32 + 759*64
        X1 = X0 + 1024*32

        self.TAG_NAMES = {BCT:"BC", T0:"T0", T1:"T1", X0:"X0", X1:"X1"} 

        self.SHAPES = {
            BCT: (1, 78, 32), T0: (45, 16, 32), T1: (64, 12, 32),
            X0: (64, 16, 24), X1: (64, 16, 24)
        }

        self.MAP_XI = {
            (1,BCT): BCT, (1,T0): T0, (1, T1): X0, (1, X0): X1, (1,X1): T1
        }
        MAP_XI_ = {}
        for (exp, src), dest in self.MAP_XI.items():
            MAP_XI_[2, dest] = src
        self.MAP_XI.update(MAP_XI_)
        del MAP_XI_ 

        TABLE_ORDER = [None, BCT, T0, T1, X0, X1]

        self.TABLE_INDICES = {}
        for i, ofs in enumerate(TABLE_ORDER):
            if i:
                self.TABLE_INDICES[1, ofs] = (1, i) 
                self.TABLE_INDICES[2, ofs] = (2, i) 

        self.REVERSE_TABLE_INDICES = {}
        for x, y in self.TABLE_INDICES.items():
            self.REVERSE_TABLE_INDICES[y] = x

        self.PERM_TABLES = {}
        self.SIGN_TABLES = {}
        for (i, j), (_, start) in self.REVERSE_TABLE_INDICES.items():
            image_start = self.MAP_XI[i, start]
            shape =  self.SHAPES[start]
            image_shape = self.SHAPES[image_start]
            table = gen.make_table(j, i)
            assert shape[0] == image_shape[0], (shape[0], image_shape[0]) 
            assert len(table) == shape[0] * shape[1] * 32
            image_len = image_shape[0] * image_shape[1] * 32
            check_table(table, shape[0], shape[2])
            inv_table = gen.invert_table(table, shape[2], image_len)
            if start == BCT:
                make_table_bc_symmetric(inv_table)
            t_perm, t_sign = gen.split_table(inv_table, shape[1]*32)
            del inv_table
            if image_shape[2] == 24:
                t_perm = cut24(t_perm)
            self.PERM_TABLES[i, j] = t_perm 
            self.SIGN_TABLES[i, j] = t_sign

def map_table(exp, j):
    j1 = j if (exp == 1 or j < 4) else 9 - j
    return exp, j1

def operator_(x):
    if x == 0: return None
    if x > 0: return '+'
    return '-'

#234567890123456789012345678901234567890123456789012345678901234567890


def code_pointers(name_perm, name_sign):
    s = ""
    for exp in range(1,3):
       s += "{\n"
       for i in range(1,6):
           t_p = name_perm + str(exp) + str(i) 
           t_s = name_sign + str(exp) + str(i)
           s += "    {%s, %s}%s\n" % (t_p, t_s, ("," if i < 5 else ""))
       s += "}%s\n" % ("," if exp < 2 else "")
    return s


class MM_TablesXi:
    done_ = False
    directives = {
        "CODE_XI_POINTERS": UserDirective(code_pointers, "ss"),
    }
    def __init__(self):
        cls = self.__class__
        if cls.done_:
            return
        Pre_Tables = Pre_MM_TablesXi()
        cls.TAG_NAMES = Pre_Tables.TAG_NAMES
        cls.PERM_TABLES = {}
        cls.SIGN_TABLES = {}
            
        for i in range(1,3):
            for j in range(1,6):
                i1, j1 =  map_table(i, j)
                cls.PERM_TABLES[i, j] = Pre_Tables.PERM_TABLES[i1, j1] 
                cls.SIGN_TABLES[i, j] = Pre_Tables.SIGN_TABLES[i1, j1]

        cls.SOURCE_SHAPES = {}
        cls.DEST_SHAPES = {}
        cls.SOURCE_START_1 = {}
        cls.SOURCE_START_DIFF = {}
        cls.SOURCE_OP_DIFF = {}
        cls.DEST_START_1 = {}
        cls.DEST_START_DIFF = {}
        cls.DEST_OP_DIFF = {}
        cls.SOURCE_TAGS = {}
        cls.DEST_TAGS = {}
        cls.MAX_ABS_START_DIFF = MDIFF = 32768
        REV = Pre_Tables.REVERSE_TABLE_INDICES
        for j in range(1,6):
            source_start1 = REV[map_table(1,j)][1] 
            source_start2 = REV[map_table(2,j)][1]
            dest_start1 = Pre_Tables.MAP_XI[1, source_start1]
            dest_start2 = Pre_Tables.MAP_XI[2, source_start2]
            SHAPES = Pre_Tables.SHAPES
            assert SHAPES[source_start1] == SHAPES[source_start2] 
            assert SHAPES[dest_start1] == SHAPES[dest_start2]
            cls.SOURCE_SHAPES[j] = SHAPES[source_start1]
            cls.DEST_SHAPES[j] = SHAPES[dest_start1]
            cls.SOURCE_START_1[j] = source_start1
            cls.SOURCE_START_DIFF[j] = source_start2 - source_start1
            cls.DEST_START_1[j] = dest_start1
            cls.DEST_START_DIFF[j] = dest_start2 - dest_start1
            assert abs(cls.SOURCE_START_DIFF[j]) in [0, MDIFF]
            assert abs(cls.DEST_START_DIFF[j]) in [0, MDIFF]
            cls.SOURCE_OP_DIFF[j] = operator_(cls.SOURCE_START_DIFF[j])
            cls.DEST_OP_DIFF[j] = operator_(cls.DEST_START_DIFF[j])
            cls.SOURCE_TAGS[j] = (cls.TAG_NAMES[source_start1], 
                cls.TAG_NAMES[source_start2]) 
            cls.DEST_TAGS[j] = (cls.TAG_NAMES[dest_start1], 
                cls.TAG_NAMES[dest_start2]) 
        del SHAPES; del REV
       
        TABLES = {}
        for k in product([1,2], range(1,6)):
            TABLES["MM_TABLE_PERM_XI_%d%d" % k] = cls.PERM_TABLES[k]
            TABLES["MM_TABLE_SIGN_XI_%d%d" % k] = cls.SIGN_TABLES[k]

        cls.tables = TABLES
        cls.done_ = True

    @classmethod
    def display_config(cls):
        cls.__init__()
        print("source:")
        print(" shapes:", cls.SOURCE_SHAPES)
        print(" start: ", cls.SOURCE_START_1)
        print(" diff:  ", cls.SOURCE_OP_DIFF)
        print(" tags:  ", cls.SOURCE_TAGS)
        print("destination:")
        print(" shapes:", cls.DEST_SHAPES)
        print(" start: ", cls.DEST_START_1)
        print(" diff:  ", cls.DEST_OP_DIFF)
        print(" tags:  ", cls.DEST_TAGS)



class Mockup_MM_TablesXi:
    directives = {
        "CODE_XI_POINTERS": UserDirective(code_pointers, "ss"),
    }
    TABLES = {}
    for k in product([1,2], range(1,6)):
        TABLES["MM_TABLE_PERM_XI_%d%d" % k] = [0]
        TABLES["MM_TABLE_SIGN_XI_%d%d" % k] = [0]
    tables = TABLES


class Tables:
     mockup_tables = Mockup_MM_TablesXi.tables
     mockup_directives = Mockup_MM_TablesXi.directives

     def __init__(self, *args, **kwds):
         self._table_class = None

     def _load_tables(self):
         if self._table_class is None:
             self._table_class =  MM_TablesXi()
         return self._table_class

     @property
     def tables(self):
         return self._load_tables().tables

     @property
     def directives(self):
         return self._load_tables().directives



if __name__ == "__main__":
     MM_TablesXi().display_config() 



