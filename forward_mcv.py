from __future__ import annotations
from functools import reduce


class Point:
    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col


# box's position in the room - start: (top, left), end: (bottom, right)
class BoxPosition:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end


class Box:
    def __init__(self, id: int, remaining_pos: [BoxPosition] = []):
        self.remaining_pos = remaining_pos # all remaining valid positions for the given box
        self.id = id
        self.final_pos = None

    # check constraints for the given position
    def is_pos_valid(self, pos: BoxPosition, rows: int, cols: int, pillars: [Point]) -> bool:
        if pos.end.row <= rows and pos.end.col <= cols:
            return all(
                map(lambda p: not (pos.start.row < p.row < pos.end.row and pos.start.col < p.col < pos.end.col),
                    pillars))
        return False

    # initialize remaining positions from the constraints
    def init_pos(self, length: int, width: int, rows: int, cols: int, pillars: [Point]):
        for r in range(0, rows):
            for c in range(0, cols):
                # first without rotating
                pos = BoxPosition(Point(r, c), Point(r + length, c + width))
                if self.is_pos_valid(pos, rows, cols, pillars):
                    self.remaining_pos.append(pos)
                if length != width:
                    # if it's not a square then check rotated
                    pos_rotated = BoxPosition(Point(r, c), Point(r + width, c + length))
                    if self.is_pos_valid(pos_rotated, rows, cols, pillars):
                        self.remaining_pos.append(pos_rotated)

    # returns a new box that we'd get if we added the box in the given position
    def added_box(self, added: BoxPosition) -> Box:
        def is_compatible(p):
            return not ((p.start.row < added.end.row and p.start.col < added.end.col)
                        and (p.end.row > added.start.row and p.end.col > added.start.col))

        new_remaining_pos = list(filter(is_compatible, self.remaining_pos))
        return Box(self.id, new_remaining_pos)

    # returns a new box with the final position added
    def added_final(self, final_pos: BoxPosition) -> Box:
        new_box = Box(self.id, self.remaining_pos)
        new_box.final_pos = final_pos
        return new_box


# MCV: Most Constrained Variable
# return the most constrained box from boxes if its id is in from_ids
def mcv_box_from(boxes: [Box], from_ids: [int]) -> Box:
    return reduce(
        lambda b1, b2: b1 if len(b1.remaining_pos) < len(b2.remaining_pos) and b1.id in from_ids else b2,
        boxes)


# places boxes in the room from the unplaced_boxes and puts them in placed_boxes with their final position
# return placed_boxes:  if all boxes are placed
# return None:          if the boxes cannot be placed
# recursive
def place_boxes(unplaced_boxes: [Box], placed_boxes: [Box] = []) -> [Box]:
    if len(unplaced_boxes) == 0:
        return placed_boxes
    else:
        ids = [box.id for box in unplaced_boxes]
        while len(ids) != 0:
            mcv_box = mcv_box_from(unplaced_boxes, ids)
            for pos in mcv_box.remaining_pos:
                candidate = True
                new_unplaced_boxes = []
                for box in unplaced_boxes and candidate:
                    if box.id != mcv_box.id:
                        new_box = box.added_box(pos)
                        new_unplaced_boxes.append(new_box)
                        if len(new_box.remaining_pos) == 0: # one box cannot be placed if mcv_box is chosen
                            candidate = False

                if candidate:
                    result = place_boxes(new_unplaced_boxes, placed_boxes + [mcv_box.added_final(pos)])
                    if result is not None:
                        return result

            # if it wasn't successful then remove its id
            ids.remove(mcv_box.id)
        return None


# prints solution in a matrix format
def pretty_print(boxes: [Box], rows: int, cols: int):
    arr = [[0 for n in range(cols)] for n in range(rows)]

    for b in boxes:
        for row in range(b.final_pos.start.y, b.final_pos.end.y):
            for col in range(b.final_pos.start.x, b.final_pos.end.x):
                arr[row][col] = b.id

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
