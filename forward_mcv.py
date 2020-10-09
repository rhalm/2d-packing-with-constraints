from __future__ import annotations
from functools import reduce


# box's position represented by its start (top, left) and end (bottom, right)
class BoxPosition:
    def __init__(self, start: (int, int), end: (int, int)):
        self.start = start
        self.end = end


class Box:
    def __init__(self, idx: int, remaining_pos: [BoxPosition] = None):
        if remaining_pos is None:
            self.remaining_pos = []
        else:
            self.remaining_pos = remaining_pos
        self.idx = idx
        self.final_pos = (-1, -1)

    # check constraints for the given position
    def check_pos(self, pos: BoxPosition, rows: int, cols: int, pillars: [(int, int)]) -> bool:
        if pos.end[0] <= rows and pos.end[1] <= cols:
            for (pr, pc) in pillars:
                if pos.start[0] < pr < pos.end[0] and pos.start[1] < pc < pos.end[1]:
                    return False
            return True
        return False

    # initialize remaining positions from the constraints
    def init_pos(self, length: int, width: int, rows: int, cols: int, pillars: [(int, int)]):
        for r in range(0, rows):
            for c in range(0, cols):
                # first without rotating
                pos = BoxPosition((r, c), (r + length, c + width))
                if self.check_pos(pos, rows, cols, pillars):
                    self.remaining_pos.append(pos)
                if length != width:
                    # if it's not a square then check rotated
                    pos_rotated = BoxPosition((r, c), (r + width, c + length))
                    if self.check_pos(pos_rotated, rows, cols, pillars):
                        self.remaining_pos.append(pos_rotated)

    # returns a new box that we'd get if we added the box in the given position
    # box coordinates - start: (top, left), end: (bottom, right)
    def added_box(self, added: BoxPosition) -> Box:
        def is_compatible(p):
            return not ((p.start[0] < added.end[0] and p.start[1] < added.end[1])
                        and (p.end[0] > added.start[0] and p.end[1] > added.start[1]))

        new_remaining_pos = list(filter(is_compatible, self.remaining_pos))
        return Box(self.idx, new_remaining_pos)


# MCV: Most Constrained Variable
# return the most constrained box from boxes if it's index is in indices
def get_MCV_box(boxes: [Box], indices: [int]) -> Box:
    if len(boxes) == 0:
        return None

    mcv = reduce(lambda b1, b2: b1 if len(b1.remaining_pos) < len(b2.remaining_pos) and b1.idx in indices else b2,
                 boxes)
    return mcv


# places boxes in the room from the queue and puts them in fix_pos with their final position
# return fix_pos:   if all boxes are placed
# return None:      if the boxes cannot be placed
def place_boxes(queue: [Box], fix_pos: [Box] = None) -> [Box]:
    if fix_pos is None:
        fix_pos = []
    if len(queue) == 0:
        return fix_pos

    indices = [b.idx for b in queue]
    while len(indices) != 0:
        mcv_box = get_MCV_box(queue, indices)
        for pos in mcv_box.remaining_pos:
            candidate = True
            new_queue = []
            for box in queue:
                if box.idx != mcv_box.idx:
                    new_box = box.added_box(pos)
                    new_queue.append(new_box)
                    if len(new_box.remaining_pos) == 0:
                        candidate = False
                        break

            if candidate:
                mcv_box.final_pos = pos
                new_fix_pos = fix_pos + [mcv_box]
                result = place_boxes(new_queue, new_fix_pos)
                if result is not None:
                    return result

        # if it wasn't successful then remove its index
        indices.remove(mcv_box.idx)

    return None


# prints solution in a matrix format
def pretty_print(boxes: [Box], rows: int, cols: int):
    arr = [[0 for n in range(cols)] for n in range(rows)]

    for b in boxes:
        for row in range(b.final_pos.start[0], b.final_pos.end[0]):
            for col in range(b.final_pos.start[1], b.final_pos.end[1]):
                arr[row][col] = b.idx

    for row in arr:
        print("\t".join(map(str, row)))


def forward_checking():
    # read input
    (rows, cols) = map(int, input().split("\t"))
    pillar_count = int(input())
    box_count = int(input())
    pillars = []
    boxes = []
    for pi in range(pillar_count):
        (x, y) = map(int, input().split("\t"))
        pillars.append((x, y))
    for bi in range(box_count):
        (length, width) = map(int, input().split("\t"))
        box = Box(bi + 1)
        box.init_pos(length, width, rows, cols, pillars)
        boxes.append(box)

    # solve and print solution
    final_positions = place_boxes(boxes)
    pretty_print(final_positions, rows, cols)


if __name__ == '__main__':
    forward_checking()
