bl_info = {
    "name": "Project Setup",
    "author": "kursad-k",
    "version": (1, 4),
    "blender": (2, 80, 0),
    "location": "File > Project Setup",
    "description": "Setup project folders inspired by Maya, with correct labels and default input values as described.",
    "category": "System"
}

import bpy
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator, PropertyGroup
import os

# Maya standard folders
MAYA_FOLDERS = [
    "scenes",
    "images",
    "sourceimages",
    "render",
    "clips",
    "scripts",
    "sound",
    "movie",
    "autosave"
]

# Custom folders
CUSTOM_FOLDERS = [
    "Incoming",
    "Outgoing",
    "Export",
    "Reference",
    "BLENDER"
]

ALL_FOLDERS = MAYA_FOLDERS + CUSTOM_FOLDERS

class ProjectFolder(PropertyGroup):
    label: StringProperty(name="Label", default="")
    name: StringProperty(name="Folder Name", default="")

class PROJECTSETUP_OT_create_folders(Operator):
    bl_idname = "projectsetup.create_folders"
    bl_label = "Create Project Folders"
    bl_description = "Create project folders in the selected directory"

    root_path: StringProperty(
        name="Root Directory",
        description="Choose the root directory for the project setup",
        subtype='DIR_PATH'
    )
    folders: CollectionProperty(type=ProjectFolder)

    def execute(self, context):
        created = []
        for folder in self.folders:
            folder_name = folder.name.strip()
            if not folder_name:
                continue
            path = os.path.join(self.root_path, folder_name)
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
                    created.append(folder_name)
            except Exception as e:
                self.report({'WARNING'}, f"Could not create '{folder_name}': {e}")
        # Create workspace.py as empty file
        mel_path = os.path.join(self.root_path, "workspace.py")
        if not os.path.exists(mel_path):
            try:
                with open(mel_path, 'w') as f:
                    f.write('// workspace file\n')
            except Exception as e:
                self.report({'WARNING'}, f"Could not create workspace.py: {e}")

        self.report({'INFO'}, f"Created folders: {', '.join(created)}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # Only fill folders on first show
        if not self.folders:
            for folder_name in MAYA_FOLDERS:
                item = self.folders.add()
                item.label = folder_name      # left label
                item.name = folder_name       # right field default value
            for custom_name in CUSTOM_FOLDERS:
                item = self.folders.add()
                item.label = custom_name      # left label
                item.name = custom_name       # right field default value
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=400)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "root_path")
        layout.label(text="Edit folder names below before creating:")
        for folder in self.folders:
            row = layout.row()
            row.label(text=folder.label)
            row.prop(folder, "name", text="")

def menu_func(self, context):
    self.layout.operator(PROJECTSETUP_OT_create_folders.bl_idname, icon='FILE_FOLDER')

classes = [ProjectFolder, PROJECTSETUP_OT_create_folders]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file.append(menu_func)

def unregister():
    bpy.types.TOPBAR_MT_file.remove(menu_func)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
