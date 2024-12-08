#!/usr/bin/env python3
"""A module which calculates the angles in paths"""

import math
from tldhamburg.control.routplaning.models import ORSNode


# 0.7 radians are approximately 40 degrees.
TOLERANCE: float = 0.7


def is_left_turn(a: ORSNode, b: ORSNode, c: ORSNode) -> bool:
    """Determines whether the path from a over b to c
    is -strictly speaking - a left-turn"""
    return (b.lon - a.lon) * (c.lat - a.lat) -\
           (b.lat - a.lat) * (c.lon - a.lon) > 0


def angle_inbetween(a: ORSNode, b: ORSNode, c: ORSNode) -> float:
    """Determines the angle one turns at point b to reach c from a over b"""
    
    try:
        calculation =  math.acos(((b - a) @ (c - b)) / (abs(b - a) * abs(c - b)))
        return calculation
    except ValueError as e:
        return 0
    

def is_left_turn_tolerance(a: ORSNode, b: ORSNode, c: ORSNode) -> bool:
    """Determines whether th path from a over b to c is a left-turn.
    In this function, we have a given tolerance to allow for roads
    that are not perfectly straight"""
    return angle_inbetween(a, b, c) > TOLERANCE and is_left_turn(a, b, c)


def is_right_turn_tolerance(a: ORSNode, b: ORSNode, c: ORSNode) -> bool:
    """Determines whether th path from a over b to c is a right-turn.
    In this function, we have a given tolerance to allow for roads
    that are not perfectly straight"""
    return angle_inbetween(a, b, c) > TOLERANCE and not is_left_turn(a, b, c)


def is_straight_line_tolerance(a: ORSNode, b: ORSNode, c: ORSNode) -> bool:
    """Determines whether th path from a over b to c is a straight path.
    In this function, we have a given tolerance to allow for roads
    that are not perfectly straight"""
    return angle_inbetween(a, b, c) <= TOLERANCE
