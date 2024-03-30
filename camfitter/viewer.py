import bpy
import math
from bpy.types import Operator, Panel

class VIEW3D_OT_camera_fit_view(Operator):
    """Align and fit camera to view and match lens properties."""
    bl_idname = "view3d.camera_fit_view"
    bl_label = "Camera to View"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.space_data.region_3d.view_perspective != 'CAMERA'

    def execute(self, context):
        # Check if there's an active camera, otherwise create a new one
        if context.scene.camera is None:
            bpy.ops.object.camera_add()
            new_camera = context.object
            new_camera.name = "3D View Camera"  # Set camera name
            context.scene.camera = new_camera
        else:
            new_camera = context.scene.camera

        region = context.region
        rv3d = context.region_data
        width = region.width
        height = region.height

        # Get render resolution
        render = context.scene.render

        # Calculate scale factors for x and y
        scale_x = render.resolution_x / width
        scale_y = render.resolution_y / height

        view_camera_matrix = rv3d.view_matrix.inverted()
        view_camera_translation = view_camera_matrix.translation

        # Use the smaller scale factor to ensure camera fits within both dimensions
        scale = min(scale_x, scale_y)

        distance = math.sqrt(view_camera_translation.x ** 2 + view_camera_translation.y ** 2 + view_camera_translation.z ** 2)

        new_camera.location = view_camera_translation
        new_camera.rotation_euler = view_camera_matrix.to_euler()

        new_camera.data.sensor_width = 72
        new_camera.data.lens = context.scene.camera_fit_view_settings.custom_lens
        new_camera.data.clip_start = context.space_data.clip_start
        new_camera.data.clip_end = context.space_data.clip_end

        # Adjust the FOV based on the screen space
        fov_x = 2.0 * math.atan((width / 2.0 * scale) / distance)
        fov_y = 2.0 * math.atan((height / 2.0 * scale) / distance)
        fov = max(fov_x, fov_y)
        new_camera.data.lens = (width / 2.0 * scale) / math.tan(fov / 2.0)

        # Set active camera lens
        bpy.data.cameras[new_camera.data.name].lens = context.scene.camera_fit_view_settings.custom_lens

        # Update render resolution
        render.resolution_x = int(width * scale)
        render.resolution_y = int(height * scale)

        # Start rendering
        bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)

        return {'FINISHED'}

class CameraFitViewSettings(bpy.types.PropertyGroup):
    custom_lens: bpy.props.FloatProperty(
        name="Lens (mm)",
        default=50.0,
        min=1.0,
        update=lambda self, context: update_lens(self, context)
    )

def update_lens(self, context):
    cam = context.scene.camera
    if cam is not None:
        cam.data.lens = self.custom_lens

addon_keymaps = []

def register():
    bpy.utils.register_class(VIEW3D_OT_camera_fit_view)
    bpy.utils.register_class(CameraFitViewSettings)
    bpy.types.Scene.camera_fit_view_settings = bpy.props.PointerProperty(type=CameraFitViewSettings)

    # Register shortcut keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('view3d.camera_fit_view', 'F10', 'PRESS', ctrl=True)

        addon_keymaps.append((km, kmi))

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_camera_fit_view)
    bpy.utils.unregister_class(CameraFitViewSettings)
    del bpy.types.Scene.camera_fit_view_settings

    # Unregister shortcut keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
    addon_keymaps.clear()

if __name__ == "__main__":
    register()
