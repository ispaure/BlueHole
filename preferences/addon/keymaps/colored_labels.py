"""Colored text in native lists without changing Blender's global theme.

UILayout exposes only the red alert color. Small cached text tiles use the
public preview API and retain native list selection, scrolling and tooltips.
No native UI pointers or persistent Blender data are used.
"""
from collections import OrderedDict
from math import ceil, sqrt

import blf
import bpy
import bpy.utils.previews
import gpu
from mathutils import Matrix

_previews = None
_labels = OrderedDict()
_serial = 0
_TILE = 32  # Twice the native 16-unit icon size, for high-DPI text.
_LIMIT = 256
AMBER = (1.0, 190 / 255, 45 / 255, 1.0)


def _fit(text, width):
    if blf.dimensions(0, text)[0] <= width:
        return text
    low, high = 0, len(text)
    while low < high:
        middle = (low + high + 1) // 2
        if blf.dimensions(0, text[:middle] + '…')[0] <= width:
            low = middle
        else:
            high = middle - 1
    return text[:low] + '…'


def _tiles(text, points):
    global _previews, _serial
    key = (text, points)
    if key in _labels:
        _labels.move_to_end(key)
        return _labels[key]
    if _previews is None:
        _previews = bpy.utils.previews.new()
    width = max(_TILE, ceil(blf.dimensions(0, text)[0] / _TILE) * _TILE)
    target = gpu.types.GPUOffScreen(width, _TILE)
    try:
        with target.bind():
            frame = gpu.state.active_framebuffer_get()
            frame.clear(color=(0, 0, 0, 0))
            with gpu.matrix.push_pop():
                gpu.matrix.load_matrix(Matrix.Identity(4))
                gpu.matrix.load_projection_matrix(Matrix(((2 / width, 0, 0, -1),
                    (0, 2 / _TILE, 0, -1), (0, 0, 1, 0), (0, 0, 0, 1))))
                blf.disable(0, blf.CLIPPING)
                blf.position(0, 0, 6, 0)
                blf.color(0, *AMBER)
                blf.draw(0, text)
            pixels = frame.read_color(0, 0, width, _TILE, 4, 0, 'FLOAT')
            pixels.dimensions = width * _TILE * 4
            pixels = list(pixels)
    finally:
        target.free()
    names = []
    for x in range(0, width, _TILE):
        name = str(_serial)
        _serial += 1
        tile = _previews.new(name)
        tile.icon_size = (_TILE, _TILE)
        tile.icon_pixels_float = [value for y in range(_TILE)
            for value in pixels[(y * width + x) * 4:(y * width + x + _TILE) * 4]]
        names.append(name)
    _labels[key] = names
    while len(_labels) > _LIMIT:
        _, retired = _labels.popitem(last=False)
        for name in retired:
            del _previews[name]
    return names


def label(layout, text, *, width):
    points = bpy.context.preferences.ui_styles[0].widget.points
    blf.size(0, points * 2)
    # Leave a full tile at the edge, so Blender never compresses icon cells.
    text = _fit(text, max(16, width - 16) * 2)
    names = _tiles(text, points)
    line = layout.row(align=True)
    line.alignment = 'LEFT'
    # Native layout scaling is applied when estimating and resolving icon cells.
    line.scale_x = sqrt(16 / 20)
    for name in names:
        line.label(text='', icon_value=_previews[name].icon_id)


def clear():
    global _previews, _serial
    if _previews is not None:
        bpy.utils.previews.remove(_previews)
        _previews = None
    _labels.clear()
    _serial = 0
