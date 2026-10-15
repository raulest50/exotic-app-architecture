"""Pure geometry. Points are in the line's coordinate system, source first."""

EPSILON = 1e-6


def equal(a, b):
    return abs(a[0] - b[0]) < EPSILON and abs(a[1] - b[1]) < EPSILON


def simplify(points):
    result = []
    for point in points:
        point = tuple(map(float, point))
        if result and equal(result[-1], point):
            continue
        while len(result) >= 2:
            a, b = result[-2:]
            # Only remove a middle point on the segment, never a U-turn.
            vertical = abs(a[0] - b[0]) < EPSILON and abs(b[0] - point[0]) < EPSILON
            horizontal = abs(a[1] - b[1]) < EPSILON and abs(b[1] - point[1]) < EPSILON
            between = ((b[0] - a[0]) * (point[0] - b[0]) >= 0
                       and (b[1] - a[1]) * (point[1] - b[1]) >= 0)
            if not ((vertical or horizontal) and between):
                break
            result.pop()
        result.append(point)
    return result


def native_points(points):
    """Gaphas requires alternating axes, even when a path doubles back.

    A zero-length perpendicular segment preserves an intentional 180-degree
    turn without moving a fixed waypoint. All other redundant points were
    already removed by simplify(). These are native handles, not custom data.
    """
    result = []
    previous_axis = None
    for point in points:
        if result:
            axis = abs(result[-1][1] - point[1]) < EPSILON
            if axis == previous_axis:
                result.append(result[-1])
            previous_axis = axis
        result.append(point)
    return result


class Route:
    def __init__(self):
        self.legs = []
        self.horizontal = True

    def points(self, start, end):
        points = [start]
        for target, horizontal in [*self.legs, (end, self.horizontal)]:
            previous = points[-1]
            points.append((target[0], previous[1]) if horizontal else (previous[0], target[1]))
            points.append(target)
        return simplify(points)

    def fix(self, start, end):
        previous = self.legs[-1][0] if self.legs else start
        if not equal(previous, end):
            # Gaphas positions contain mutable solver Variables, not floats.
            self.legs.append((tuple(map(float, end)), self.horizontal))

    def flip(self):
        self.horizontal = not self.horizontal
