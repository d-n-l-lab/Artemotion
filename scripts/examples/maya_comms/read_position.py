import os
import sys

if sys.platform == 'win32':
  mimic_path = 'D:\\OneDrive\\Documents\\maya\\modules'
elif sys.platform == 'darwin':
  mimic_path = '~/Library/Preferences/Autodesk/maya/modules'

print(mimic_path)
if mimic_path in sys.path:
  sys.path.remove(mimic_path)
sys.path.append(os.path.abspath(mimic_path))
print(sys.path)
try:
  from mimic.scripts import mimic_utils as mu
except ImportError:
  print('Either Maya is not running or no robot.')

print(mu.get_axis_val(1, False))
