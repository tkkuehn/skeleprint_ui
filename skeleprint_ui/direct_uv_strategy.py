from gcode_utils import MM_PER_REV, toggle_uv


class DirectUvStrategy:
    def adjust_target(self, pitch):
        """Returns original pitch; this works with any angle"""

        return pitch

    def generate_layer_gcode(self, current_layer, filament_width,
                             adjusted_axial_length, layer_revolutions,
                             start_points, layer_height, dir_mod):
        """Generate the g code for one layer with direct UV.

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

        while (a < start_points):
            # print one helix the entire length of the print
            commands.extend(toggle_uv())
            commands.append("M8 G1 X{:.5f} Y{:.5f}".format(
                adjusted_axial_length,
                dir_mod
                * MM_PER_REV
                * (layer_revolutions + (a / start_points))
            ))
            commands.append("M9")
            commands.extend(toggle_uv())

            a += 1
            # rotate slightly to the next start point
            commands.append("G1 Y{:.5f}".format(
                dir_mod
                * MM_PER_REV
                * (layer_revolutions + (a / start_points))
            ))

            # check if the layer is complete
            if (a < start_points):
                extrude = "M8 "
                commands.extend(toggle_uv())
            else:
                extrude = ""

            # return to the other side, extruding if necessary
            commands.append("{}G1 X{:.5f} Y{:.5f}".format(
                extrude,
                0,
                dir_mod * MM_PER_REV * (a / start_points)))

            # if extruding, stop
            if (a < start_points):
                commands.append("M9")
                commands.extend(toggle_uv())
                a += 1

                # rotate slightly to the next start point
                commands.append("G1 Y{:.5f}".format(
                    dir_mod * MM_PER_REV * (a / start_points)))

        return commands
