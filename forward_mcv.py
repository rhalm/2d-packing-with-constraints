from __future__ import annotations
from functools import reduce


class Point:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


# box's position represented by its start (top, left) and end (bottom, right)
class BoxPosition:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end


class Box:
    def __init__(self, idx: int, remaining_pos: [BoxPosition] = []):
        self.remaining_pos = remaining_pos
        self.idx = idx
        self.final_pos = None

    # check constraints for the given position
    def check_pos(self, pos: BoxPosition, rows: int, cols: int, pillars: [Point]) -> bool:
        if pos.end.row <= rows and pos.end.col <= cols:
            for (prow, pcol) in pillars:
                if pos.start.row < prow < pos.end.row and pos.start.col < pcol < pos.end.col:
                    return False
            return True
        return False

    # initialize remaining positions from the constraints
    def init_pos(self, length: int, width: int, rows: int, cols: int, pillars: [Point]):
        for r in range(0, rows):
            for c in range(0, cols):
                # first without rotating
                pos = BoxPosition(Point(r, c), Point(r + length, c + width))
                if self.check_pos(pos, rows, cols, pillars):
                    self.remaining_pos.append(pos)
                if length != width:
                    # if it's not a square then check rotated
                    pos_rotated = BoxPosition(Point(r, c), Point(r + width, c + length))
                    if self.check_pos(pos_rotated, rows, cols, pillars):
                        self.remaining_pos.append(pos_rotated)

    # returns a new box that we'd get if we added the box in the given position
    # box coordinates - start: (top, left), end: (bottom, right)
    def added_box(self, added: BoxPosition) -> Box:
        def is_compatible(p):
            return not ((p.start.row < added.end.row and p.start.col < added.end.col)
                        and (p.end.row > added.start.row and p.end.col > added.start.col))

        new_remaining_pos = list(filter(is_compatible, self.remaining_pos))
        return Box(self.idx, new_remaining_pos)


# MCV: Most Constrained Variable
# return the most constrained box from boxes if it's index is in indices
def get_MCV_box(boxes: [Box], indices: [int]) -> Box:
    mcv = reduce(lambda b1, b2: b1 if len(b1.remaining_pos) < len(b2.remaining_pos) and b1.idx in indices else b2, boxes)
    return mcv


# places boxes in the room from the queue and puts them in fix_pos with their final position
# return fix_pos:   if all boxes are placed
# return None:      if the boxes cannot be placed
def place_boxes(queue: [Box], fix_pos: [Box] = []) -> [Box]:
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
        for row in range(b.final_pos.start.y, b.final_pos.end.y):
            for col in range(b.final_pos.start.x, b.final_pos.end.x):
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
        (row, col) = map(int, input().split("\t"))
        pillars.append(Point(row, col))
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
