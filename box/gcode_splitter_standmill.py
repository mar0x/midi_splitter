#!/usr/bin/env python3
import sys

from gcode import gcode

mill_diameter = 3.175        # mm, mill diameter
mill_radius = mill_diameter / 2.0
mill_gap = mill_radius       # mm
vertical_step = -1.5         # mm, vertical step

vertical_feed_rate = 60      # mm/min, vertical feed rate
horizontal_feed_rate = 300   # mm/min, horizontal feed rate

spindle_speed = 10000        # rpm, spindle speed
tool_change_height = 3.0     # mm
rapid_move_height = 3.0      # mm
retract_height = 3.0         # mm
rapid_plunge_height = 0.5    # mm

stand_d = 6                  # mm
stand_r = stand_d / 2

box_edge_z = -5              # mm

mill_start = 0
mill_depth = box_edge_z -5.6

g = gcode(
      spindle_speed = spindle_speed,
      horizontal_feed_rate = horizontal_feed_rate,
      vertical_feed_rate = vertical_feed_rate,
      tool_change_height = tool_change_height,
      rapid_move_height = rapid_move_height,
      rapid_plunge_height = rapid_plunge_height,
      mill_diameter = mill_diameter,
      split_arcs = 0.001,
      )

g.retract()

def mill_stand(hx, hy, wallx, wally):
    g.gcmd("MSG, Ready?) ")

    r = mill_radius + 0.5

    g.G(0, X=hx, Y=hy - r)

    g.M(3, c="Spindle on clockwise")
    g.G(4, P=1.0, c="Wait for spindle to get up to speed")

    z = mill_start
    while (z >= mill_depth):
        g.plunge(z)
        g.G(2, X=hx - r, Y=hy, I=0, J=r)
        g.G(2, X=hx, Y=hy + r, I=r, J=0)
        g.G(2, X=hx + r, Y=hy, I=0, J=-r)
        g.G(2, X=hx, Y=hy - r, Z=z, I=-r, J=0)

        if z == mill_depth:
            break

        z += vertical_step
        if z < mill_depth:
            z = mill_depth

    r = 4.6
    g.G(1, X=hx, Y=hy)
    g.G(1, X=hx, Y=hy + r * wally)
    g.G(1, X=hx, Y=hy)
    g.G(1, X=hx + r * wallx, Y=hy)
    g.G(1, X=hx, Y=hy)

    g.retract()

    g.M(5, c="Spindle off")
    g.G(4, P=1.0, c="Wait for spindle to stop")

mill_stand(0, 0, 1, 1)
mill_stand(0, -38.5, 1, -1)
mill_stand(-85.5, -38.5, -1, -1)
mill_stand(-85.5, 0, -1, 1)

g.G(0, X=0, Y=0)
g.G(0, X=0, Y=55)

g.end()
