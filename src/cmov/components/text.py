from PIL import Image, ImageDraw
from PIL import ImageFont
from ..core.component import Component
from ..core.animation import Animation
from ..core.composite_anim import CompositeAnimation
from ..easing.curves import *
from PIL import ImageFilter
from .align import Align

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
    def __init__(self, text="", x=0, y=0, size=12, color="#ffffff", font_path="SF-Pro-Text-Medium.otf",
                 align: Align = Align.TOP_LEFT, multiline=True, line_spacing=1.2):
        super().__init__()
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font_path = font_path
        self.align = align
        self.multiline = multiline
        self.line_spacing = line_spacing
        self.characters = []
        self.width, self.height = (0,0)
        self._init_characters()

    def _init_characters(self):
        from .align import get_aligned_position
        self.characters = []
        try:
            font = ImageFont.truetype(self.font_path, self.size) if self.font_path else ImageFont.load_default()
        except IOError:
            font = ImageFont.load_default()
        lines = self.text.split("\n") if self.multiline else [self.text]
        total_height = len(lines) * self.size * self.line_spacing
        line_widths = [sum(font.getlength(c) if hasattr(font, "getlength") else (font.getbbox(c)[2] - font.getbbox(c)[0] if font.getbbox(c) else self.size) for c in line) for line in lines]
        max_line_width = max(line_widths) if line_widths else 0

        # Get base position for the whole block
        base_x, base_y = get_aligned_position(self.x, self.y, max_line_width, total_height, self.align)
        #base_y += self.size * 0.4
        self.width = max_line_width
        self.height = total_height

        y_cursor = base_y
        for i, line in enumerate(lines):
            line_width = line_widths[i]
            # Get aligned position for each line
            line_x, _ = get_aligned_position(self.x, self.y, line_width, total_height, self.align)
            x_cursor = line_x
            for char in line:
                self.characters.append(Character(char, x_cursor, y_cursor, self.size, self.color, opacity=0.0, font_path=self.font_path, font=font))
                if hasattr(font, "getlength"):
                    char_width = font.getlength(char)
                else:
                    bbox = font.getbbox(char)
                    char_width = bbox[2] - bbox[0] if bbox else self.size
                x_cursor += char_width
            y_cursor += self.size * self.line_spacing

    def render(self, image, draw):
        for char in self.characters:
            char.render(image, draw)

    def fadein(self, stagger="0.02s", easing=ease_out_bounce):
        return CompositeAnimation.stagger(*[
            CompositeAnimation.parallel(*[
                Animation(char, prop="opacity", start=0.0, end=1.0, easing=easing),
                (Animation(char, prop="y", start=char.y+self.size*0.4, end=char.y, easing=easing), 2),
                Animation(char, prop="blur", start=2.0, end=0.0, easing=easing)
            ]) for char in self.characters], stagger=stagger)

    def fadeout(self, stagger="0.02s", easing=ease_in):
        return CompositeAnimation.stagger(*[
            CompositeAnimation.parallel(*[
                Animation(char, prop="opacity", start=1.0, end=0.0, easing=easing),
                (Animation(char, prop="y", start=char.y, end=char.y+self.size*0.4, easing=easing), 2),
                Animation(char, prop="blur", start=0.0, end=5.0, easing=easing)
            ]) for char in self.characters], stagger=stagger)

    def move_to(self, new_x, new_y, duration="0.5s", easing=ease_in_out):
        dx = new_x - self.x
        dy = new_y - self.y
        return CompositeAnimation.parallel(*[
            Animation(char, prop="x", start=char.x, end=char.x + dx, easing=easing)
            for char in self.characters
        ] + [
            Animation(char, prop="y", start=char.y, end=char.y + dy, easing=easing)
            for char in self.characters
        ])

    def _with_alpha(self, color, opacity):
        if color.startswith('#'):
            color = color.lstrip('#')
            lv = len(color)
            rgb = tuple(int(color[i:i+lv//3], 16) for i in range(0, lv, lv//3))
            return (*rgb, int(255 * opacity))
        return color
