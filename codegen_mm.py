r"""Generation of genernal C code for the monster representations

This script generates the C code for basic computations in the monster
group. The generated C modules are used in the python extension 
``mmgroup.mm``. The functions used by that extension are contained in 
a shared library with name ``mmgroup_mm_basics``. The reason for
creating such a shared library is that that these functions are also
called by other python extensions.

Therefore several .c, .h, .pyd files are created, and also one .pyx
file. Then the Cython package is used for integrating all C 
functions into a single python extension. The action of the extension
is controlled by the .pyx file, which also includes the generated 
.pyd files.

Function ``generate_pyx()`` in this module generates all these files.

Variable ``INT_BITS`` in file config.py should be set to 32 or 64 for
32-bit or 64-bit target systems. There might be performace issues
if ``INT_BITS`` is not chosen properly. 


Generating .c files
...................

We use the C code generation mechanism in class 
``generate_c.TableGenerator``. There .c and .h files are generated
from files with extension .ske. These .ske files are like .c files, 
but augmented with some code generation statements for entering 
(usually rather large) tables and automatically generated code into 
the .c file to be generated. These .ske files may also have statements 
for automatically generating .h files declaring the exported functions.  
    
Variable C_BASICS_SKELETONS is a list of all .ske files. We will 
create  one  .c file from each .ske file in that list.


Entering tables and automatically generated code
................................................

We create an instance ``tg`` of class ``TableGenerator`` for 
generating the .c files. The table generator ``tg`` takes two
dictionaries ``tables`` and ``directives`` as arguments. These
dictionaries provide user-defined tables and directives for the
code generator. There are several table-providing classes that
provide dictionaries ``tables`` and ``directives`` for the 
code genertor ``tg``. Variable ``BASIC_TABLE_CLASSES`` contains 
the list of table-providing classes.

Each table-providing class has methods ``tables()`` and 
``directives()`` that return the corresponding dictionaries.
The union of the dictionaries  ``tables()`` or ``directives()`` 
of all table-providing classes is passed as the constructor
of the instance ``tg`` as argument ``tables()`` or 
``directives()``, respectively.

A simple example for a table-generating class is class 
``Lsbit24Function`` in module ``mmgroups.dev.mat24.mat24aux``.


Generating the .h and the .pxd file
...................................

We create a single .h file containing the prototypes for the 
functions in all generated .c files. The name of that .h file is 
given by the variable ``H_BASICS_NAME``. The content of the .h file 
is also  generated by the instance ``tg`` of class 
``TableGenerator`` described above. 

The .h file has a prefix given by the string ``H_BASICS_BEGIN``
and suffix given by the string ``H_BASICS_END``. 

For each .h file the Cython package requires a .pxd file for
generating a python extension. The .pxd file contains essentially 
the same information as the .h file. Method ``generate_pxd()``
of the code generator ``tg`` generates the .pxd file. The name
of the .pxd file is given by ``PXD_BASICS_NAME``. The generated
.pxd file is prefixed with the content of the string
``PXD_DECLARATIONS``.



Generating the .pxi file
........................

The functions exported by the python extension ``mmgroup.mm`` are
just simple wrappers for the C functions generated by the code
generator. These wrappers must be coded in the Cython language.
They are simple enough so that they can be generated automatically
by function  ``pxd_to_pyx()`` in module ``mmgroup.generate_c``.
Function ``pxd_to_pyx()`` takes the .pxd file (see last section)
as input and it creates the .pxi file with name given by
``PXI_FILE_NAME``. 

When building the ``mmgroup.mm`` extension we simply include that 
.pxi file into the file ``mm_basics.pyx`` (located in directory
``.../mmgroup/dev/mm_basics``). That .pyx file defines the content
of the extension ``mmgroup.mm``.

 
Generating documentation
........................
 
Function ``make_doc()`` in module  ``mmgroup.generate_c`` is used to
generate documentation from some automaticaly generated .c files. 
Here documentation files have names similar to the names of the
corresponding .c files. Usually they just contain a module
documentation and also the commented function prototypes taken from
the .c files. 


Location of the output files
............................

The location of the generated output files is controlled by certain
variables in module config.py. Each of these variables specifies the
name of a directory.

Files with extension .c, .h go to the directory ``C_DIR``. Files with
extension .pxd, .pxi, .pyx go to the directory ``PXD_DIR``. 

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
sys.path.append(REAL_SRC_DIR)

from config import INT_BITS
SKE_DIR = os.path.join(DEV_DIR, "mm_basics")

from mmgroup.generate_c import TableGenerator, make_doc, format_item
from mmgroup.generate_c import pxd_to_pyx

import mmgroup.dev.mm_basics
from mmgroup.dev.mm_basics import mm_aux, mm_tables, mm_basics
from mmgroup.dev.mm_basics import mm_tables_xi, mm_crt





VERBOSE = 0

##########################################################################
# Generating .c files
##########################################################################


H_BASICS_SKELETONS = [
    "mm_basics.h",
]

C_BASICS_SKELETONS = [
   "mm_aux",
 #  "mm_sparse",  # deprecated!
 #  "mm_random",  # deprecated!
   "mm_tables",
   "mm_group_word",
   "mm_tables_xi",
   "mm_crt",
]



##########################################################################
# Generating .h and .pxd files files
##########################################################################

H_BASICS_NAME = "mm_basics.h"      # name of generated .h file


PXD_BASICS_NAME = "mm_basics.pxd"  # name of generated .pxd file



### Generate the basic header


H_BASICS_BEGIN = """

