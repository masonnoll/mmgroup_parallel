"""Auxiliary functions for writing tables into C program"""

from __future__ import absolute_import, division, print_function
from __future__ import  unicode_literals


import sys
import re
import os
import argparse

from mmgroup.generate_c.make_c_tables import TableGenerator


from mmgroup.generate_c.generate_code import MyArgumentParser
from mmgroup.generate_c.generate_code import find_file
from mmgroup.generate_c.generate_code import open_for_write
from mmgroup.generate_c.generate_code import set_real_pathlist
from mmgroup.generate_c.generate_code import set_real_path 
from mmgroup.generate_c.generate_code import load_tables
from mmgroup.generate_c.generate_code import import_tables
from mmgroup.generate_c.generate_code import StringOutputFile
from mmgroup.generate_c.make_pxd import pxd_from_h
from mmgroup.generate_c.make_pxi import pxd_to_pxi




def generate_pxd_parser():
    """Create parser for reading arguments for code generation 

    """
    description = ("Generate .pdx and .pxi file from header file"
    "for the mmgroup project using certain tables in the source file."
    )

    epilog = ("Some more documentation will follow here later."
    )

    parser = MyArgumentParser(
        description=description, epilog=epilog,
        fromfile_prefix_chars='+',
    )

    parser.add_argument('--pxd-out', 
        metavar='PXD',
        action='store', default = None,
        help="Set name of generated .pxd file to PXD."
    )

    parser.add_argument('--h-in', 
        metavar='HEADER',
        action='store', default = None,
        help = "Set input HEADER for generating .pxd file."
    )

    parser.add_argument('--pxd-in', 
        metavar='PXD',
        action='store', default = None,
        help="Set input .pxd file PXD for generating .pxd file."
    )

    parser.add_argument('--pxi-in', 
        metavar='PXI',
        action='store', default = None,
        help="Set input .px file PXI for generating .pxi file."
    )

    parser.add_argument('--h-name', 
        metavar='HEADER',
        action='store', default = None,
        help="Set name of header to be stored in .pxd file to HEADER. "
             "Default is name of input header file."
    )

    parser.add_argument('--nogil', 
        action='store_true', default = False,
        help = "Optional, declare exported functions as 'nogil' "
        "when set."
    )
 
 
    parser.add_argument('--tables', 
        nargs = '*',  metavar='TABLES',
        action = 'extend', default = [], 
        help="Add list TABLES of table classes "
        "to the tables to be used for generating .pxd and .pxi files."
    )
  
    parser.add_argument('--pxd-path', nargs = '*', action='extend',
        metavar = 'PATHS', default = [],
        help = 'Set list of PATHS for finding input .pxd and .pxi files')

    parser.add_argument('--h-path', nargs = '*', action='extend',
        metavar = 'PATHS', default = [],
        help = 'Set list of PATHS for finding input .h files')

    parser.add_argument('--py-path', nargs = '*', action='extend',
        metavar = 'PATHS', default = [],
        help = 'Set list of PATHS for finding python scripts')

    parser.add_argument('--out-dir', 
        metavar = 'DIR', default = None,
        help = 'Set directory DIR for output file') 
 
    parser.add_argument('--mockup', 
        default = False,
        action = 'store_true',
        help = 'Use tables for Sphinx mockup if present')
 
    parser.add_argument('-v', '--verbose', action = 'store_true',
        help = 'Verbose operation')

    return parser




ERR_GENPXI = "Cannot create .pxi file if not output .pxd file is given" 

def set_pxi_out(instance):   
    setattr(instance, 'pxi_out', None) 
    if not getattr(instance,'pxi_in', None):
       return
    pxd_out =  getattr(instance,'pxd_out')
    if not pxd_out:
        raise ValueError(ERR_GENPXI)
    pxd_name, _ = os.path.splitext(pxd_out) 
    pxi_name = pxd_name + ".pxi"
    setattr(instance, 'pxi_out', pxi_name) 


def finalize_parse_args(s):
    #print("\nFinalizing\n", s)
    if getattr(s, 'finalized', None):
        return
    set_real_pathlist(s, 'h_path')
    set_real_pathlist(s, 'pxd_path')
    set_real_pathlist(s, 'py_path')
    set_real_path(s, 'out_dir')
    set_pxi_out(s)
    #print("\nFinalized\n", s)
    s.finalized = True
 


def check_args_parsed(args):
    ERR = False
    if not getattr(args, "pxd_out", None):
        ERR = "No output .pxd file specified"
    if not getattr(args, "h_in", None):
        ERR = "No input header file specified"
    if not getattr(args, "pxd_in", None):
        ERR = "No input .pxd file specified"
    if ERR:
        raise ValueError(ERR)


