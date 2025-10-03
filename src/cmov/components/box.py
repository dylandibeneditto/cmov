from PIL import Image, ImageDraw
from ..core.component import Component
from ..core.animation import Animation
from ..core.composite_anim import CompositeAnimation
from ..easing.curves import ease_out

class Box(Component):
    def __init__(self, x=0, y=0, width=10, height=10, color="#ffffff"):
        super().__init__()
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.opacity = 1.0
        self.scale = 1.0
        self.color = color

    def render(self, image, draw):
        box_img = Image.new("RGBA", image.size, (0, 0, 0, 0))
        box_draw = ImageDraw.Draw(box_img)
        fill = self._with_alpha(self.color, self.opacity)
        scaled_w = self.w * self.scale
        scaled_h = self.h * self.scale
        box_draw.rectangle([round(self.x), round(self.y), round(self.x + scaled_w), round(self.y + scaled_h)], fill=fill)
        image.paste(box_img, (0, 0), box_img)

    def _with_alpha(self, color, opacity):
        if color.startswith('#'):
            color = color.lstrip('#')
            lv = len(color)
            rgb = tuple(int(color[i:i+lv//3], 16) for i in range(0, lv, lv//3))
            return (*rgb, int(255 * opacity))
        return color


    def bouncein(self):
        return CompositeAnimation.chain(
            CompositeAnimation.parallel(
                self.fadein(),
                self.scaleto(1.5)
            ),
            self.scaleto(1.0)
        )

    def fadein(self, easing=ease_out):
        self.opacity = 0
        self.y += self.h * self.scale
        return CompositeAnimation.parallel(
            Animation(self, prop="opacity", start=0.0, end=1.0, easing=easing),
            (Animation(self, prop="y", start=self.y, end=self.y-self.h * self.scale, easing=easing), 0.5)
        )

    def moveto(self, x, y, easing=ease_out):
        return CompositeAnimation.parallel(
            Animation(self, prop="x", start=self.x, end=x, easing=easing),
            Animation(self, prop="y", start=self.y, end=y, easing=easing)
        )


    def scaleto(self, scale, easing=ease_out):
        return Animation(
            component=self,
            prop="scale",
            start=self.scale,
            end=scale,
            easing=ease_out
        )
