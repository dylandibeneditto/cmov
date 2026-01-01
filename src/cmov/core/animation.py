class Animation:
    def __init__(self, component, prop, start, end, easing):
        self.component = component
        self.prop = prop
        # start or end may be None to indicate "capture at first apply"
        self._initial_start = start
        self._initial_end = end
        self.easing = easing

        # Internal per-animation runtime values (captured on first apply)
        self._started = False
        self._actual_start = None
        self._actual_end = None

    def apply(self, t, duration, scene=None, start_value=None):
        """
        Apply animation at time t (frames). If start or end were provided as None,
        capture the component's current property value on first apply.

        The renderer may pass `start_value` (cached segment start) — prefer that
        if provided for the actual start.
        """
        if not self._started:
            # Determine actual start. Prefer an explicitly provided start value
            # from the Animation constructor. Only fall back to renderer-provided
            # start_value (which is the component's value at segment start) when
            # the animation did not specify an explicit start.
            if self._initial_start is not None:
                self._actual_start = self._initial_start
            elif start_value is not None:
                self._actual_start = start_value
            else:
                self._actual_start = getattr(self.component, self.prop)

            # Determine actual end. Prefer an explicitly provided end value from
            # the Animation constructor; otherwise capture the current component
            # value as the target.
            if self._initial_end is not None:
                self._actual_end = self._initial_end
            else:
                self._actual_end = getattr(self.component, self.prop)

            self._started = True

        start = self._actual_start
        end = self._actual_end

        if duration == 0:
            progress = 1.0
        else:
            progress = min(max(t / duration, 0.0), 1.0)

        eased = self.easing(progress)
        value = start + (end - start) * eased
        setattr(self.component, self.prop, value)
