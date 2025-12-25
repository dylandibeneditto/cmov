class Animation:
    def __init__(self, component, prop, start, end, easing):
        self.component = component
        self.prop = prop
        self._initial_start = start
        self.end = end
        self.easing = easing
        self._started = False
        self._actual_start = None

    def apply(self, t, duration, scene=None, start_value=None):
        if not self._started:
            if start_value is not None:
                self._actual_start = start_value
            else:
                self._actual_start = getattr(self.component, self.prop)
            self._started = True
        
        start = self._actual_start
        
        if duration == 0:
            progress = 1.0
        else:
            progress = min(max(t / duration, 0.0), 1.0)

        eased = self.easing(progress)
        value = start + (self.end - start) * eased
        setattr(self.component, self.prop, value)
