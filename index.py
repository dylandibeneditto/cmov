from cmov import *
from cmov.components import *

if __name__ == "__main__":
    scene = Scene(800,800, fps=100)
    text = [Text("Hola world lalalalalala", x=100, y=i*42+100, size=32, color="#ffffff") for i in range(10)]
    scene.play(CompositeAnimation.stagger(*[t.fadein() for t in text], stagger="0.1s"), "1s")
    scene.render()