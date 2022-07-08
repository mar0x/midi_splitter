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
vertical_step = -1.0         # mm, vertical step

vertical_feed_rate = 30      # mm/min, vertical feed rate
horizontal_feed_rate = 60    # mm/min, horizontal feed rate

spindle_speed = 10000        # rpm, spindle speed
tool_change_height = 10.0    # mm
rapid_move_height = 3.0      # mm
retract_height = 3.0         # mm
rapid_plunge_height = 0.5    # mm

hole_r = 16 / 2              # mm
hole_depth = -3.0            # mm
hole_step = 20.32            # mm
hole_y = hole_r + 10         # mm
hole_x = hole_step * 1       # mm
hole_count = 1


g = gcode(
      spindle_speed = spindle_speed,
      horizontal_feed_rate = horizontal_feed_rate,
      vertical_feed_rate = vertical_feed_rate,
      tool_change_height = tool_change_height,
      rapid_move_height = rapid_move_height,
      rapid_plunge_height = rapid_plunge_height,
      split_arcs = 0.001,
      )

#g.retract()
#g.G(0, X=0, Y=0)

r = hole_r - mill_gap

for h in range(hole_count):
    hx = hole_x + h * hole_step - (hole_count - 1) * hole_step / 2

    g.retract()
    g.G(0, X=hx, Y=hole_y - r)

    z = 0
    while (z >= hole_depth):
        g.plunge(z)

        #r = hole_r - mill_gap + z

        g.G(1, X=hx, Y=hole_y - r)
        N = 200000
        for n in range(N):
            a = (2.0 * math.pi) / N * n
            g.G(1, X=hx - r * math.sin(a), Y=hole_y - r * math.cos(a))

        g.G(1, X=hx, Y=hole_y - r)

        #g.G(2, X=hx - r, Y=hole_y, Z=z - 0.38, I=0, J=r)
        #g.G(2, X=hx, Y=hole_y + r, Z=z - 0.58, I=r, J=0)
        #g.G(2, X=hx + r, Y=hole_y, Z=z - 0.38, I=0, J=-r)
        #g.G(2, X=hx, Y=hole_y - r, Z=z, I=-r, J=0)

        z += vertical_step


g.end()
