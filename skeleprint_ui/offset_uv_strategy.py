from gcode_utils import toggle_uv


class OffsetUvStrategy:
    MM_PER_REV = 10

    def __init__(self, uv_offset):
        self.uv_offset = uv_offset

    def adjust_target(self, pitch):
        # revolutions per offset distance - will be adjusted to a whole
        # number
        pitch_adjust = self.uv_offset / pitch

        # to be cured, the mandrel needs to rotate a whole number of times
        # before the pen reaches the ink
        offset_divisor = round(pitch_adjust)
        if (offset_divisor < 1.0):
            offset_divisor = 0.0

        # store offset rotations for printing
        self.offset_rotations = offset_divisor

        # actually change the relevant variables
        if (offset_divisor > 0.0):
            pitch = self.uv_offset / offset_divisor

        return pitch

    def generate_layer_gcode(self, current_layer, filament_width,
                             adjusted_axial_length, layer_revolutions,
                             start_points, layer_height, dir_mod):
        """Generate the g code for one layer with an offset UV spot.

        Arguments:
        current_layer -- index (from 0) of the current layer
        filament_width -- width of the filament in the axial direction
        adjusted_axial_length -- total length of the print
        layer_revolutions -- total number of turns required to print one layer
        start_points -- number of start points for the current layer
        layer_height -- height of one layer
        dir_mod -- modifier (1 or -1) indicating the direction of the helix
        """

        commands = []

        a = 0  # index of the helix currently being printed

        extrusion_height = (current_layer * layer_height) + layer_height
        transit_height = extrusion_height + (2 * layer_height)

        # Home the print head in the radial and axial directions
        commands.append("G0 Z{:.5f}".format(extrusion_height))
        commands.append("G0 X{:.5f}".format(0))
        # Redefine current axial and rotational coordinates as 0
        commands.append("G10 P0 L20 X0 Y0")

        while (a < start_points):
            # print the helix the entire length of the print
            commands.extend(toggle_uv())
            commands.append("M8 G1 X{:.5f} Y{:.5f}".format(
                adjusted_axial_length,
                dir_mod
                * self.MM_PER_REV
                * (layer_revolutions + (a / start_points))
            ))
            commands.append("M9")

            # cure the remaining uncured part of the helix
            commands.append("G1 X{:.5f} Y{:.5f}".format(
                adjusted_axial_length + self.uv_offset,
                dir_mod
                * self.MM_PER_REV
                * (layer_revolutions + (a / start_points)
                   + self.offset_rotations)
            ))
            commands.extend(toggle_uv())

            a += 1

            # return to the other side
            commands.append("G0 Z{:.5f}".format(transit_height))
            commands.append("G0 X{:.5f}".format(0))
            commands.append("G0 Y{:.5f}".format(
                dir_mod
                * self.MM_PER_REV
                * (a / start_points)
            ))
            commands.append("G0 Z{:.5f}".format(extrusion_height))

        return commands
