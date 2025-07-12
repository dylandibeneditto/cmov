class Component:
    def __init__(self):
        self.visible = True

    def render(self, image, draw):
        """
        Override in subclasses to draw the component on the image.
        """
        raise NotImplementedError("render() must be implemented by subclasses.")

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
