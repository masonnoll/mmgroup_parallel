r"""Generation of genernal C code for reduction in the monster 

This script generates the C code for reduction of elements of the
monster group. The generated C modules are used in the python 
extension ``mmgroup.mm_reduce``. The functions used by that extension 
are contained in a shared library with name ``mmgroup_mm_reduce``. 
The reason for creating such a shared library is that that these 
functions may also be called by an external computer algebra package.

Therefore several .c, .h, .pyd files are created, and also one .pyx
file. Then the Cython package is used for integrating all C 
functions into a single python extension. The action of the extension
is controlled by the .pyx file, which also includes the generated 
.pyd files.

Function ``generate_pyx()`` in this module generates all these files.


Implementation of this module is along the lines of module ``codegen_mm"


"""


from __future__ import absolute_import, division, print_function
from __future__ import  unicode_literals


import sys
import os
import re
import collections
import warnings
from numbers import Integral


from config import SRC_DIR, DEV_DIR,  C_DIR, PXD_DIR
from config import REAL_SRC_DIR 

from config import INT_BITS
SKE_DIR = os.path.join(DEV_DIR, "mm_reduce")



if  __name__ == "__main__":
    sys.path.append(REAL_SRC_DIR)
    from mmgroup.generate_c import TableGeneratorStream, make_doc, format_item
    from mmgroup.generate_c import generate_pxd, pxd_to_pxi
    from mmgroup.dev.mm_op import mm_op
    from mmgroup.dev.mm_reduce import order_vector_tables
    from mmgroup.dev.mm_reduce import vector_v1_mod3




VERBOSE = 0


##########################################################################
# Entering tables and automatically generated code
##########################################################################

TABLE_CLASSES = None

def table_classes():
    global TABLE_CLASSES
    if not TABLE_CLASSES is None:
        return  TABLE_CLASSES

    if "mockup" in sys.argv[1:]:
        TABLE_CLASSES = [
            mm_op.Mockup_MM_Op,
            order_vector_tables.Mockup_OrderVectorTable,
            vector_v1_mod3.Mockup_V1_Mod3_Table,
        ]
    else:
        TABLE_CLASSES = [
            mm_op.MM_Op,
            order_vector_tables.OrderVectorTable,
            vector_v1_mod3.V1_Mod3_Table,
        ]  
    return TABLE_CLASSES




##########################################################################
# Generating .c files
##########################################################################


H_REDUCE_SKELETONS = [
    "mm_reduce.h",
]

C_REDUCE_SKELETONS = [
   "mm_order_vector",
   "mm_order",
   "mm_compress",
   "mm_reduce",
   "mm_suborbit",
   "mm_shorten",
   "mm_vector_v1_mod3",
 
]



def mm_reduce_sources():
    return C_REDUCE_SKELETONS



##########################################################################
# Generating .h and .pxd files files
##########################################################################

H_REDUCE_NAME = "mm_reduce.h"      # name of generated .h file


PXD_REDUCE_NAME = "mm_reduce.pxd"  # name of generated .pxd file



### Generate the basic header


H_REDUCE_BEGIN = """

// %%EXPORT_KWD MM_REDUCE_API


// %%GEN h
#ifndef MM_REDUCE_H
#define MM_REDUCE_H


"""


H_REDUCE_END = """
// %%GEN h

#endif  // #ifndef MM_REDUCE_H
"""




### Declarations for the generated .pxd files


PXD_DECLARATIONS = """

from libc.stdint cimport uint64_t, uint32_t, uint16_t, uint8_t
from libc.stdint cimport int64_t, int32_t
from libc.stdint cimport uint{INT_BITS}_t as uint_mmv_t

INT_BITS = {INT_BITS}


cdef extern from "mm_reduce.h":
    enum: MAX_GT_WORD_DATA
    enum: MM_COMPRESS_TYPE_NENTRIES

    ctypedef struct gt_subword_type:
        uint32_t eof  
        uint32_t length
        uint32_t img_Omega
        uint32_t t_exp
        uint32_t reduced
        gt_subword_type *p_prev
        gt_subword_type *p_next
        uint32_t data[MAX_GT_WORD_DATA]

    ctypedef struct gt_word_type:
        gt_subword_type *p_end
        gt_subword_type *p_node
        gt_subword_type *p_free
        int32_t reduce_mode;

    ctypedef struct mm_compress_type:
        uint64_t nx
        uint32_t w[MM_COMPRESS_TYPE_NENTRIES]


""".format(INT_BITS = INT_BITS)






    
##########################################################################
# Generating the .pyx file
##########################################################################