class pxdGenerator:
    """Yet to be documented"""
    def __init__(self, args):
        if isinstance(args, str):
            parser = generate_pxd_parser()
            self.s = parser.parse_args(args.split())
        elif isinstance(args, list):
            parser = generate_pxd_parser()
            self.s = parser.parse_args(args)
        elif isinstance(args, argparse.Namespace):
            self.s = args
        else:
            ERR = "Cannot constuct class %s object from %s object"
            raise TypeError(ERR % (self.__class__, type(args)))
        self.old_path = None
        check_args_parsed(self.s)

    def string_from_input(self, path, filename, table_generator = None):
        in_file = find_file(path, filename) if filename else None
        string_file = StringOutputFile()
        if in_file:
            f = open(in_file)
            if table_generator:
                table_generator.generate(f, string_file) 
            else:
                string_file.write(f.read())
        string_file.write("\n")
        return string_file.as_string()

    def generate_pxd_file(self):
        finalize_parse_args(self.s)
        s = self.s
        h_in = os.path.normpath(s.h_in)
        h_name = getattr(s, "h_name", None)
        h_name = os.path.normpath(h_name) if h_name else h_in
        h_in = find_file(self.s.h_path, h_name)
        out_dir = os.path.normpath(getattr(s, "out_dir", None))
        pxd_out = open_for_write(out_dir, s.pxd_out)
        pxd_in = getattr(s, "pxd_in", None)
        """
        pxd_in = find_file(self.s.pxd_path, pxd_in) if pxd_in else None
        """
        tg = TableGenerator()
        self.load_table_generator(tg)
        pxd_in = self.string_from_input(s.pxd_path, s.pxd_in, tg)
        nogil = getattr(s, "no_gil", False)
        pxd_from_h(pxd_out, h_in, pxd_in, h_name, nogil)
        pxd_out.close()
 

    def generate_pxi_file(self):
        finalize_parse_args(self.s)
        s = self.s
        """generate a .pxi file for the generated .pxd file"""
        # generate .pxi file
        if not s.pxi_in or not s.pxd_out:
           return
        out_dir = os.path.normpath(getattr(s, "out_dir", None))
        pxi_out = open_for_write(out_dir, s.pxi_out)
        pxi_out.write("""{0}
### Wrappers for C functions from file {1}
###
### File has been generated automatically. Do not change!
{0}

""".format("#" * 70, s.pxd_out)
        )
        """
        pxi_source_name = find_file(self.s.pxd_path, s.pxi_in)
        pxi_source_text = open(pxi_source_name).read()
        """
        tg = TableGenerator()
        self.load_table_generator(tg)
        pxi_source_text = self.string_from_input(s.pxd_path, s.pxi_in, tg)

        pxi_out.write(pxi_source_text)
        pxi_out.write("\n")

        pxd_source = os.path.join(out_dir, s.pxd_out)
        pxi_content = pxd_to_pxi(pxd_source, nogil = s.nogil)
        pxi_out.write(pxi_content)
        pxi_out.close()

    def generate(self):
        self.generate_pxd_file()
        self.generate_pxi_file()

    def activate_py_path(self):
        finalize_parse_args(self.s)
        s = self.s
        if not s.py_path:
            return
        if self.old_path:
            ERR = "Python path for class CodeGenerator object already active" 
            raise ValueError(ERR)
        self.old_path = [x for x in sys.path]
        for i, path in enumerate(s.py_path):
            sys.path.insert(i, path)

    def deactivate_py_path(self):
        finalize_parse_args(self.s)
        if not self.s.py_path or not self.old_path:
            return
        if sys.path != self.s.py_path + self.old_path:
            W = ("Could not deactivate python path for " 
                 "class CodeGenerator object")
            warnings.warn(W, UserWarning)
        else:
            del sys.path[:len(self.s.py_path)]

    def import_tables(self):
        finalize_parse_args(self.s)
        if getattr(self.s, "table_classes", None) is None:
            table_modules = self.s.tables
            mockup = self.s.mockup
            verbose = self.s.verbose
            table_classes = import_tables(table_modules, mockup, verbose)
            self.s.table_classes = table_classes    

    def load_table_generator(self, table_generator, params = {}):
        assert isinstance(table_generator, TableGenerator)
        #tables = {}
        #directives = {}
        tables = self.s.table_classes
        load_tables(table_generator, tables, params, False)

 
###############################################################################


def example():
    SAMPLE_ARGS = """ 
    """
    parser = generate_pcd_parser()
    s = parser.parse_args(SAMPLE_ARGS.split())
    print(s)
    print("\n")
    pg = pxdGenerator(s)
    print("")
    parser.print_help()


if __name__ == "__main__":
    example()

