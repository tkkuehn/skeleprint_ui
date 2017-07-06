#! /usr/bin/env python
#
# Support module generated by PAGE version 4.8.9
# In conjunction with Tcl version 8.6
#    Feb 25, 2017 07:24:37 PM
#    Feb 25, 2017 11:35:57 PM

from __future__ import division
import os
import errno
import math
import time

try:
    from Tkinter import DoubleVar
except ImportError:
    from tkinter import DoubleVar


def set_Tk_var():
    # These are Tk variables used passed to Tkinter and must be
    # defined before the widgets using them are created.
    global axial_length
    axial_length = DoubleVar()

    global printbed_diameter
    printbed_diameter = DoubleVar()

    global final_diameter
    final_diameter = DoubleVar()

    global filament_width_og
    filament_width_og = DoubleVar()

    global helix_angle
    helix_angle = DoubleVar()

    global smear_factor
    smear_factor = DoubleVar()

    global feedrate
    feedrate = DoubleVar()


def init(top, gui, *args, **kwargs):
    global w, top_level, root
    w = gui
    top_level = top
    root = top


def destroy_window():
    """Close the window."""
    global top_level
    top_level.destroy()
    top_level = None


commands = []


def axial_travel_calc(num_start_points, layer_diameter, filament_width):
    """Calculate axial travel from one revolution to the next.

    Arguments:
    num_start_points -- number of layer start points, placed at angles
    of 2pi / start points
    layer_diameter -- layer diameter (incremented every layer)
    filament_width -- filament width (effectively stretched by the print
    angle)
    """

    # caution, this script uses angles in radians
    print_angle = math.asin(num_start_points * filament_width / layer_diameter)
    axial_travel = filament_width / math.cos(print_angle)
    return axial_travel


def angle_finder(num_start_points, circumference, filament_width):
    """Adjust the helix angle to prevent gaps between helices.

    The correction is based on a number of start points calculated using the
    user-specified angle, so that the result is as close as possible to that
    value without allowing helices to overlap.
    """

    # caution, this script uses angles in radians

    theta = math.atan(num_start_points*filament_width/circumference)

    return theta


def calc_tangential_velocity(feedrate, axial_travel, diameter, theta):
    """Calculate the tangential velocity of the print head."""

    hyp = (math.pi * diameter) / math.cos(theta)
    time = (hyp/feedrate)
    w = (2 * math.pi) / time
    tangential_velocity = w * (diameter / 2)

    return tangential_velocity


def init_layer(feedrate, current_layer, printbed_diameter, filament_width_og,
               layer_diameter):
    """Initialize gcode and set feedrate (movement speed of the axis)."""

    commands.append(";----------------------")
    commands.append("; layer {}".format(current_layer))
    commands.append(";----------------------")
    commands.append("G1 F{:.5f}".format(feedrate))


def main_gcode(current_layer, filament_width, x2, y, n, layer_height):
    """Generate the g code for one layer.

    Arguments:
    current_layer -- index (from 0) of the current layer
    filament_width -- width of the filament in the axial direction
    x2 -- total length of the print
    y -- total number of turns required to print one layer
    n -- number of start points for the current layer
    layer_height -- height of one layer
    """

    mm_per_rev = 10

    a = 0  # index of the helix currently being printed

    # Home the print head in the radial and axial directions
    commands.append("G0 Z{:.5f}".format(current_layer * (layer_height)))
    commands.append("G0 X{:.5f}".format(0))
    # Redefine current axial and rotational coordinates as 0
    commands.append("G10 P0 L20 X0 Y0")

    # Make rotation direction alternate every other layer
    if (current_layer % 2 == 0):
        dir_mod = 1
    else:
        dir_mod = -1

    while (a < n):
        # print one helix the entire length of the print
        commands.append("M8 G1 X{:.5f} Y{:.5f}".format(
            x2,
            dir_mod * mm_per_rev * (y + (a / n))))
        commands.append("M9")

        a += 1
        # rotate slightly to the next start point
        commands.append("G1 Y{:.5f}".format(
            dir_mod * mm_per_rev * (y + (a / n))))

        # check if the layer is complete
        if (a < n):
            extrude = "M8 "
        else:
            extrude = ""

        # return to the other side, extruding if necessary
        commands.append("{}G1 X{:.5f} Y{:.5f}".format(
            extrude,
            0,
            dir_mod * mm_per_rev * (a / n)))

        # if extruding, stop
        if (a < n):
            commands.append("M9")
            a += 1
            
            # rotate slightly to the next start point
            commands.append("G1 Y{:.5f}".format(dir_mod * mm_per_rev * (a / n)))


def min_angle_print(current_layer, x2, y, layer_height):
    """Generate g code to print one layer at the minimum angle.

    Arguments:
    current_layer -- number of completed layers before this one
    layer_height -- height of each layer
    """

    mm_per_rev = (10)

    commands.append("G0 Z{:.5f}".format(current_layer * (layer_height)))
    commands.append("G0 X{:.5f}".format(0))
    commands.append("G10 P0 L20 X0 Y0")  # reset x and y axis position

    if (current_layer % 2 == 0):
        commands.append("M8 G1 X{:.5f} Y{:.5f}".format(x2, mm_per_rev*y))
        commands.append("M9")

    else:
        commands.append("M8 G1 X{:.5f} Y{:.5f}".format(x2, (-1)*mm_per_rev*y))
        commands.append("M9")


