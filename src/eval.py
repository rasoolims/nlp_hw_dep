import os,sys
from utils import *

uas,las = eval(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]))

print 'Unlabeled attachment score', round(uas,2)
print 'Labeled attachment score', round(las,2)
