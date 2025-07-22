from PIL import Image, ImageDraw
from PIL import ImageFont
from ..core.component import Component
from ..core.animation import Animation
from ..core.composite_anim import CompositeAnimation
from ..easing.curves import *
from PIL import ImageFilter


class Character(Component):
    def __init__(self, char, x, y, size=12, color="#ffffff", opacity=1.0, font_path=None, font=None):
        super().__init__()
        self.char = char
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.blur = 0
        self.opacity = opacity
        self.font_path = font_path
        self.font = font

    def render(self, image, draw):
        font = self.font
        # Only create a small image for the character, not the full frame
        if hasattr(font, "getlength"):
            char_width = int(font.getlength(self.char))
        else:
            bbox = font.getbbox(self.char)
            char_width = bbox[2] - bbox[0] if bbox else self.size
        char_height = self.size * 2  # generous height for blur
        char_img = Image.new("RGBA", (char_width, char_height), (0, 0, 0, 0))
        char_draw = ImageDraw.Draw(char_img)
        fill = self._with_alpha(self.color, self.opacity)
        char_draw.text((0, 0), self.char, font=font, fill=fill)
        if self.blur > 0:
            char_img = char_img.filter(ImageFilter.GaussianBlur(self.blur))
        # Paste the blurred character at the correct position
        image.paste(char_img, (int(self.x), int(self.y)), char_img)

    def _with_alpha(self, color, opacity):
        if color.startswith('#'):
            color = color.lstrip('#')
            lv = len(color)
            rgb = tuple(int(color[i:i+lv//3], 16) for i in range(0, lv, lv//3))
            return (*rgb, int(255 * opacity))
        return color

class Text(Component):
    def __init__(self, text="", x=0, y=0, size=12, color="#ffffff", font_path="SF-Pro-Text-Medium.otf"):
        super().__init__()
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font_path = font_path
        self.characters = []
        self._init_characters()

    def _init_characters(self):
        self.characters = []
        try:
            font = ImageFont.truetype(self.font_path, self.size) if self.font_path else ImageFont.load_default()
        except IOError:
            font = ImageFont.load_default()
        x_cursor = self.x
        for char in self.text:
            self.characters.append(Character(char, x_cursor, self.y, self.size, self.color, opacity=0.0, font_path=self.font_path, font=font))
            if hasattr(font, "getlength"):
                char_width = font.getlength(char)
            else:
                bbox = font.getbbox(char)
                char_width = bbox[2] - bbox[0] if bbox else self.size
            x_cursor += char_width

    def render(self, image, draw):
        for char in self.characters:
            char.render(image, draw)

    def fadein(self, stagger="0.02s", easing=ease_out):
        return CompositeAnimation.stagger(*[
            CompositeAnimation.parallel(*[
                Animation(char, prop="opacity", start=0.2, end=1.0, easing=easing),
                (Animation(char, prop="y", start=self.y, end=self.y-self.size//2, easing=easing), 2),
                Animation(char, prop="blur", start=5, end=0.0, easing=easing)
            ]) for char in self.characters], stagger=stagger)

    def _with_alpha(self, color, opacity):
        if color.startswith('#'):
            color = color.lstrip('#')
            lv = len(color)
            rgb = tuple(int(color[i:i+lv//3], 16) for i in range(0, lv, lv//3))
            return (*rgb, int(255 * opacity))
        return color