def end_gcode():
    """Add final g code and write file containing it."""

    commands.append(";----------------------")
    commands.append("G0 Z{:.5f}".format(20))
    commands.append("G0 X{:.5f} Y{:.5f}".format(0, 0))
    commands.append("; End g code")

    timestr = time.strftime("%d_%m-%H_%M_%S")

    loc = os.path.join(os.path.expanduser("~"),
                       os.path.join('Desktop', 'gcode'))
    filename = timestr+'_skeleprint.gcode'

    if not os.path.exists(loc):
        try:
            os.makedirs(loc)
        except OSError as exc:  # Guard against race condition
            print ("Directory not found, somehow you don't have a desktop. ",
                   "Or I can't find it. ")
            if exc.errno != errno.EEXIST:
                raise

    with open(os.path.join(loc, filename), "w") as file:
        file.write("\n".join(commands))


def tpg(axial_travel, filament_width_og, printbed_diameter, final_diameter,
        helix_angle, smear_factor, feedrate_og):
    """Generate g-code for printing cylinders at various angles.

    Required params:
        axial_travel - total length of print (ex. 200)
        filament_width_og - width of filament (0.1)
        print_radius - total radius of print (10)
        printbed_diameter - diameter of the print bed (10)
        final_diameter - target print diameter
        helix_angle - angle of the helix printed (0 - 90)
        smear_factor - how much the subsequent layer is smeared (0 - 1)

    all units are in mm and degrees
    """

    del commands[:]
    commands.append(";PARAMETERS")
    commands.append(";filament_width={}".format(filament_width_og))
    commands.append(";axial_travel={}".format(axial_travel))
    commands.append(";printbed_diameter={}".format(printbed_diameter))
    commands.append(";final_diameter={}".format(final_diameter))
    commands.append(";feedrate from flowrate={}".format(feedrate_og))

    smear_factor = smear_factor * 0.01
    print "smear factor", smear_factor

    # Step 1: number of layers needed to print the chosen final diameter
    layers = (((final_diameter - printbed_diameter) * 0.5)
              / (filament_width_og * smear_factor))

    if (layers < 1):
        layers = 1.0

    # need a whole number of layers
    if (layers % (filament_width_og * smear_factor) != 0):
        layers = math.floor(layers)
        print "The print diameter you've set is not symmetrical and has \
been rounded to {} mm, with {} layers".format(
                       final_diameter - filament_width_og, layers)

    print "layers:", layers
    commands.append(";layers={}".format(layers))

    # Step 2: Deposition Angle
    helix_angle_rad = math.radians(helix_angle)

    # Angles below this will cause smearing as a helix overlaps itself
    min_angle = math.atan(filament_width_og / (math.pi * printbed_diameter))
    print "min angle", min_angle

    # Angles above this will print too slowly
    max_angle = math.radians(88)

    if (helix_angle_rad <= min_angle):
        theta = min_angle
        base_case = True
    elif (helix_angle_rad >= max_angle):
        theta = max_angle
        base_case = False
    else:
        theta = helix_angle_rad
        base_case = False

    print "base case", base_case

    commands.append(";helix_angle={}".format(math.degrees(theta)))

    current_layer = 0

    # set defaults: absolute position, mm, stop all movements
    commands.append("G0 G54 G17 G21 G90 G94 M5 M9 T0 F0.0 S0")
    commands.append("G10 P0 L20 X0 Y0 Z0")

    while (current_layer < layers):
        # Step 3: Number of start points with corresponding angle
        print "Layer: ", current_layer
        layer_diameter = (printbed_diameter
                          + (current_layer * filament_width_og))
        print "layer diameter", layer_diameter
        circumference = math.pi * layer_diameter
        print "circumference", circumference

        # distance traveled in the axial direction with every rotation
        x_move_per_rev = circumference * math.tan(theta)
        print "x_move_per_rev:", x_move_per_rev

        # filament width corrected for angle of deposition
        filament_width = filament_width_og / math.cos(theta)
        print "filament width update:", filament_width
        n = x_move_per_rev / filament_width  # number of start points
        print "number of start points: ", n

        if (float(n).is_integer()):
            print "number of total start points:", n
            print "updated angle", math.degrees(theta)
        else:
            if (n > 1):
                n = math.floor(n)
            else:
                n = 1
            theta = angle_finder(n, circumference, filament_width)

        print "theta (rads) for layer {}: {}".format(current_layer, theta)
        print "number of total start points for layer {}: {}".format(
            current_layer, n)
        print "updated helix angle", math.degrees(theta)

        # Step 4: Feed rate
        x2 = axial_travel - filament_width  # adjusted for endpoint
        y = axial_travel / x_move_per_rev
        print "revs per winding:", y

        feedrate = calc_tangential_velocity(
            feedrate_og, axial_travel, layer_diameter, theta)

        # Step 5: Print layer
        init_layer(feedrate, current_layer, printbed_diameter,
                   filament_width_og, layer_diameter)
        if (base_case):
            min_angle_print(
                current_layer, x2, y, filament_width_og * smear_factor)
        else:
            main_gcode(current_layer, filament_width, x2, y, n,
                       filament_width_og * smear_factor)
        current_layer += 1

    # Step 6: Complete print
    end_gcode()


if __name__ == '__main__':
    import tpg_gui
    tpg_gui.vp_start_gui()
