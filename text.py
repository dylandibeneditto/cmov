from src.cmov import *
from src.cmov.components import *
from PIL import ImageFont

if __name__ == "__main__":
    scene = Scene(1080, 1080, fps=30)

    aligns = [
        Align.TOP_LEFT, Align.LEFT, Align.BOTTOM_LEFT,
        Align.TOP, Align.CENTER, Align.BOTTOM,
        Align.TOP_RIGHT, Align.RIGHT, Align.BOTTOM_RIGHT
    ]

    for i, align in enumerate(aligns):
        x = 540
        y = 100 + i * 100
        # Insert background box behind text
        box_width = 64
        box_height = 2 * 32  # Two lines of text at size 32
        bg = Box(x=x-box_width//2, y=y-box_height//2, width=box_width, height=box_height, color="#222222")
        scene.play(bg.fadein(), "0.5s")
        txt = Text(
            text=f"{align.name}\nMultiline", 
            x=x, y=y, size=64, color="#%02x%02x%02x" % (255 - i*20, 100 + i*10, 150),
            align=align, multiline=True, line_spacing=2
        )
        aligned_pos = get_aligned_position(txt.x, txt.y, txt.width, txt.height, align)
        background = Box(
            x=aligned_pos[0], y=aligned_pos[1], width=txt.width, height=txt.height, color="#101010"
        )
        scene.play(CompositeAnimation.parallel(background.fadein(), txt.fadein()), "0.5s")

    scene.render()