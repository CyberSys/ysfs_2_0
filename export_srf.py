import os
import bpy
import bmesh
import mathutils
from bpy.props import (BoolProperty, FloatProperty, StringProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper, unpack_list, unpack_face_list, axis_conversion)

# Infomation
bl_info = {
    'name'       : 'YSFS 2.0 - SRF file',
    'description': 'YSFlight scripts | Export single selected object to SRF file.',
    'author'     : 'Symbian9, Mr Mofumofu',
    'version'    : (2, 0, 1),
    'blender'    : (2, 75, 0),
    'location'   : 'File > Import-Export',
    'warning'    : '',
    'wiki_url'   : '',
    'tracker_url': 'http://github.com/Symbian9/ysfs_2_0/issues/new',
    'category'   : 'Airplanes 3D',
}

def export(obj):
    # ==============================
    # Getting Data
    # ==============================
    # Convert to BMesh(For N-Sided Polygon)
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Transform
    ys_matrix = mathutils.Matrix((
        (-1.0,  0.0,  0.0,  0.0),
        ( 0.0,  0.0,  1.0,  0.0),
        ( 0.0, -1.0,  0.0,  0.0),
        ( 0.0,  0.0,  0.0,  1.0),
    ))
    bm.transform(ys_matrix * obj.matrix_world)
    bm.normal_update()
    # Set Axis
    local_axis = ys_matrix.to_3x3() * obj.location
    # Vertexs and Faces
    verts = bm.verts
    faces = bm.faces

    # ==============================
    # Output
    # ==============================
    output = ''
    za = ''
    zacount = 0

    # Header
    output += 'SURF\n'

    # Vertexs
    for vert in verts:
        vertex = vert.co - local_axis
        output += 'V {:.4f} {:.4f} {:.4f} '.format(*vertex)
        # Smoothing
        smooth = True
        for edge in vert.link_edges:
            if edge.smooth == False:
                smooth = False
                break
        if smooth:
            for face in vert.link_faces:
                if face.smooth:
                    output += 'R'
                    break
        output += '\n'

    # Faces
    for face in faces:
        output += 'F\n'

        # Has Material?
        if len(obj.material_slots):
            # Getting Material
            material = obj.material_slots[face.material_index].material
            # Color
            color = material.diffuse_color * 255.0
            output += 'C {:.0f} {:.0f} {:.0f}\n'.format(*color)
            # Lighting
            if material.emit > 0.0:
                output += 'B\n'
            # Transparent
            if material.alpha < 1.0:
                if zacount == 0:
                    za += 'ZA {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                elif zacount % 8 == 0:
                    za += '\nZA {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                else:
                    za += ' {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                zacount = zacount + 1

        # Median and Normal
        median = face.calc_center_median_weighted() - local_axis
        normal = -face.normal
        output += 'N {:.4f} {:.4f} {:.4f} '.format(*median)
        output += '{:.4f} {:.4f} {:.4f}\n'.format(*normal)

        # Vertexs consist Face
        output += 'V'
        for vid in face.verts:
            output += ' {:d}'.format(vid.index)
        output += '\n'
        output += 'E\n'

    # Footer
    output += 'E\n'

    # For Transparent
    if za != '':
        output += za + '\n'

    # ==============================
    # Close
    # ==============================
    bm.free()

    return output

# Export Form
class ExportSRF(bpy.types.Operator, ExportHelper):
    # Settings
    bl_idname = 'export_model.srf'
    bl_label = 'Export SRF'
    filter_glob = StringProperty(
        default = '*.srf',
        options = {'HIDDEN'},
    )
    check_extension = True
    filename_ext = '.srf'

    # On Click Save Button
    def execute(self, context):
        # Currently Scene
        scene = context.scene
        filepath = os.fsencode(self.filepath)
        fp = open(filepath, 'w')

        # Selected Object
        fp.write(export(scene.objects.active))

        return {'FINISHED'}

# Menu Button
def menu_func_export(self, context):
    self.layout.operator(ExportSRF.bl_idname, text = 'SRF Model (.srf)')

# Regist
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export)

# Unregist
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == '__main__':
    register()
