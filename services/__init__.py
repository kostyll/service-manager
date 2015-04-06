import os
import importlib

this_dir = os.path.dirname(os.path.abspath(__file__))

subdirs = filter(
    lambda x: os.path.isdir(os.path.join(this_dir,x)),
    os.listdir(this_dir)
)

__all__ = []

os.sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

for subdir in subdirs:
    setattr(os.sys.modules[__name__],subdir, importlib.import_module(subdir))
    __all__.append(subdir)

print  __all__
