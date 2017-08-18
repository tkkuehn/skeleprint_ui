class StrongAngleTargeter:
    def __init__(self, angle):
        self.angle = angle
        self.max_angle_alternator = 1

    def get_layer_target_angle(self, layer_index):
        if (layer_index % 3 == 0):
            return 90
        else:
            return self.angle

    def get_layer_direction_modifier(self, layer_index):
        # Make rotation direction alternate every other layer
        if (layer_index % 3 == 1):
            dir_mod = 1
        elif (layer_index % 3 == 2):
            dir_mod = -1
        else:
            dir_mod = self.max_angle_alternator
            self.max_angle_alternator *= -1
        return dir_mod
