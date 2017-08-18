# Number of millimetres that correspond to one full turn of the rotational axis
MM_PER_REV = 10
# Maximum angle defined to prevent extremely long print times
MAX_ANGLE = 88


def toggle_uv():
    """Generate gcode to pulse the UV control line, toggling the pen"""
    gcode = []

    gcode.append("M3")
    gcode.append("G4 P0.2")
    gcode.append("M5")

    return gcode
