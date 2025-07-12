from cmov import *
from cmov.components import *

if __name__ == "__main__":
    scene = Scene(800,800, fps=100)
    box = Box(100, 100)
    scene.wait("1s")
    scene.play(box.fadein(), "1s")
    scene.play(box.moveto(700,700), "1s")
    scene.play(box.moveto(400,400), "1s")
    scene.render()