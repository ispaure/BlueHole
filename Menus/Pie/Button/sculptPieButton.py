"""
Pie Menus pertaining to Blender (Vanilla) for sculpting. These do not rely on external resources.
"""

# ----------------------------------------------------------------------------------------------------------------------
# AUTHORSHIP INFORMATION - THIS FILE BELONGS TO THE BLUE HOLE BLENDER PLUGIN https://blue-hole.weebly.com

__author__ = 'Marc-André Voyer'
__copyright__ = 'Copyright (C) 2020-2025, Marc-André Voyer'
__license__ = "MIT License"
__maintainer__ = 'Marc-André Voyer'
__email__ = 'marcandre.voyer@gmail.com'
__status__ = 'Production'

# ----------------------------------------------------------------------------------------------------------------------
# IMPORTS
import enum
# ----------------------------------------------------------------------------------------------------------------------
# PIE MENU BUTTON


# ----------------------------------------------------------------------------------------------------------------------
# Sculpt


class BlenderBrush(enum.Enum):
    GRAB = "Grab"
    CLAY = "Clay"
    FLATTEN_CONTRAST = "Flatten/Contrast"
    DRAW = "Draw"
    DRAW_SHARP = "Draw Sharp"
    POSE = "Pose"
    CLAY_STRIPS = "Clay Strips"
    CLAY_THUMB = "Clay Thumb"
    CREASE_POLISH = "Crease Polish"
    CREASE_SHARP = "Crease Sharp"
    DEFLATE = "Deflate"
    LAYER = "Layer"
    FILL_DEEPEN = "Fill/Deepen"
    PLATEAU = "Plateau"
    SCRAPE_MULTIPLANE = "Scrape Multiplane"
    SCRAPE_FILL = "Scrape/Fill"
    BLOB = "Blob"
    SMOOTH = "Smooth"
    TRIM = "Trim"
    BOUNDARY = "Boundary"
    ELASTIC_GRAB = "Elastic Grab"
    ELASTIC_SNAKE_HOOK = "Elastic Snake Hook"
    GRAB_2D = 'Grab 2D'
    GRAB_SILHOUETTE = 'Grab Silhouette'
    NUDGE = 'Nudge'
    PINCH_MAGNIFY = 'Pinch/Magnify'
    PULL = 'Pull'
    RELAX_PINCH = 'Relax Pinch'
    RELAX_SLIDE = 'Relax Slide'
    SNAKE_HOOK = 'Snake Hook'
    THUMB = 'Thumb'
    TWIST = 'Twist'
    DENSITY = 'Density'
    ERASE_MULTIRES_DISPLACEMENT = 'Erase Multires Displacement'
    FACE_SET_PAINT = 'Face Set Paint'
    MASK = 'Mask'
    SMEAR_MULTIRES_DISPLACEMENT = 'Smear Multires Displacement'
    AIRBRUSH = 'Airbrush'
    BLEND_HARD = 'Blend Hard'
    BLEND_SOFT = 'Blend Soft'
    BLEND_SQUARE = 'Blend Square'
    PAINT_BLEND = 'Paint Blend'
    PAINT_HARD = 'Paint Hard'
    PAINT_HARD_PRESSURE = 'Paint Hard Pressure'
    PAINT_SOFT = 'Paint Soft'
    PAINT_SOFT_PRESSURE = 'Paint Soft Pressure'
    PAINT_SQUARE = 'Paint Square'
    SHARPEN = 'Sharpen'
    SMEAR = 'Smear'
    BEND_BOUNDARY_CLOTH = 'Bend Boundary Cloth'
    BEND_TWIST_CLOTH = 'Bend/Twist Cloth'
    DRAG_CLOTH = 'Drag Cloth'
    EXPAND_CONTRACT_CLOTH = 'Expand/Contract Cloth'
    GRAB_CLOTH = 'Grab Cloth'
    GRAB_PLANAR_CLOTH = 'Grab Planar Cloth'
    GRAB_RANDOM_CLOTH = 'Grab Random Cloth'
    INFLATE_CLOTH = 'Inflate Cloth'
    PINCH_FOLDS_CLOTH = 'Pinch Folds Cloth'
    PINCH_POINT_CLOTH = 'Pinch Point Cloth'
    PUSH_CLOTH = 'Push Cloth'
    STRETCH_MOVE_CLOTH = 'Stretch/Move Cloth'
    TWIST_BOUNDARY_CLOTH = 'Twist Boundary Cloth'


def brush(pie, brush: BlenderBrush):
    op = pie.operator("brush.asset_activate", text=brush.value, icon='BRUSHES_ALL')
    op.asset_library_type = 'ESSENTIALS'
    op.asset_library_identifier = ''
    op.relative_asset_identifier = f'brushes/essentials_brushes-mesh_sculpt.blend/Brush/{brush.value}'
