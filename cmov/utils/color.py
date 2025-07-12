# Color utilities

def hex_to_rgba(hex_color, opacity=1.0):
    hex_color = hex_color.lstrip('#')
    lv = len(hex_color)
    rgb = tuple(int(hex_color[i:i+lv//3], 16) for i in range(0, lv, lv//3))
    return (*rgb, int(255 * opacity))
