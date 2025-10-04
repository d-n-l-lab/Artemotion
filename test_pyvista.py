#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Quick test script to verify PyVista integration works correctly.
"""

import sys
from PySide6.QtWidgets import QApplication

# Test PyVista imports
try:
    import pyvista as pv
    print(f"✓ PyVista {pv.__version__} imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PyVista: {e}")
    sys.exit(1)

try:
    from pyvistaqt import QtInteractor
    print(f"✓ PyVistaQt imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PyVistaQt: {e}")
    sys.exit(1)

try:
    import vtk
    print(f"✓ VTK {vtk.vtkVersion.GetVTKVersion()} imported successfully")
except ImportError as e:
    print(f"✗ Failed to import VTK: {e}")
    sys.exit(1)

# Test our PyVista widget
try:
    from scripts.ui.widgets_3d.PyVistaWidget import PyVistaWidget
    print(f"✓ PyVistaWidget imported successfully")
except ImportError as e:
    print(f"✗ Failed to import PyVistaWidget: {e}")
    sys.exit(1)

# Test creating the widget
try:
    app = QApplication(sys.argv)
    widget = PyVistaWidget()
    print(f"✓ PyVistaWidget created successfully")
    
    # Test room creation
    widget.create_room()
    print(f"✓ Room created successfully")
    
    # Show widget briefly
    widget.show()
    widget.resize(800, 600)
    
    print("\n" + "="*60)
    print("SUCCESS! PyVista integration is working correctly.")
    print("="*60)
    print("\nThe 3D widget should now be displayed.")
    print("Close the window to exit.")
    
    sys.exit(app.exec())
    
except Exception as e:
    print(f"✗ Failed to create or use PyVistaWidget: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

