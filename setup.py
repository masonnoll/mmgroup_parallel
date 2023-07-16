from __future__ import absolute_import, division, print_function


####################################################################
# History
####################################################################

VERSION = '0.0.12' # 2023-01-09. Support for the group Y_555 and the Bimonster
# VERSION = '0.0.11' # 2022-10-19. Bugfixes and macOS version added
# VERSION = '0.0.10' # 2022-10-11. Support for cibuildwheel added
# VERSION = '0.0.9' # 2022-09-01. Performance improved
# VERSION = '0.0.8' # 2022-07-12. Performance improved
# VERSION = '0.0.7' # 2021-12-01. Bugfix in version generation
# VERSION = '0.0.6' # 2021-12-01. Group operation accelerated
# VERSION = '0.0.5' # 2021-08-02. Word shortening in monster implemented
# VERSION = '0.0.4' # 2020-06-15. MSVC compiler is now supported
# VERSION = '0.0.3' # 2020-06-10. bugfixes in code generator
# VERSION = '0.0.2' # 2020-06-04. Order oracle added; bugfixes
# VERSION = '0.0.1' # 2020-05-20. First releae

# Version history must also be updated in the API Reference,
# section 'Version history'.

####################################################################
# Imports
####################################################################


import sys
import os
import re
import subprocess
import numpy as np
from glob import glob
import shutil

import setuptools
from setuptools import setup, find_namespace_packages
from collections import defaultdict


ROOTDIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(ROOTDIR)


from build_ext_steps import Extension, CustomBuildStep, SharedExtension
from build_ext_steps import BuildExtCmd, BuildExtCmdObj
from build_ext_steps import DistutilsPlatformError, DistutilsSetupError
   

import config
from config import EXTRA_COMPILE_ARGS, EXTRA_LINK_ARGS
from config import ROOT_DIR, SRC_DIR, PACKAGE_DIR, DEV_DIR
from config import REAL_SRC_DIR
from config import C_DIR, PXD_DIR


####################################################################
# Print command line arguments (if desired)
####################################################################


def print_commandline_args():
    print("Command line arguments of setup.py (in mmgroup project):")
    for arg in sys.argv:
        print(" " + arg)
    print("Current working directory os.path.getcwd():")
    print(" " + os.getcwd())
    print("Absolute path of file setup.py:")
    print(" " + os.path.abspath(__file__))
    print("")


print_commandline_args()


####################################################################
# Get output directory from command line arguments 
####################################################################

def get_output_directory_from_args():
    for i in range(len(sys.argv) - 1):
        if sys.argv[i] == "--dist-dir":
            return sys.argv[i + 1]
    return None


####################################################################
# Global options
####################################################################


STAGE = 1
# Parse a global option '--stage=i" and set variable ``STAGE``
# to the integer value i if such an option is present.
for i, s in enumerate(sys.argv[1:]):
    if s.startswith("--stage="):
        STAGE = int(s[8:])
        sys.argv[i+1] = None
    elif s[:1].isalpha:
        break
while None in sys.argv: 
    sys.argv.remove(None)


####################################################################
# Delete files
####################################################################


# The following files are before building the extension
# if the command line option -f or --force has been set
ext_delete = [
    os.path.join("C_DIR", "*.*"),
    os.path.join("PXD_DIR", "*.*"),
    os.path.join(PACKAGE_DIR, "*.dll"), 
    os.path.join(PACKAGE_DIR, "*.pyd"),
]


def force_delete():
    """Delete some files before command 'build_ext'"""
    if not "-f" in sys.argv and not  "--force" in sys.argv:
        return
    for file_pattern in ext_delete:
        for file in glob(file_pattern):
            try:
                #print(file)
                os.remove(file)
            except:
                pass
   


####################################################################
# create directories
####################################################################

def make_dir(*args):
    """Create subdirectory if it does not exist

    The path is given by the arguments
    """
    directory = os.path.realpath(os.path.join(*args))
    if not os.path.exists(directory):
        os.makedirs(directory)
    fname = os.path.join(directory, "readme.txt")
    with open(fname, "wt") as f:
        f.write(
"""The files in this directory have been created automatically
or copied from some other place.
So it is safe to delete all files in this directory.
"""
        )   

