bl_info = {
    "name": "Camera Fitter",
    "author": "Odilkhan Yakubov",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Camera Fitter",
    "category": "Camera",
    "description": "Align and fit camera lens as in 3D View",
}

# Importing the viewer module
from . import viewer

__all__ = ['viewer']

# Register the addon
def register():
    viewer.register()

# Unregister the addon
def unregister():
    viewer.unregister()
