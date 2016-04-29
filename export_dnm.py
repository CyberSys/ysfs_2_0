import os
import bpy
import bmesh
import mathutils
from bpy.props import (BoolProperty, FloatProperty, StringProperty, EnumProperty)
from bpy_extras.io_utils import (ImportHelper, ExportHelper, unpack_list, unpack_face_list, axis_conversion)

# Infomation
bl_info = {
    'name'       : 'YSFS 2.0 - DNM file',
    'description': 'YSFlight scripts | Export all objects in scene to DNM file.',
    'author'     : 'Symbian9', 'Mr Mofumofu',
    'version'    : (2, 0, 1),
    'blender'    : (2, 75, 0),
    'location'   : 'File > Import-Export',
    'warning'    : '',
    'wiki_url'   : '',
    'tracker_url': 'http://github.com/Symbian9/ysfs_2_0/issues/new',
    'category'   : 'Airplanes 3D',
}

# Surface Class
class Surface:
    # Getting Data
    def __init__(self, obj, scene):
        self.obj = obj
        self.location = obj.location
        self.name = '{}.srf'.format(self.obj.name)
        self.uid = SurfMan().getUID()
        SurfMan().addUID()
        self.children = []

        for objs in (ob for ob in obj.children if ob.is_visible(scene) and ob.type == 'MESH'):
            self.children.append(SurfMan().getUID())
            SurfMan().addList(Surface(objs, scene))

    # PCK Node
    def pck(self):
        # ==============================
        # Getting Data
        # ==============================
        # Convert to BMesh(For N-Sided Polygon)
        bm = bmesh.new()
        bm.from_mesh(self.obj.data)
        # Transform
        ys_matrix = mathutils.Matrix((
            (-1.0,  0.0,  0.0,  0.0),
            ( 0.0,  0.0,  1.0,  0.0),
            ( 0.0, -1.0,  0.0,  0.0),
            ( 0.0,  0.0,  0.0,  1.0),
        ))
        bm.transform(ys_matrix * self.obj.matrix_world)
        bm.normal_update()
        # Set Axis
        local_axis = ys_matrix.to_3x3() * self.obj.location
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
            if len(self.obj.material_slots):
                # Getting Material
                material = self.obj.material_slots[face.material_index].material
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

        # Finalize
        length = len(output.split('\n')) - 1
        result = 'PCK {} {:d}\n{}\n'.format(self.name, length, output)

        # ==============================
        # Close
        # ==============================
        bm.free()

        return result

    #　SRF Node
    def srf(self):
        # ==============================
        # Getting Data
        # ==============================
        # Transform
        ys_matrix = mathutils.Matrix((
            (-1.0,  0.0,  0.0,  0.0),
            ( 0.0,  0.0,  1.0,  0.0),
            ( 0.0, -1.0,  0.0,  0.0),
            ( 0.0,  0.0,  0.0,  1.0),
        ))
        # Set Axis
        local_axis = ys_matrix.to_3x3() * self.obj.location

        # ==============================
        # Output
        # ==============================
        output = ''

        # Status
        output += 'SRF "{:d}"\n'.format(self.uid)
        output += 'FIL {}\n'.format(self.name)
        output += 'CLA 0\n'
        output += 'NST 0\n'

        # Support Axis Export
        if not isinstance(self.obj.parent, type(None)):
            local_axis_parent = ys_matrix.to_3x3() * self.obj.parent.location
            local_axis_pos = local_axis - local_axis_parent
            if local_axis_parent == (0, 0, 0):
                output += 'POS 0.0000 0.0000 0.0000 0 0 0 1\n'
                output += 'CNT {:.4f} {:.4f} {:.4f}\n'.format(*local_axis)
            else:
                output += 'POS {:.4f} {:.4f} {:.4f} 0 0 0 1\n'.format(*local_axis_pos)
                output += 'CNT 0.0000 0.0000 0.0000\n'
        else:
            output += 'POS 0.0000 0.0000 0.0000 0 0 0 1\n'
            output += 'CNT {:.4f} {:.4f} {:.4f}\n'.format(*local_axis)

        # Support Parent-Children Relation Export
        output += 'REL DEP\n'
        output += 'NCH {:d}\n'.format(len(self.children))
        for uid in self.children:
            output += 'CLD "{:d}"\n'.format(uid)
        output += 'END\n'

        return output

# Surface Manager
class SurfMan(object):
    _instance = None
    _list = []
    _saved = []
    _uid = 0

    # Singleton
    def __new__(this, *argarray, **argdict):
        if this._instance is None:
            this._instance = object.__new__(this, *argarray, **argdict)
        return this._instance

    # Add List
    def addList(self, obj):
        if not obj.name in self._saved:
            self._list.append(obj)
            self._saved.append(obj.name)


    # Get List
    def getList(self):
        return self._list

    # Add UID
    def addUID(self):
        self._uid = self._uid + 1

    # Get UID
    def getUID(self):
        return self._uid

    # Finalize
    def free(self):
        self._list = []
        self._saved = []
        self._uid = 0

# Export DNM
class ExportDNM(bpy.types.Operator, ExportHelper):
    # Settings
    bl_idname = 'export_model.dnm'
    bl_label = 'Export DNM Model'
    filter_glob = StringProperty(
        default = '*.dnm',
        options = {'HIDDEN'},
    )
    check_extension = True
    filename_ext = '.dnm'

    # On Click Save Button
    def execute(self, context):
        # ==============================
        # Getting Data
        # ==============================
        # Currently Scene
        scene = context.scene

        # Selected Object
        for obj in (ob for ob in scene.objects if ob.is_visible(scene) and ob.type == 'MESH'):
            if obj.type == 'MESH':
                SurfMan().addList(Surface(obj, scene))

        # ==============================
        # Output
        # ==============================
        # Save File
        filepath = os.fsencode(self.filepath)
        fp = open(filepath, 'w')

        # Header
        fp.write('DYNAMODEL\n')
        fp.write('DNMVER 1\n')

        # PCK Node
        for surf in SurfMan().getList():
            fp.write(surf.pck())

        # SRF Node
        for surf in SurfMan().getList():
            fp.write(surf.srf())

        # Footer
        fp.write('END\n')

        # ==============================
        # Close
        # ==============================
        SurfMan().free()
        fp.close()

        return {'FINISHED'}

# Menu Button
def menu_func_export(self, context):
    self.layout.operator(ExportDNM.bl_idname, text = 'DNM Model (.dnm)')

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
