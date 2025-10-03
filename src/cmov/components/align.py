from enum import Enum

class Align(Enum):
    TOP_LEFT = 0
    LEFT = 1
    BOTTOM_LEFT = 2
    TOP = 3
    CENTER = 4
    BOTTOM = 5
    TOP_RIGHT = 6
    RIGHT = 7
    BOTTOM_RIGHT = 8

def get_aligned_position(x, y, width, height, align: Align):
    """
    Returns the top-left (x, y) position for a box of given width/height aligned at (x, y) with the given Align.
    """
    if align == Align.CENTER:
        return x - width / 2, y - height / 2
    elif align == Align.TOP:
        return x - width / 2, y
    elif align == Align.BOTTOM:
        return x - width / 2, y - height
    elif align == Align.LEFT:
        return x, y - height / 2
    elif align == Align.RIGHT:
        return x - width, y - height / 2
    elif align == Align.TOP_LEFT:
        return x, y
    elif align == Align.TOP_RIGHT:
        return x - width, y
    elif align == Align.BOTTOM_LEFT:
        return x, y - height
    elif align == Align.BOTTOM_RIGHT:
        return x - width, y - height
    else:
        return x, y