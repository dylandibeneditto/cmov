from cmov import *
from cmov.components import *

if __name__ == "__main__":
    scene = Scene(800,800, fps=100)
    boxes = [Box(100, i*20+100) for i in range(10)]
    scene.play(CompositeAnimation.stagger(*[box.fadein() for box in boxes], stagger=5), "1s")
    scene.render()