class Animation:
    def __init__(self, component, prop, start, end, easing):
        self.component = component
        self.prop = prop
        self._initial_start = start
        self.end = end
        self.easing = easing

    def apply(self, t, duration, scene=None, start_value=None):
        # Always animate from self._initial_start to self.end
        start = self._initial_start
        if duration == 0:
            progress = 1.0
        else:
            progress = min(max(t / duration, 0.0), 1.0)

        eased = self.easing(progress)
        value = start + (self.end - start) * eased
        setattr(self.component, self.prop, value)
