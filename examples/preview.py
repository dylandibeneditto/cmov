from cmov.core.scene import Scene
from cmov.components.box import Box

if __name__ == "__main__":
    scene = Scene(800, 800, fps=30)
    box = Box(10, 10)
    scene.play(box.fadein(), "1s")
    # scene.render()  # To be implemented
