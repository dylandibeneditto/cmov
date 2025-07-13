
from .animation import Animation

class CompositeAnimation(Animation):
    def __init__(self, animations, mode="parallel", stagger=0):
        super().__init__(None, None, None, None, None)
        self.animations = []
        self.mode = mode
        self.stagger = stagger
        for anim in animations:
            if isinstance(anim, tuple) and len(anim) == 2 and isinstance(anim[1], (int, float, str)):
                self.animations.append(anim)
            else:
                self.animations.append((anim, 1))

    @staticmethod
    def parallel(*animations):
        return CompositeAnimation(animations, mode="parallel")

    @staticmethod
    def stagger(*animations, stagger=5):
        return CompositeAnimation(animations, mode="stagger", stagger=stagger)

    @staticmethod
    def chain(*animations, gap=0):
        return CompositeAnimation(animations, mode="chain", stagger=gap)

    def apply(self, t, total_duration, scene=None):
        if self.mode == "parallel":
            # All animations start at t=0 and run for their duration (or total_duration)
            for anim, weight in self.animations:
                duration = self._get_duration(weight, total_duration, scene)
                if hasattr(anim, 'apply'):
                    anim.apply(min(t, duration), duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(min(t, duration), duration)
        elif self.mode == "stagger":
            # Each animation starts stagger frames after the previous
            n = len(self.animations)
            if n == 0:
                return
            # Compute the duration for each animation so that the last one finishes at total_duration
            if n == 1 or self.stagger == 0:
                per_duration = total_duration
            else:
                per_duration = total_duration - self.stagger * (n - 1)
                per_duration = max(per_duration, 0)  # avoid negative
                per_duration = per_duration
            for i, (anim, weight) in enumerate(self.animations):
                start_offset = i * self.stagger
                duration = self._get_duration(weight, per_duration, scene)
                if start_offset <= t < start_offset + duration:
                    local_t = t - start_offset
                    if hasattr(anim, 'apply'):
                        anim.apply(local_t, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(local_t, duration)
                elif t >= start_offset + duration:
                    # Clamp to end state after animation is done
                    if hasattr(anim, 'apply'):
                        anim.apply(duration, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(duration, duration)
        elif self.mode == "chain":
            # Each animation starts after the previous one ends, with optional gap (self.stagger)
            n = len(self.animations)
            if n == 0:
                return
            # Compute the duration for each animation so that all durations + gaps == total_duration
            total_gap = self.stagger * (n - 1)
            if n == 1:
                per_duration = total_duration
            else:
                per_duration = (total_duration - total_gap) / n if total_duration > total_gap else 0
            elapsed = 0
            for i, (anim, weight) in enumerate(self.animations):
                duration = self._get_duration(weight, per_duration, scene)
                start_offset = elapsed
                if start_offset <= t < start_offset + duration:
                    local_t = t - start_offset
                    if hasattr(anim, 'apply'):
                        anim.apply(local_t, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(local_t, duration)
                    break
                elif t >= start_offset + duration:
                    # Clamp to end state after animation is done
                    if hasattr(anim, 'apply'):
                        anim.apply(duration, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(duration, duration)
                elapsed += duration + self.stagger

    def _total_weight(self):
        total = 0
        for _, w in self.animations:
            if isinstance(w, (int, float)):
                total += w
        return total if total > 0 else len(self.animations)

    def _get_duration(self, weight, total_duration, scene=None, total_weight=None):
        if isinstance(weight, str):
            if scene is not None:
                return scene.parse_time(weight)
            raise ValueError("scene instance required for time parsing")
        if total_weight is None:
            return total_duration
        return total_duration * (weight / total_weight)
