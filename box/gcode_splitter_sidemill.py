#!/usr/bin/env python3
import sys
import math

from gcode import gcode

mill_diameter = 2.0          # mm, mill diameter
mill_radius = mill_diameter / 2.0
mill_gap = mill_radius       # mm
mill_depth_step = -1.0       # mm, depth for one step

plunge_feed_rate = 80        # mm/min, plunge feed rate
mill_feed_rate = 200         # mm/min, milling feed rate

spindle_speed = 10000        # rpm, spindle speed
tool_change_height = 3.0     # mm
rapid_move_height = 3.0      # mm
retract_height = 3.0         # mm
rapid_plunge_height = 0.5    # mm

box_edge_z = -5              # mm

mill_depth = -3.0            # mm
mill_start = mill_depth_step # mm

midi_hole_r = 16 / 2         # mm
midi_hole_y_step = 20.32     # mm

# box_edge_z
# gap from edge to top of the shim ( -2 mm )
# shim height ( -4 mm )
# PCB thickness ( -1.5 mm )
pcb_surface_z = box_edge_z -2 -4 -1.5

# distance from PCB surface to hole center ( -10 mm )
midi_hole_z = pcb_surface_z -10   # mm

midi_out_center_y = 0        # mm
midi_out_count = 3

usb_hole_width = 11          # mm
usb_hole_height = 10         # mm
usb_hole_z = pcb_surface_z -0.5

usb_led_hole_y = -10         # mm
usb_led_hole_z = pcb_surface_z - 11/2 # mm

midi_in_led_hole_y = 12.7    # mm

box_length = 101             # mm
box_width = 55               # mm

def new_gcode(out):
    return gcode(
          out = out,
          spindle_speed = spindle_speed,
          horizontal_feed_rate = mill_feed_rate,
          vertical_feed_rate = plunge_feed_rate,
          tool_change_height = tool_change_height,
          rapid_move_height = rapid_move_height,
          rapid_plunge_height = rapid_plunge_height,
          mill_diameter = mill_diameter,
          split_arcs = 0.001,
          )

def box_edge_cut(l):
    # cut the edge
    g.G(0, X=rapid_move_height, c='Retract')
    g.G(0, Y=l / 2 + mill_diameter, Z=box_edge_z + mill_gap)

    x = mill_start
    while (x >= mill_depth):
        # retract and move to milling start position
        g.G(0, X=rapid_move_height, c='Retract')
        g.G(0, Y=l / 2 + mill_diameter)

        # rapid plunge because mill is OUT of the box
        g.G(0, X=x, c='Plunge')
        g.G(1, F=mill_feed_rate, c="Set milling feed rate")
        g.G(1, Y=-l / 2 - mill_diameter)

        x += mill_depth_step

    # retract and move to start position
    g.G(0, X=rapid_move_height, c='Retract')
    g.G(0, Y=0)

def hole(hy, hz, hr):
    g.G(0, X=rapid_move_height, c='Retract')

    r = hr - mill_gap
    g.G(0, Y=hy, Z=hz - r)

    x = mill_start
    while (x >= mill_depth):
        g.G(1, X=x, F=plunge_feed_rate, c='Plunge')
        g.G(1, F=mill_feed_rate, c="Set milling feed rate")

        g.G(1, Y=hy, Z=hz - r)
        N = 360
        for n in range(N):
            a = (2.0 * math.pi) / N * n
            g.G(1, Y=hy - r * math.sin(a), Z=hz - r * math.cos(a))

        g.G(1, Y=hy, Z=hz - r)

        x += mill_depth_step

def midi_hole(hy):
    hole(hy, midi_hole_z, midi_hole_r)

def long_side():
    # cut the edge
    box_edge_cut(box_length)

    # holes are milled along Y axis
    # the mill oriented along X axis

    for h in range(midi_out_count):
        midi_hole(midi_out_center_y + h * midi_hole_y_step - (midi_out_count - 1) * midi_hole_y_step / 2)

def usb_side():
    # cut the edge
    box_edge_cut(box_width)

    g.G(0, Y=-usb_hole_width / 2 + mill_gap, Z=usb_hole_z - mill_gap)

    # x + 23.2
    x = mill_start
    while (x >= mill_depth):
        g.G(1, X=x, F=plunge_feed_rate, c='Plunge')
        g.G(1, F=mill_feed_rate, c="Set milling feed rate")

        g.G(1, Y=usb_hole_width / 2 - mill_gap)
        g.G(1, Z=usb_hole_z - usb_hole_height + mill_gap)
        g.G(1, Y=-usb_hole_width / 2 + mill_gap)
        g.G(1, Z=usb_hole_z - mill_gap)

        x += mill_depth_step

    g.G(0, X=rapid_move_height, c='Retract')
    g.G(0, Y=usb_led_hole_y, Z=usb_led_hole_z)
    g.G(1, X=mill_depth, F=plunge_feed_rate, c='Plunge')

def power_usb_side():
    # cut the edge
    box_edge_cut(box_width)

    usb_hole_y = -10

    g.G(0, Y=usb_hole_y -usb_hole_width / 2 + mill_gap, Z=usb_hole_z - mill_gap)

    # x + 23.2
    x = mill_start
    while (x >= mill_depth):
        g.G(1, X=x, F=plunge_feed_rate, c='Plunge')
        g.G(1, F=mill_feed_rate, c="Set milling feed rate")

        g.G(1, Y=usb_hole_y + usb_hole_width / 2 - mill_gap)
        g.G(1, Z=usb_hole_z - usb_hole_height + mill_gap)
        g.G(1, Y=usb_hole_y -usb_hole_width / 2 + mill_gap)
        g.G(1, Z=usb_hole_z - mill_gap)

        x += mill_depth_step

    g.G(0, X=rapid_move_height, c='Retract')

    power_hole_y = 9
    power_hole_z = pcb_surface_z -6.5
    power_hole_r = 7.5 / 2

    hole(power_hole_y, power_hole_z, power_hole_r)

    g.G(0, X=rapid_move_height, c='Retract')
    g.G(0, Y=0, Z=usb_led_hole_z)
    g.G(1, X=mill_depth, F=plunge_feed_rate, c='Plunge')

def midi_in_side():
    # cut the edge
    box_edge_cut(box_width)

    midi_hole(0)

    g.G(0, X=rapid_move_height, c='Retract')
    g.G(0, Y=midi_in_led_hole_y, Z=midi_hole_z)
    g.G(1, X=mill_depth, F=plunge_feed_rate, c='Plunge')


with open("splitter_long_side.ngc", "w") as f:
    g = new_gcode(f)
    long_side()
    g.G(0, X=rapid_move_height, c='Retract')
    g.end()

with open("splitter_usb_side.ngc", "w") as f:
    g = new_gcode(f)
    usb_side()
    g.G(0, X=rapid_move_height, c='Retract')
    g.end()

with open("splitter_power_usb_side.ngc", "w") as f:
    g = new_gcode(f)
    power_usb_side()
    g.G(0, X=rapid_move_height, c='Retract')
    g.end()

with open("splitter_midi_in_side.ngc", "w") as f:
    g = new_gcode(f)
    midi_in_side()
    g.G(0, X=rapid_move_height, c='Retract')
    g.end()

