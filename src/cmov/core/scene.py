from PIL import Image, ImageDraw
from fmov import Video
from ..utils.time import parse_time
from tqdm import tqdm

class Scene:
    def _flatten_animations(self, animation, start_frame, duration_frames):
        """
        Recursively flatten all animations (including inside composites) into a list of
        (component, prop, animation, anim_start_frame, anim_end_frame, anim_duration)
        Handles correct timing for parallel, chain, and stagger composite animations.
        """
        result = []
        if animation is None:
            return result
        if hasattr(animation, 'animations'):
            mode = getattr(animation, 'mode', 'parallel')
            stagger = getattr(animation, 'stagger', 0)
            anims = getattr(animation, 'animations', [])
            n = len(anims)
            if mode == 'parallel':
                # All start at the same time, share duration_frames
                for anim_tuple in anims:
                    if isinstance(anim_tuple, tuple):
                        anim, weight = anim_tuple
                        if isinstance(weight, str):
                            anim_duration = self.parse_time(weight)
                        else:
                            anim_duration = duration_frames if not isinstance(weight, str) else self.parse_time(weight)
                    else:
                        anim = anim_tuple
                        anim_duration = duration_frames
                    result.extend(self._flatten_animations(anim, start_frame, anim_duration))
            elif mode == 'stagger':
                # Each starts after i*stagger, each animation gets duration_frames
                # Interpret stagger as a timecode string if possible
                if isinstance(stagger, str):
                    stagger_frames = self.parse_time(stagger)
                else:
                    stagger_frames = int(stagger)
                for i, anim_tuple in enumerate(anims):
                    if isinstance(anim_tuple, tuple):
                        anim, weight = anim_tuple
                        if isinstance(weight, str):
                            anim_duration = self.parse_time(weight)
                        else:
                            anim_duration = duration_frames if not isinstance(weight, str) else self.parse_time(weight)
                    else:
                        anim = anim_tuple
                        anim_duration = duration_frames
                    child_start = start_frame + i * stagger_frames
                    result.extend(self._flatten_animations(anim, child_start, anim_duration))
            elif mode == 'chain':
                # Each starts after previous ends, with gap=stagger (interpreted as timecode)
                if isinstance(stagger, str):
                    gap_frames = self.parse_time(stagger)
                else:
                    gap_frames = int(stagger)
                child_start = start_frame
                for i, anim_tuple in enumerate(anims):
                    if isinstance(anim_tuple, tuple):
                        anim, weight = anim_tuple
                        if isinstance(weight, str):
                            anim_duration = self.parse_time(weight)
                        else:
                            anim_duration = duration_frames if not isinstance(weight, str) else self.parse_time(weight)
                    else:
                        anim = anim_tuple
                        anim_duration = duration_frames
                    result.extend(self._flatten_animations(anim, child_start, anim_duration))
                    child_start += anim_duration + gap_frames
        elif hasattr(animation, 'component') and hasattr(animation, 'prop'):
            result.append((animation.component, animation.prop, animation, start_frame, start_frame + duration_frames, duration_frames))
        return result

    def __init__(self, width, height, fps=30):
        self.width = width
        self.height = height
        self.fps = fps
        self.timeline = []
        self.components = []

    def add(self, component):
        if component not in self.components:
            self.components.append(component)

    def play(self, animation, duration=None):
        def add_components_from_anim(anim):
            if anim is None:
                return
            if hasattr(anim, 'component') and hasattr(anim, 'prop'):
                if anim.component is not None and anim.component not in self.components:
                    self.components.append(anim.component)
            if hasattr(anim, 'animations'):
                for anim_tuple in getattr(anim, 'animations', []):
                    if isinstance(anim_tuple, tuple):
                        add_components_from_anim(anim_tuple[0])
                    else:
                        add_components_from_anim(anim_tuple)

        if isinstance(animation, list):
            for anim, dur in animation:
                add_components_from_anim(anim)
                self.timeline.append((anim, dur))
        else:
            add_components_from_anim(animation)
            self.timeline.append((animation, duration))

    def wait(self, duration):
        self.timeline.append((None, duration))

    def parse_time(self, t):
        """
        Parses a time string or int into a number of frames (for self.frames).
        Supports frames (no suffix), ms, s, m, h, and stacked units (e.g. '1h23m', '2m 10s', '500ms', '100').
        """
        if t is None:
            return 0
        if isinstance(t, int):
            # Assume frames if int
            return t
        if isinstance(t, str):
            import re
            total_frames = 0.0
            t = t.replace(' ', '')
            for value, unit in re.findall(r'([\d.]+)(ms|s|m|h|)', t):
                if unit == '':  # frames
                    total_frames += float(value)
                elif unit == 'ms':
                    total_frames += float(value) * self.fps / 1000.0
                elif unit == 's':
                    total_frames += float(value) * self.fps
                elif unit == 'm':
                    total_frames += float(value) * 60 * self.fps
                elif unit == 'h':
                    total_frames += float(value) * 3600 * self.fps
            return int(total_frames)
        return 0

    def _render_animation(self, animation, img, draw, timeline):
        if animation is None:
            return
        if hasattr(animation, 'animations'):
            for anim_tuple in getattr(animation, 'animations', []):
                anim = anim_tuple[0] if isinstance(anim_tuple, tuple) else anim_tuple
                self._render_animation(anim, img, draw, timeline)
        elif hasattr(animation, "component") and animation.component is not None:
            animation.component.render(img, draw, timeline)

    def _apply_animations(self, t, duration_frames, scene):
        for animation, dur in self.timeline:
            if animation:
                if hasattr(animation, 'apply'):
                    animation.apply(t, duration_frames, scene=scene)

    def render(self, output_path="output.mp4"):
        timeline_frames = []
        for anim, dur in self.timeline:
            frames = self.parse_time(dur)
            timeline_frames.append((anim, frames))

        flat_animations = []
        cursor = 0
        for anim, frames in timeline_frames:
            flat_animations.extend(self._flatten_animations(anim, cursor, frames))
            cursor += frames

        # Determine when each component first appears (first animation referencing it)
        component_first_frame = {}
        max_end_frame = 0
        for comp, p, anim, start, end, duration in flat_animations:
            if comp not in component_first_frame or start < component_first_frame[comp]:
                component_first_frame[comp] = start
            if end > max_end_frame:
                max_end_frame = end

        total_frames = max_end_frame

        with Video(output_path, (self.width, self.height), fps=self.fps) as video:
            frame_counter = 0
            segment_start_values = {}
            for frame_idx in tqdm(range(total_frames), unit="frames"):
                for component in self.components:
                    # Only render component if its first animation has started
                    if component in component_first_frame and frame_idx < component_first_frame[component]:
                        continue
                    for prop in vars(component):
                        active_anim = None
                        active_start = None
                        active_duration = None
                        for comp, p, anim, start, end, duration in flat_animations:
                            if comp is component and p == prop:
                                if start <= frame_idx < end:
                                    active_anim = anim
                                    active_start = start
                                    active_duration = duration
                        if active_anim is not None:
                            seg_key = (id(component), prop, active_start)
                            if seg_key not in segment_start_values:
                                segment_start_values[seg_key] = getattr(component, prop)
                            start_value = segment_start_values[seg_key]
                            t = (frame_idx - active_start) / active_duration if active_duration > 0 else 0
                            t *= self.fps
                            active_anim.apply(t, active_duration, scene=self, start_value=start_value)
                        else:
                            last_anim = None
                            last_end = -1
                            last_duration = None
                            last_start_value = None
                            for comp, p, anim, start, end, duration in flat_animations:
                                if comp is component and p == prop:
                                    if end <= frame_idx and end > last_end:
                                        last_anim = anim
                                        last_end = end
                                        last_duration = duration
                                        seg_key = (id(component), prop, start)
                                        last_start_value = segment_start_values.get(seg_key, getattr(component, prop))
                            if last_anim is not None:
                                last_anim.apply(last_duration, last_duration, scene=self, start_value=last_start_value)
                img = Image.new("RGBA", (self.width, self.height), (0,0,0,0))
                draw = ImageDraw.Draw(img)
                for component in self.components:
                    if component in component_first_frame and frame_idx < component_first_frame[component]:
                        continue
                    component.render(img, draw)
                # Convert to RGB for video output if needed
                video.pipe(img.convert("RGB"))
                frame_counter += 1

