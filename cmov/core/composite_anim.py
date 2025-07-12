
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
            for anim, _ in self.animations:
                if hasattr(anim, 'apply'):
                    anim.apply(t, total_duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(t, total_duration)
        elif self.mode == "stagger":
            for i, (anim, weight) in enumerate(self.animations):
                start_offset = i * self.stagger
                duration = self._get_duration(weight, total_duration, scene)
                if start_offset <= t < start_offset + duration:
                    if hasattr(anim, 'apply'):
                        anim.apply(t - start_offset, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(t - start_offset, duration)
        elif self.mode == "chain":
            elapsed = 0
            total_weight = self._total_weight()
            for i, (anim, weight) in enumerate(self.animations):
                duration = self._get_duration(weight, total_duration, scene, total_weight)
                start_offset = elapsed
                if start_offset <= t < start_offset + duration:
                    if hasattr(anim, 'apply'):
                        anim.apply(t - start_offset, duration, scene=scene) if 'scene' in anim.apply.__code__.co_varnames else anim.apply(t - start_offset, duration)
                    break
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
