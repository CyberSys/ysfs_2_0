# -*- coding: utf-8 -*-
# ========================================
# YSFS 2.0 - YSFlight Tools for Blender
# Writen by u2fly (aka 'Symbian9')
# ========================================
bl_info = {
    "name": "YSFS 2.0 - Panel on toolshelf",
    "description": "YSFlight scripts for Blender 2.75+.",
    "author": "Symbian9",
    "version": (2, 0, 1),
    "blender": (2, 75, 0),
    "location": "1)Menu > Tool Shelf; 2)File > Export",
    "warning": "",
    "category": "Airplanes 3D",
    "wiki_url": "http://forum.ysfhq.com/viewtopic.php?t=8534",
    "tracker_url": "https://github.com/Symbian9/ysfs_2_0"
}
'''
CHANGELOG:
v2.0.0
	create panel "YSFS 2.0" for tool box;
v.2.0.1
	add export tabs on this panel (in export dialog too);
TODO:
    add NACA airfoil generator;
    add Game Property Visualyzer (display CLA);
	make single lable for export tabs;
	add "Game Property" dialog;
	add new options;
'''
# To support reload properly, try to access a package var, if it's there,
# reload everything
if "bpy" in locals():
	import imp
	if 'export_dnm' in locals():
		imp.reload(export_dnm)
	if 'export_srf' in locals():
		imp.reload(export_srf)
	if 'explode_srf' in locals():
		imp.reload(explode_srf)	

import bpy

from .export_dnm import ExportDNM
from .export_srf import ExportSRF
from .explode_srf import ExplodeSRF
# Make game property visual
# from .space_view3d_game_props_visualiser import 

####################
# YSFS Tools Panel
class VIEW3D_PT_ysfs_export_dnm(bpy.types.Panel):
    bl_label = "Export whole model"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "YSFS 2.0"
    def draw(self, context):
        self.layout.operator(ExportDNM.bl_idname, text = "DNM Model (.dnm)")

class VIEW3D_PT_ysfs_export_srf(bpy.types.Panel):
    bl_label = "Export one selected object"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "YSFS 2.0"
    def draw(self, context):
        self.layout.operator(ExportSRF.bl_idname, text = "SURF Model (.srf)")
        
class VIEW3D_PT_ysfs_explode_srf(bpy.types.Panel):
    bl_label = "Export all as parts"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "YSFS 2.0"    
    def draw(self, context):
        self.layout.operator(ExplodeSRF.bl_idname, text = "DNM Parts (.srf)")

# Menu Button
def menu_func_export_dnm(self, context):
    self.layout.operator(ExportDNM.bl_idname, text = "DNM Model (.dnm)")
    
def menu_func_export_srf(self, context):
    self.layout.operator(ExportSRF.bl_idname, text = "SURF Model (.srf)")
    
def menu_func_explode_srf(self, context):
    self.layout.operator(ExplodeSRF.bl_idname, text = "DNM Parts (.srf)")


# Regist
def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func_export_dnm)
    bpy.types.INFO_MT_file_export.append(menu_func_export_srf)
    bpy.types.INFO_MT_file_export.append(menu_func_explode_srf)
        
# Unregist
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_dnm)
    bpy.types.INFO_MT_file_export.remove(menu_func_export_srf)
    bpy.types.INFO_MT_file_export.remove(menu_func_explode_srf)
    
if __name__ == "__main__":
    register()
