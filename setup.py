#
# setup.py file for Python Robotics

# BUILD
#   python setup.py build
#
# INSTALL (usually as root)
#   python setup.py install

from distutils.core import setup, Extension
from distutils import sysconfig

std_macros = [("_POSIX_THREADS", None), 
              ("_POSIX_THREAD_SAFE_FUNCTIONS", None),
              ("_REENTRANT", None),
              ("POSIX", None), 
              ("__x86__", None), 
              ("__linux__", None), 
              ("__OSVERSION__", 2), 
              ("USINGTHREADS", None), 
              ("LINUX", None), 
              ("_GNU_SOURCE", None)]

std_library_dirs = ["/usr/X11R6/lib"]
std_libraries = ["stdc++", "X11", "Xt", "Xm", "dl", "pthread", "Xp", "Xext"]

setup(name = "pythonrobotics",
      version = "2.2.3",
      description = "Robotics packages including vision, neural net, and genetic algorithm components in Python and C",
      author = "",
      url = "http://emergent.brynmawr.edu/~dblank/pyro/",

      # Compile extension modules
      ext_modules = [Extension("pyro.brain.psom._csom", 
                       ["brain/psom/csom_src/som_pak.i"],
                       include_dirs = [sysconfig.get_python_inc(), "brain/psom/csom_src/som_pak-dev"]),
                     Extension("pyro.camera.device.Device", 
                       ["camera/device/Device.cpp"],
                       include_dirs = [sysconfig.get_python_inc()],
                       library_dirs = std_library_dirs,
                       libraries = std_libraries,
                       define_macros = std_macros,
                       extra_compile_args = ["-frepo"]),
                     Extension("pyro.camera.blob._blob", 
                       ["camera/blob/Blob.cpp", "camera/blob/Blob.i"],
                       include_dirs = [sysconfig.get_python_inc(), "camera/device/"],
                       library_dirs = std_library_dirs,
                       libraries = std_libraries.append("../device/Device.o"),
                       define_macros = std_macros,
                       extra_compile_args = ["-frepo", "-shared"]),
                    ],

      # Python packages
      package_dir = {"": "../"},
      packages = [ "pyro.brain/behaviors",
                   "pyro.brain",
                   "pyro.brain/psom",
                   "pyro.brain/VisConx",
                   "pyro.camera/blob",
                   "pyro.camera",
                   "pyro.camera/fake",
                   "pyro.camera/v4l",
                   "pyro.engine",
                   "pyro.geometry",
                   "pyro.gui/3DArray",
                   "pyro.gui",
                   "pyro.gui/canvas",
                   "pyro.gui/plot",
                   "pyro.gui/renderer",
                   "pyro.gui/viewer",
                   "pyro.gui/widgets/TKwidgets",
                   "pyro.gui/widgets",
                   "pyro.plugins/brains",
                   "pyro.plugins",
                   "pyro.plugins/robots",
                   "pyro.plugins/services",
                   "pyro.plugins/maps",
                   "pyro.plugins/views",
                   "pyro.robot/driver/armor",
                   "pyro.robot/driver",
                   "pyro.robot/driver/khepera",
                   "pyro.robot/driver/saphira",
                   "pyro.robot/driver/testc",
                   "pyro.robot/driver/video",
                   "pyro.robot/driver/b21r",
                   "pyro.robot",
                   "pyro.robot/sensor",
                   "pyro.simulators",
                   "pyro.simulators/khepera/CNTRL",
                   "pyro.simulators/khepera",
                   "pyro.system",
                   "pyro.tools/cluster",
                   "pyro.tools",
                   "pyro.vision",
                   "pyro.vision/cblob",
                   "pyro.vision/cvision",
                   "pyro.map",
                   "pyro.general",
                   "pyro.ai",
                   "pyro"
                   ]
     )