####################################################################
# extend path
####################################################################

def extend_path():
    sys.path.append(REAL_SRC_DIR)

####################################################################
# Check if we are in a 'readthedocs' environment
####################################################################


on_readthedocs = os.environ.get('READTHEDOCS') == 'True'



codegen_args = ["mockup"] if on_readthedocs else []

####################################################################
# Set path for shared libraries in linux
####################################################################

if not on_readthedocs and os.name == "posix":    
    old_ld_path = os.getenv("LD_LIBRARY_PATH")
    old_ld_path = old_ld_path + ";" if old_ld_path else ""
    new_LD_LIBRARY_PATH = os.path.abspath(PACKAGE_DIR)
    os.environ["LD_LIBRARY_PATH"] =  old_ld_path + new_LD_LIBRARY_PATH 


####################################################################
# Add extensions and shared libraries to package data
####################################################################


if os.name in ["nt"]:
    extension_wildcards =  ["*.pyd", "*.dll"]     
elif os.name in ["posix"]:
    extension_wildcards =  ["*.so"]  
else:   
    extension_wildcards =  []  


package_data = {
        # If any package contains *.txt or *.rst files, include them:
        "mmgroup": extension_wildcards
}




####################################################################
# Desription of the list 'general_presteps'.
#
# This is a list of programs to be run before executing the 'build_ext' 
# command. Each entry of list 'custom_presteps' is a list which we call 
# a program list. A program list ia a list of strings corresponding to 
# a program to be executed with:
#     subprocess.check_call(program_list) . 
# The first entry of a program list is the name of the program to be 
# executed; here sys.executable means the current python version. 
# Subsequents entries correspond to command line arguments.
#
# If the first entry in that list is not a string then it is 
# interpreted as a function to be called with the arguments
# given by the subsequent entries of that list.
####################################################################





pyx_sources = [
    os.path.join(DEV_DIR, "mat24", "mat24fast.pyx"),
    os.path.join(DEV_DIR, "generators", "generators.pyx"),
    os.path.join(DEV_DIR, "mm_basics", "mm_basics.pyx"),
    os.path.join(DEV_DIR, "mm_op", "mm_op.pyx"),
    os.path.join(DEV_DIR, "clifford12", "clifford12.pyx"),
    os.path.join(DEV_DIR, "mm_reduce", "mm_reduce.pyx"),
]

def copy_pyx_sources():
    for filename in pyx_sources:
        shutil.copy(filename, PXD_DIR)




general_presteps = CustomBuildStep("Starting code generation",
  [make_dir, "src", "mmgroup", "dev", "c_files"],
  [make_dir, "src", "mmgroup", "dev", "pxd_files"],
  [sys.executable, "cleanup.py", "-cx"],
  [force_delete],
  [copy_pyx_sources],
  [extend_path],
)

if STAGE > 1:
    general_presteps = CustomBuildStep("Starting code generation",
       [copy_pyx_sources],
       [extend_path],
    )

####################################################################
# We have to divide the code generation process 
# into stages, since a library built in a certain stage may be 
# for generating the code used in a subsequent stage.
####################################################################





####################################################################
# Building the extenstions at stage 1
####################################################################


DIR_DICT = {
   "SRC_DIR" : SRC_DIR,
   "C_DIR" : C_DIR,
   "DEV_DIR" : DEV_DIR,
   "PXD_DIR" : PXD_DIR,
}

DIR_DICT["MOCKUP"] = "--mockup\n" if on_readthedocs else ""

