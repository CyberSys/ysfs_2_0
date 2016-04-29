import os
import bpy
import bmesh
import mathutils
from bpy.props import (BoolProperty, FloatProperty, StringProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper, unpack_list, unpack_face_list, axis_conversion)

# Infomation
bl_info = {
    'name'       : 'YSFS 2.0 - DNM Parts as SRF file',
    'description': 'YSFlight scripts | Export all objects in scene to DNM with separated parts as SRF files.',
    'author'     : 'Symbian9, Mr Mofumofu',
    'version'    : (2, 0, 1),
    'blender'    : (2, 75, 0),
    'location'   : 'File > Import-Export',
    'warning'    : '',
    'wiki_url'   : '',
    'tracker_url': 'http://github.com/Symbian9/ysfs_2_0/issues/new',
    'category'   : 'Airplanes 3D',
}

# Export Form
class ExplodeSRF(bpy.types.Operator, ExportHelper):
    # Settings
    bl_idname = 'export_model.expsrf'
    bl_label = 'Export DNM Parts(SURF)'
    filter_glob = StringProperty(
        default = '*.srf',
        options = {'HIDDEN'},
    )
    check_extension = True
    filename_ext = '.srf'

    # On Click Save Button
    def execute(self, context):
        # ==============================
        # Getting Data
        # ==============================
        # Currently Scene
        scene = context.scene
        # Rotation(Option)
        global_matrix = mathutils.Matrix((
            (-1.0,  0.0,  0.0,  0.0),
            ( 0.0,  0.0,  1.0,  0.0),
            ( 0.0, -1.0,  0.0,  0.0),
            ( 0.0,  0.0,  0.0,  1.0),
        ))
        # Selected Object
        for object in scene.objects:
            export(object, self.filepath, global_matrix)
        return {'FINISHED'}

def export(object, filepath, global_matrix):
    me = object.data
    for objects in object.children:
        export(objects, filepath, global_matrix)
    if isinstance(me, bpy.types.Mesh):
        # Convert to BMesh(For N-Sided Polygon)
        bm = bmesh.new()
        bm.from_mesh(me)
        # Rotation(Option)
        bm.transform(global_matrix * object.matrix_world)
        bm.normal_update()

        # Vertexs and Faces
        verts = bm.verts
        faces = bm.faces

        # ==============================
        # Output
        # ==============================
        # Save File
        filepath = '{0}/{1}.srf'.format(os.path.dirname(filepath), object.name)
        filepath = os.fsencode(filepath)
        fp = open(filepath, 'w')

        # For Transparent
        za = ''
        zacount = 0

        # Header
        fp.write('SURF\n')

        # Vertexs
        for vert in verts:
            fp.write('V {:.4f} {:.4f} {:.4f} '.format(*vert.co))
            # Smoothing
            smooth = True
            for edge in vert.link_edges:
                if edge.smooth == False:
                    smooth = False
                    break
            if smooth:
                for face in vert.link_faces:
                    if face.smooth:
                        fp.write('R')
                        break
            fp.write('\n')

        # Faces
        for face in faces:
            fp.write('F\n')

            # Has Material?
            if len(object.material_slots):
                # Getting Material
                material = object.material_slots[face.material_index].material
                # Color
                color = material.diffuse_color * 255.0
                fp.write('C {:.0f} {:.0f} {:.0f}\n'.format(*color))
                # Lighting
                if material.emit > 0.0:
                    fp.write('B\n')
                # Transparent
                if material.alpha < 1.0:
                    if zacount == 0:
                        za = 'ZA {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                    elif zacount % 8 == 0:
                        za += '\nZA {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                    else:
                        za += ' {:d} {:.0f}'.format(face.index, (1.0 - material.alpha) * 228.0)
                    zacount = zacount + 1

            # Median and Normal
            median = face.calc_center_median_weighted()
            normal = -face.normal
            fp.write('N {:.4f} {:.4f} {:.4f} '.format(*median))
            fp.write('{:.4f} {:.4f} {:.4f}\n'.format(*normal))

            # Vertexs consist Face
            fp.write('V')
            for vid in face.verts:
                fp.write(' {:d}'.format(vid.index))
            fp.write('\n')

            fp.write('E\n')

        # Footer
        fp.write('E\n')

        # For Transparent
        if za != '':
            fp.write(za + '\n')

        # ==============================
        # Close
        # ==============================
        fp.close()
        bm.free()

        return {'FINISHED'}

# Menu Button
def menu_func_export(self, context):
    self.layout.operator(ExplodeSRF.bl_idname, text = 'DNM Parts (.srf)')

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
