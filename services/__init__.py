import os

this_dir = os.path.dirname(os.path.abspath(__file__))

subdirs = filter(
    lambda x: os.path.isdir(os.path.join(this_dir,x)),
    os.listdir(this_dir)
)

for subdir in subdirs:
    print subdir


print subdirs
