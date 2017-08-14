class DefaultAngleTargeter:
    def __init__(self, angle):
        self.angle = angle

    def get_layer_target_angle(self, layer_index):
        return self.angle

    def get_layer_direction_modifier(self, layer_index):
        # Make rotation direction alternate every other layer
        if (layer_index % 2 == 0):
            dir_mod = 1
        else:
            dir_mod = -1
        return dir_mod
