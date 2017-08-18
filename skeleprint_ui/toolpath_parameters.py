"""Contains and processes toolpath parameters.

This class stores all parameters required to generate a toolpath, and can
generate secondary parameters that are derived directly from the explicitly
defined parameters.
"""


import math


class ToolpathParameters:

    def __init__(self, axial_length, printbed_diameter, final_diameter,
                 filament_width_og, helix_angle, smear_factor, feedrate,
                 uv_offset):
        self.axial_length = axial_length
        self.printbed_diameter = printbed_diameter
        self.final_diameter = final_diameter
        self.filament_width_og = filament_width_og
        self.helix_angle = helix_angle
        self.smear_factor = smear_factor
        self.feedrate = feedrate
        self.uv_offset = uv_offset

    def get_theta(self):
        return math.radians(self.helix_angle)
