import math

def linear(t):
    return t

def ease_in(t):
    return t * t

def ease_out(t):
    return 1 - (1 - t) * (1 - t)

def ease_in_out(t):
    if t < 0.5:
        return 2 * t * t
    return 1 - pow(-2 * t + 2, 2) / 2

def ease_out_bounce(t):
    x1, y1, x2, y2 = 0.5, -0.34, 0.25, 1.35
    def cubic_bezier(t, p0, p1, p2, p3):
        return (1 - t)**3 * p0 + 3 * (1 - t)**2 * t * p1 + 3 * (1 - t) * t**2 * p2 + t**3 * p3
    return cubic_bezier(t, 0.0, y1, y2, 1.0)

def ease_in_back(t):
    c1 = 1.70158
    return c1 * t * t * ((1 + c1) * t - c1)