PXI_FILE_NAME = "mm_reduce.pxi"







##########################################################################
# Functions of this module for generating .c, .h and .pyx file
##########################################################################

def list_reduce_c_files():
    """Return list of names of c files generated by make_reduce()"""
    def c_file(name):
         return os.path.join(C_DIR, name + ".c")
    return [c_file(name) for name in C_REDUCE_SKELETONS]


def make_reduce():
    """Generate basic .c files from  .ske files 

    The relevant .ske files are listed in variable
    C_REDUCE_SKELETONS. One corresponding .h and .pxd file
    is also generated. The .c files and the .h file are written 
    to directory given by C_DIR, the .pxd file is written to the 
    current directory.

    Tables and directives for automatically generated C code
    are taken from the classes listed in BASIC_TABLE_CLASSES.

    Return pair of lists, one of the .c files and one of the.
    .pxd files generated
    """
    tables = {}
    directives = {}
    global generated_tables
    for table_class in table_classes():
        table_instance = table_class(15)
        tables.update(table_instance.tables)
        directives.update(table_instance.directives)
    # print("Basic functions:\n",  directives.keys())
    tg = TableGeneratorStream(tables, directives, verbose = VERBOSE)
    # first generate C files
    c_files = []
    all_ske_files = [H_REDUCE_BEGIN] 
    all_ske_files += [
        os.path.join(SKE_DIR, f) for f in H_REDUCE_SKELETONS]
    for name in C_REDUCE_SKELETONS:
        ske_file = name + ".ske"
        ske_path = os.path.join(SKE_DIR, ske_file)
        c_file = name + ".c"
        c_path = os.path.join(C_DIR, c_file)
        print("Creating %s from %s" % (c_file, ske_file))
        tg.generate(ske_path, c_path)
        all_ske_files.append(ske_path)
        c_files.append(c_path)
    all_ske_files.append(H_REDUCE_END)

    # generate .h and .pxd file
    h_file =  H_REDUCE_NAME
    h_path =  os.path.join(C_DIR, h_file)
    pxd_file =  PXD_REDUCE_NAME
    print("Creating %s from previous .ske files" % h_file)
    #print(all_ske_files)
    tg.generate(all_ske_files, None, h_path)
    print("Creating %s" % pxd_file)
    generate_pxd(
        os.path.join(PXD_DIR, pxd_file),
        h_path, 
        PXD_DECLARATIONS
    )
    return c_files,  [ pxd_file ]







##########################################################################
# The main function for generating code
##########################################################################


def generate_files():
    """The main function of this module for generating code

    This function generates all reqired .c files and also the required
    headers.

    It also generates the .pxi file with name given by PYX_FILE_NAME and
    stores it in the current directory. Cython will use the .pxi file to
    build a wrapper for all generated C functions. 
    """
    def pxi_comment(text, f):
        print("\n" + "#"*70 + "\n### %s\n" % text + "#"*70 + "\n\n",file=f)
    c_files,  pxd_files =  make_reduce() 
    print("Creating %s" % PXI_FILE_NAME)
    f_pxi = open(os.path.join(PXD_DIR, PXI_FILE_NAME), "wt")
    print(PXD_DECLARATIONS, file = f_pxi)
    for pxd_f in pxd_files:
        pxi_comment("Wrappers for C functions from file %s" % pxd_f, f_pxi)
        pxi_content = pxd_to_pxi(
            os.path.join(PXD_DIR, pxd_f),
            os.path.split(pxd_f)[0]
        )
        print(pxi_content, file = f_pxi)
    f_pxi.close()
    print("Code generation for module mm_reduce terminated successfully")
    return c_files


##########################################################################
# Main function
##########################################################################





if __name__ == "__main__":
    generate_files()
