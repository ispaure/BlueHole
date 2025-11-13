"""
Render utilities for Blue Hole. Hasn't been edited yet.
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
# DEBUG

show_verbose = True


# ----------------------------------------------------------------------------------------------------------------------
# CODE

def set_render_camera(camera_name):
    """
    Sets the default cameras to non-renderable and sets chosen camera as renderable.
    :param camera_name: Name of camera to set as render camera
    :type camera_name: str
    """
    pass


def set_render_resolution(width, height):
    """
    Sets the resolution of the render
    :param width: Width of render (in pixels)
    :type width: int
    :param height: Height of render (in pixels)
    :type height: int
    """
    pass


def set_render_settings_atlas(width=1024, height=1024):
    """
    Sets render settings for atlas baker
    """
    # Set transparency to depth peeling
    pass


def render_save(file_path):
    """
    Exports last render to file path (which must include extension). Right now, only detects tga/png but others could be
    recognized if properly added to this function.
    :param file_path: File path of exported file.
    :type file_path: str
    """
    pass
    
    return True