// %%EXPORT_KWD MM_BASICS_API


// %%GEN h
#ifndef MM_BASICS_H
#define MM_BASICS_H


"""


H_BASICS_END = """
// %%GEN h

#endif  // #ifndef MM_BASICS_H
"""




### Declarations for the generated .pxd files


PXD_DECLARATIONS = """

from libc.stdint cimport uint64_t, uint32_t, uint16_t, uint8_t
from libc.stdint cimport int64_t, int32_t
from libc.stdint cimport uint{INT_BITS}_t as uint_mmv_t

INT_BITS = {INT_BITS}
""".format(INT_BITS = INT_BITS)




##########################################################################
# Entering tables and automatically generated code
##########################################################################


if "mockup" in sys.argv[1:]:
    BASIC_TABLE_CLASSES = [
        mm_basics.Mockup_MM_Const,
        mm_tables_xi.Mockup_MM_TablesXi,
    ]  
else:
    BASIC_TABLE_CLASSES = [
        mm_basics.MM_Const,
        mm_tables_xi.MM_TablesXi,
    ]  


MORE_BASIC_TABLE_CLASSES = [
    mm_basics.MM_Const,
    mm_aux.MM_IO24,
    mm_tables.MM_OctadTable,
    mm_crt.MM_CrtCombine,  
]

BASIC_TABLE_CLASSES += MORE_BASIC_TABLE_CLASSES

    
##########################################################################
# Generating the .pyx file
##########################################################################



PXI_FILE_NAME = "mm_basics.pxi"







##########################################################################
# Functions of this module for generating .c, .h and .pyx file
##########################################################################

def list_basics_c_files():
    """Return list of names of c files generated by make_basics()"""
    def c_file(name):
         return os.path.join(C_DIR, name + ".c")
    return [c_file(name) for name in C_BASICS_SKELETONS]


def make_basics():
    """Generate basic .c files from  .ske files 

    The relevant .ske files are listed in variable
    C_BASICS_SKELETONS. One corresponding .h and .pxd file
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
    for table_class in BASIC_TABLE_CLASSES:
        table_instance = table_class()
        tables.update(table_instance.tables)
        directives.update(table_instance.directives)
    # print("Basic functions:\n",  directives.keys())
    tg = TableGenerator(tables, directives, verbose = VERBOSE)
    # first generate C files
    c_files = []
    all_ske_files = [H_BASICS_BEGIN] 
    all_ske_files += [
        os.path.join(SKE_DIR, f) for f in H_BASICS_SKELETONS]
    for name in C_BASICS_SKELETONS:
        ske_file = name + ".ske"
        ske_path = os.path.join(SKE_DIR, ske_file)
        c_file = name + ".c"
        c_path = os.path.join(C_DIR, c_file)
        print("Creating %s from %s" % (c_file, ske_file))
        tg.generate(ske_path, c_path)
        all_ske_files.append(ske_path)
        c_files.append(c_path)
    all_ske_files.append(H_BASICS_END)

    # generate .h and .pxd file
    h_file =  H_BASICS_NAME
    h_path =  os.path.join(C_DIR, h_file)
    pxd_file =  PXD_BASICS_NAME
    print("Creating %s from previous .ske files" % h_file)
    #print(all_ske_files)
    tg.generate(all_ske_files, None, h_path)
    print("Creating %s" % pxd_file)
    tg.generate_pxd(
        os.path.join(PXD_DIR, pxd_file), 
        h_file, 
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
    c_files,  pxd_files =  make_basics() 
    print("Creating %s" % PXI_FILE_NAME)
    f_pxi = open(os.path.join(PXD_DIR, PXI_FILE_NAME), "wt")
    print(PXD_DECLARATIONS, file = f_pxi)
    for pxd_f in pxd_files:
        pxi_comment("Wrappers for C functions from file %s" % pxd_f, f_pxi)
        pxi_content = pxd_to_pyx(
            os.path.join(PXD_DIR, pxd_f),
            os.path.split(pxd_f)[0]
        )
        print(pxi_content, file = f_pxi)
    f_pxi.close()
    print("Code generation for module mm terminated successfully")
    return c_files


##########################################################################
# Main function
##########################################################################





if __name__ == "__main__":
    generate_files()
