class Component:
    def __init__(self):
        self.visible = True
        self.z_index = 0

    def render(self, image, draw):
        """
        Override in subclasses to draw the component on the image.
        """
        raise NotImplementedError("render() must be implemented by subclasses.")

    def set_z_index(self, z: int):
        self.z_index = z

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