def get_c_names(s):
    process = [sys.executable, "generate_code.py", "--output-c-names"
           ] + s.split()
    try:
        ls = subprocess.run(process, text = True,
               stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        ls.check_returncode()
    except subprocess.CalledProcessError as e:
        print("Error:\nreturn code: ", e.returncode, 
              "\nOutput:" )
        print(e.stdout)
        print(e.stderr)
        raise
    return(ls.stdout).split()
    

MAT24_GENERATE = """
 -v
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/mat24
 --out-dir {C_DIR}
 --tables mmgroup.dev.mat24.mat24_ref 
 --sources mat24_functions.h
 --out-header mat24_functions.h
 --sources mat24_functions.ske mat24_random.ske
""".format(**DIR_DICT)

MAT24_GENERATE_PXD = """
 -v
 --pxd-path {SRC_DIR}/mmgroup/dev/mat24
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --h-in  mat24_functions.h
 --pxd-in  mat24_functions.pxd
 --pxd-out mat24_functions.pxd
""".format(**DIR_DICT)



# print(get_c_names(MAT24_GENERATE))


GENERATORS_GENERATE = """
 -v
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/generators
 --out-dir {C_DIR}
 --tables mmgroup.dev.generators.gen_cocode_short
          mmgroup.dev.generators.gen_leech_reduce_n 
          mmgroup.dev.generators.gen_xi_ref
 --sources mmgroup_generators.h
 --out-header mmgroup_generators.h
 --sources gen_xi_functions.ske mm_group_n.ske gen_leech.ske 
           gen_leech_type.ske gen_leech3.ske gen_leech_reduce.ske
           gen_leech_reduce_n.ske gen_random.ske
""".format(**DIR_DICT)


GENERATORS_GENERATE_PXD = """
 -v
 --pxd-path {SRC_DIR}/mmgroup/dev/generators
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --h-in  mmgroup_generators.h
 --pxd-in  generators.pxd
 --pxd-out generators.pxd
 --pxi-in  generators.pxi
""".format(**DIR_DICT)






mat24_c_files = get_c_names(MAT24_GENERATE)
mat24_c_files += get_c_names(GENERATORS_GENERATE)
mat24_c_paths = [os.path.join(C_DIR, s) for s in mat24_c_files]


CLIFFORD12_GENERATE = """
 -v
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/clifford12
 --out-dir {C_DIR}
 --tables mmgroup.dev.clifford12.bit64_tables
 --sources clifford12.h
 --out-header clifford12.h
 --sources  qstate12.ske qstate12io.ske qmatrix12.ske
            bitmatrix64.ske uint_sort.ske xsp2co1.ske 
            leech3matrix.ske xsp2co1_elem.ske
            involutions.ske xsp2co1_traces.ske
            xsp2co1_map.ske
""".format(**DIR_DICT)



CLIFFORD12_GENERATE_PXD = """
 -v
 --pxd-path {SRC_DIR}/mmgroup/dev/clifford12
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --h-in  clifford12.h
 --pxd-in  clifford12.pxd
 --pxd-out clifford12.pxd
 --pxi-in  clifford12.pxd
""".format(**DIR_DICT)


clifford12_c_files = get_c_names(CLIFFORD12_GENERATE)
clifford12_c_paths = [os.path.join(C_DIR, s) for s in clifford12_c_files]


mat24_presteps = CustomBuildStep("Generating code for extension 'mat24'",
  [sys.executable, "generate_code.py"] + MAT24_GENERATE.split(),
  [sys.executable, "generate_pxd.py"] + MAT24_GENERATE_PXD.split(),
  [sys.executable, "generate_code.py"] + GENERATORS_GENERATE.split(),
  [sys.executable, "generate_pxd.py"] + GENERATORS_GENERATE_PXD.split(),
  [sys.executable, "generate_code.py"] + CLIFFORD12_GENERATE.split(),
  [sys.executable, "generate_pxd.py"] + CLIFFORD12_GENERATE_PXD.split(),
)


mat24_shared = SharedExtension(
    name = "mmgroup.mmgroup_mat24", 
    sources = mat24_c_paths,
    libraries = [], 
    include_dirs = [PACKAGE_DIR, C_DIR],
    library_dirs = [PACKAGE_DIR, C_DIR],
    extra_compile_args = EXTRA_COMPILE_ARGS,
    implib_dir = C_DIR,
    define_macros = [ ("MAT24_DLL_EXPORTS", None)],
)


shared_libs_before_stage1 = [
   mat24_shared.lib_name
] if not on_readthedocs else []
# Attribute ``lib_name`` of a instance of clsss ``SharedExtension``
# contains name of the library (or of the import library in Windows) 
# that has to be linked to a program using the shared library.






clifford12_shared = SharedExtension(
    name = "mmgroup.mmgroup_clifford12", 
    sources = clifford12_c_paths,
    include_dirs = [PACKAGE_DIR, C_DIR],
    library_dirs = [PACKAGE_DIR, C_DIR],
    libraries = shared_libs_before_stage1, 
    extra_compile_args = EXTRA_COMPILE_ARGS,
    implib_dir = C_DIR,
    define_macros = [ ("CLIFFORD12_DLL_EXPORTS", None)],
)


shared_libs_stage1 = shared_libs_before_stage1 + [
       clifford12_shared.lib_name
] if not on_readthedocs else []




mat24_extension = Extension("mmgroup.mat24",
        sources=[
            os.path.join(PXD_DIR, "mat24fast.pyx"),
        ],
        #libraries=["m"] # Unix-like specific
        include_dirs = [ C_DIR ],
        library_dirs = [PACKAGE_DIR, C_DIR ],
        libraries = shared_libs_stage1, 
        #runtime_library_dirs = ["."],
        extra_compile_args = EXTRA_COMPILE_ARGS, 
        extra_link_args = EXTRA_LINK_ARGS, 
)

generators_extension = Extension("mmgroup.generators",
        sources=[
            os.path.join(PXD_DIR, "generators.pyx"),
        ],
        #libraries=["m"] # Unix-like specific
        include_dirs = [ C_DIR ],
        library_dirs = [PACKAGE_DIR, C_DIR ],
        libraries = shared_libs_stage1, 
        #runtime_library_dirs = ["."],
        extra_compile_args = EXTRA_COMPILE_ARGS, 
        extra_link_args = EXTRA_LINK_ARGS, 
)


clifford12_extension =  Extension("mmgroup.clifford12",
        sources=[
            os.path.join(PXD_DIR, "clifford12.pyx"),
        ],
        #libraries=["m"] # Unix-like specific
        include_dirs = [ C_DIR ],
        library_dirs = [PACKAGE_DIR, C_DIR ],
        libraries = shared_libs_stage1, 
        #runtime_library_dirs = ["."],
        extra_compile_args = EXTRA_COMPILE_ARGS, 
        extra_link_args = EXTRA_LINK_ARGS, 
)


####################################################################
# Building new extenstions at stage 2
####################################################################


MM_GENERATE = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/mm_basics
               {SRC_DIR}/mmgroup/dev/mm_op
 --out-dir {C_DIR}
 --tables mmgroup.dev.mm_basics.mm_basics
          mmgroup.dev.mm_basics.mm_tables_xi
          mmgroup.dev.mm_basics.mm_aux
          mmgroup.dev.mm_basics.mm_tables
          mmgroup.dev.mm_basics.mm_crt
 --sources mm_basics.h
 --out-header mm_basics.h
 --sources  mm_aux.ske mm_tables.ske mm_group_word.ske
            mm_tables_xi.ske mm_crt.ske
""".format(**DIR_DICT)



MM_GENERATE_PXD = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --pxd-path {SRC_DIR}/mmgroup/dev/mm_basics
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --tables mmgroup.dev.mm_basics.mm_basics
 --h-in  mm_basics.h
 --pxd-in  mm_basics.pxd
 --pxd-out mm_basics.pxd
 --pxi-in  mm_basics.pxd
""".format(**DIR_DICT)



mm_c_files = get_c_names(MM_GENERATE)
mm_c_paths = [os.path.join(C_DIR, s) for s in mm_c_files]




MM_OP_SUB_GENERATE = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/mm_op
 --out-dir {C_DIR}
 --subst mm_op mm{{p}}_op
 --tables mmgroup.dev.mm_op.mm_op
          mmgroup.dev.mm_op.mm_op_xi
          mmgroup.dev.mm_op.mm_op_pi
          mmgroup.dev.mm_op.mm_op_xy
          mmgroup.dev.hadamard.hadamard_t
          mmgroup.dev.hadamard.hadamard_xi
 --sources mm_op_sub.h
 --out-header mm_op_sub.h
""".format(**DIR_DICT)

for p in [3, 7, 15, 31, 127, 255]:
   MM_OP_SUB_GENERATE += """
      --set p={p}
      --sources mm_op_defines.h
                mm_op_pi.ske
                mm_op_misc.ske
                mm_op_xy.ske
                mm_op_t.ske
                mm_op_xi.ske
                mm_op_word.ske
      """.format(p=p)


for p in [3, 15]:
   MM_OP_SUB_GENERATE += """
      --set p={p}
      --sources mm_op_rank_A.ske
                mm_op_eval_A.ske
      """.format(p=p)

for p in [15]:
   MM_OP_SUB_GENERATE += """
      --set p={p}
      --sources mm_op_eval_X.ske
      """.format(p=p)




MM_OP_P_GENERATE = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/mm_op
 --out-dir {C_DIR}
 --set C_DIR={C_DIR}
 --tables mmgroup.dev.mm_op.dispatch_p
 --sources mm_op_p.h
 --out-header mm_op_p.h
 --sources  mm_op_p_vector.ske mm_op_p_axis.ske
""".format(**DIR_DICT)


mm_op_c_files = get_c_names(MM_OP_SUB_GENERATE)
mm_op_c_files += get_c_names(MM_OP_P_GENERATE)
mm_op_c_paths = [os.path.join(C_DIR, s) for s in mm_op_c_files]






MM_OP_P_GENERATE_PXD = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --pxd-path {SRC_DIR}/mmgroup/dev/mm_op
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --tables mmgroup.dev.mm_basics.mm_basics
 --h-in  mm_op_p.h
 --pxd-in  mm_op.pxd
 --pxd-out mm_op_p.pxd
 --pxi-in  mm_op.pxd
""".format(**DIR_DICT)









mm_presteps =  CustomBuildStep("Code generation for modules mm and mm_op",
   [sys.executable, "generate_code.py"] + MM_GENERATE.split(),
   [sys.executable, "generate_pxd.py"] + MM_GENERATE_PXD.split(),
   [sys.executable, "generate_code.py"] + MM_OP_SUB_GENERATE.split(),
   [sys.executable, "generate_code.py"] + MM_OP_P_GENERATE.split(),
   [sys.executable, "generate_pxd.py"] + MM_OP_P_GENERATE_PXD.split(),
)


mm_shared =  SharedExtension(
    name = "mmgroup.mmgroup_mm_basics", 
    sources = mm_c_paths,
    libraries = shared_libs_stage1, 
    include_dirs = [PACKAGE_DIR, C_DIR],
    library_dirs = [PACKAGE_DIR, C_DIR],
    extra_compile_args = EXTRA_COMPILE_ARGS,
    implib_dir = C_DIR,
    define_macros = [ ("MM_BASICS_DLL_EXPORTS", None)],
)



mm_op_shared =  SharedExtension(
    name = "mmgroup.mmgroup_mm_op", 
    sources = mm_op_c_paths,
    libraries = shared_libs_stage1 + [mm_shared.lib_name], 
    include_dirs = [PACKAGE_DIR, C_DIR],
    library_dirs = [PACKAGE_DIR, C_DIR],
    extra_compile_args = EXTRA_COMPILE_ARGS,
    implib_dir = C_DIR,
    define_macros = [ ("MM_OP_DLL_EXPORTS", None)],
)


shared_libs_stage2 = shared_libs_stage1 + [
       mm_shared.lib_name, mm_op_shared.lib_name
] if not on_readthedocs else []




mm_extension = Extension("mmgroup.mm",
    sources=[
            os.path.join(PXD_DIR, "mm_basics.pyx"),
    ],
    #libraries=["m"] # Unix-like specific
    include_dirs = [ C_DIR ],
    library_dirs = [ PACKAGE_DIR, C_DIR ],
    libraries = shared_libs_stage2, 
            # for openmp add "libgomp" 
    #runtime_library_dirs = ["."],
    extra_compile_args = EXTRA_COMPILE_ARGS, 
            # for openmp add "-fopenmp" 
    extra_link_args = EXTRA_LINK_ARGS, 
            # for openmp add "-fopenmp" 
)





mm_op_extension = Extension("mmgroup.mm_op",
    sources=[
            os.path.join(PXD_DIR, "mm_op.pyx"),
    ],
    #libraries=["m"] # Unix-like specific
    include_dirs = [ C_DIR ],
    library_dirs = [ PACKAGE_DIR, C_DIR ],
    libraries = shared_libs_stage2, 
            # for openmp add "libgomp" 
    #runtime_library_dirs = ["."],
    extra_compile_args = EXTRA_COMPILE_ARGS, 
            # for openmp add "-fopenmp" 
    extra_link_args = EXTRA_LINK_ARGS, 
            # for openmp add "-fopenmp" 
)


mm_poststeps =  CustomBuildStep("Create substituts for legacy extensions",
   [sys.executable, "make_legacy_extensions.py", "--out-dir",
       os.path.join(SRC_DIR, "mmgroup")
   ] 
)




ext_modules = [
    general_presteps,
    mat24_presteps,
    mat24_shared,
    clifford12_shared, 
    mat24_extension,
    generators_extension,
    clifford12_extension,
    mm_presteps,
    mm_shared, 
    mm_op_shared, 
    mm_extension, 
    mm_op_extension, 
    mm_poststeps, 
]


if STAGE >= 2:
    ext_modules = ext_modules[:1] + ext_modules[-3:]




####################################################################
# Building the extenstions at stage 3
####################################################################


if STAGE >= 3:
    ext_modules = ext_modules[:1]


MM_REDUCE_GENERATE = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --source-path {SRC_DIR}/mmgroup/dev/mm_reduce
 --out-dir {C_DIR}
 --set p=15
 --tables mmgroup.dev.mm_op.mm_op
          mmgroup.dev.mm_reduce.order_vector_tables
          mmgroup.dev.mm_reduce.vector_v1_mod3
 --sources mm_reduce.h
 --out-header mm_reduce.h
 --sources  mm_order_vector.ske
            mm_order.ske
            mm_compress.ske
            mm_reduce.ske
            mm_suborbit.ske
            mm_shorten.ske
            mm_vector_v1_mod3.ske
""".format(**DIR_DICT)


mm_reduce_files = get_c_names(MM_REDUCE_GENERATE)
mm_reduce_paths = [os.path.join(C_DIR, s) for s in mm_reduce_files]






MM_REDUCE_GENERATE_PXD = """
 -v
 {MOCKUP}
 --py-path {SRC_DIR}
 --pxd-path {SRC_DIR}/mmgroup/dev/mm_reduce
 --h-path {C_DIR}
 --out-dir {PXD_DIR}
 --tables mmgroup.dev.mm_op.mm_op
 --h-in  mm_reduce.h
 --pxd-in  mm_reduce.pxd
 --pxd-out mm_reduce.pxd
 --pxi-in  mm_reduce.pxd
""".format(**DIR_DICT)





reduce_presteps =  CustomBuildStep("Code generation for modules mm_reduce",
   [sys.executable, "generate_code.py"] + MM_REDUCE_GENERATE.split(),
   [sys.executable, "generate_pxd.py"] + MM_REDUCE_GENERATE_PXD.split(),
)




mm_reduce =  SharedExtension(
    name = "mmgroup.mmgroup_mm_reduce", 
    sources = mm_reduce_paths,   
    libraries = shared_libs_stage2, 
    include_dirs = [PACKAGE_DIR, C_DIR],
    library_dirs = [PACKAGE_DIR, C_DIR],
    extra_compile_args = EXTRA_COMPILE_ARGS,
    implib_dir = C_DIR,
    define_macros = [ ("MM_REDUCE_DLL_EXPORTS", None)],
)


shared_libs_stage3 = shared_libs_stage2 + [
       mm_reduce.lib_name
] if not on_readthedocs else []


mm_reduce_extension = Extension("mmgroup.mm_reduce",
    sources=[
            os.path.join(PXD_DIR, "mm_reduce.pyx"),
    ],
    #libraries=["m"] # Unix-like specific
    include_dirs = [ C_DIR ],
    library_dirs = [ PACKAGE_DIR, C_DIR ],
    libraries = shared_libs_stage3, 
            # for openmp add "libgomp" 
    #runtime_library_dirs = ["."],
    extra_compile_args = EXTRA_COMPILE_ARGS, 
            # for openmp add "-fopenmp" 
    extra_link_args = EXTRA_LINK_ARGS, 
            # for openmp add "-fopenmp" 
)




ext_modules += [
    reduce_presteps,
    mm_reduce,
    mm_reduce_extension,
]


####################################################################
# Patching shared libraries for Linux version
####################################################################


def build_posix_wheel():
    """This does not work!!!"""
    assert  os.name == "posix"
    if not on_readthedocs and "bdist_wheel" in sys.argv:
        PROJECT_NAME = r"mmgroup"
        SUFFIX_MATCH = r"[-0-9A-Za-z._]+linux[-0-9A-Za-z._]+\.whl"
        DIST_DIR = "dist"
        w_match = re.compile(PROJECT_NAME + SUFFIX_MATCH)
        wheels = [s for s in os.listdir(DIST_DIR) if w_match.match(s)]
        for wheel in wheels:
            wheel_path = os.path.join(DIST_DIR, wheel)
            args = ["auditwheel", "-v", "repair", wheel_path]
            print(" ".join(args))
            subprocess.check_call(args)



if not on_readthedocs:
    patch_step =  CustomBuildStep(
        "Patching and copying shared libraries",
        [sys.executable, "linuxpatch.py", "-v", "--dir",
        os.path.join(SRC_DIR, "mmgroup")
        ] 
    )
    ext_modules.append(patch_step)


####################################################################
# After building the externals we add a tiny little test step.
####################################################################



test_step = CustomBuildStep("import_all",
  [sys.executable, "import_all.py"],
  ["pytest",  "src/mmgroup/", "-v", "-s", "-m", "build"],
)


ext_modules.append(test_step)



####################################################################
# Don't build any externals when building the documentation.
####################################################################


if on_readthedocs:
    ext_modules = [ 
        general_presteps,
        mat24_presteps,
        mm_presteps,
        reduce_presteps,
    ]

   

def read(fname):
    """Return the text in the file with name 'fname'""" 
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


####################################################################
# The main setup program.
####################################################################


### Prelimiary!!!
"""
ext_modules = [
    mat24_presteps,
    clifford12_shared, 
    clifford12_extension,
]
"""

if os.name ==  "posix": 
   EXCLUDE = ['*.dll', '*.pyd', '*.*.dll', '*.*.pyd'] 
elif os.name ==  "nt": 
   EXCLUDE = ['*.so', '*.*.so'] 
else:
   EXCLUDE = [] 



setup(
    name = 'mmgroup',    
    version = VERSION,    
    license='BSD-2-Clause',
    description='Implementation of the sporadic simple monster group.',
    long_description=read('README.rst'),
    author='Martin Seysen',
    author_email='m.seysen@gmx.de',
    url='https://github.com/Martin-Seysen/mmgroup',
    packages=find_namespace_packages(
        where = 'src',
        exclude = EXCLUDE
    ),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=False,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        #'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        #'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    project_urls={
       # 'Changelog': 'yet unknown',
       'Issue Tracker': 'https://github.com/Martin-Seysen/mmgroup/issues',
    },
    keywords=[
        'sporadic group', 'monster group', 'finite simple group'
    ],
    python_requires='>=3.6',
    install_requires=[
         'numpy', 'regex',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    setup_requires=[
        'numpy', 'pytest-runner', 'cython', 'regex',
        # 'sphinx',  'sphinxcontrib-bibtex',
    ],
    tests_require=[
        'pytest', 'numpy', 'regex',
    ],
    cmdclass={
        'build_ext': BuildExtCmd,
    },
    ext_modules = ext_modules,
    package_data = package_data,
    include_dirs=[np.get_include()],  # This gets all the required Numpy core files
)



