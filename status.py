
from enum import Flag, auto,Enum

class LineStatus(Flag):
    NONE = 0
    DATA = auto()
    LINE = auto()
    MARKER = auto()

class ImageStatus(Flag):
    NONE = 0
    DATA = auto()
    VALUE = auto()

class Status(Flag):
    NONE = 0
    DATA = auto()
    VALUE = auto()

class GraphStatus(Flag):
    NONE = 0
    UPDATE = auto()
    FROM_DATA = auto()

class PanelStatus(Flag):
    NONE = 0
    UPDATE = auto()

class MouseStatus(Flag):
    NONE = 0
    LEFT = auto()
    RIGHT = auto()
    MIDDLE = auto()

class RotateStatus(Flag):
    NONE = 0
    FLIP = auto()

class ItemStatus(Enum):
    VISIBLE = auto()
    INVISIBLE = auto()
    NONE = auto()

class Direction(Enum):
    LtoR = auto()
    RtoL = auto()
    DtoU = auto()
    UtoD = auto()

class PositionStatus(Enum):
    LT = auto()
    MM = auto()
    RB = auto()

class BorderStatus(Flag):
    NONE = 0
    LEFT = auto()
    TOP = auto()
    RIGHT = auto()
    BOTTOM = auto()
    ALL = LEFT|TOP|RIGHT|BOTTOM