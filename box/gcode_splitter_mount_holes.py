#!/usr/bin/env python3
import sys
import re
import math

from gcode import gcode
#from pocket import pocket
#from spirale import spirale

mill_diameter = 1.0          # mm, mill diameter
mill_radius = mill_diameter / 2.0
mill_gap = mill_radius       # mm
vertical_step = -0.5         # mm, vertical step

vertical_feed_rate = 30      # mm/min, vertical feed rate
horizontal_feed_rate = 60    # mm/min, horizontal feed rate

spindle_speed = 10000        # rpm, spindle speed
tool_change_height = 10.0    # mm
rapid_move_height = 3.0      # mm
retract_height = 3.0         # mm
rapid_plunge_height = 0.5    # mm

hole_r = 16 / 2              # mm
hole_depth = -10.0           # mm

holes = [
#    (21.5, 54.5),
#    (31.5, 44.5),
#    (44.5, 31.5),
#    (54.5, 21.5),

#    (54.5, -21.5),
#    (44.5, -31.5),
#    (31.5, -44.5),
#    (21.5, -54.5),

#    (-21.5, -54.5),
#    (-31.5, -44.5),
#    (-44.5, -31.5),
#    (-54.5, -21.5),

#    (-54.5, 21.5),
#    (-44.5, 31.5),
#    (-31.5, 44.5),
#    (-21.5, 54.5),

    (0, 55),
    (0, -55),
];

g = gcode(
      spindle_speed = spindle_speed,
      horizontal_feed_rate = horizontal_feed_rate,
      vertical_feed_rate = vertical_feed_rate,
      tool_change_height = tool_change_height,
      rapid_move_height = rapid_move_height,
      rapid_plunge_height = rapid_plunge_height,
      split_arcs = 0.001,
      )

g.retract()
g.G(0, X=0, Y=0)

for h in holes:
    g.G(0, X=h[0], Y=h[1], c='Move')
    g.plunge(rapid_plunge_height)
    g.G(1, Z=hole_depth, c='Drill')
    g.retract()
    g.G(0, X=0, Y=0)

g.end()
