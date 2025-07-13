from cmov import *
from cmov.components import *

if __name__ == "__main__":
    scene = Scene(800,800, fps=100)
    boxes = [Box(i*20+100, 100) for i in range(20)]
    scene.play(CompositeAnimation.stagger(*[box.fadein(easing=ease_out_bounce) for box in boxes], stagger="5"), "1s")
    scene.render()