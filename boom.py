import arcade
import vars


class Boom(arcade.Sprite):
    def __init__(self, x, y, scale = 1.0):
        super().__init__()
        self.scale = scale
        self.texture = arcade.load_texture("animation/boom (1).png")
        self.center_x = x
        self.center_y = y
        self.list_textures = []
        for i in range(1, vars.images_count):
            texture = arcade.load_texture(f"animation/boom ({i}).png")
            self.list_textures.append(texture)
        self.current_texture = 0
        self.texture_change_time = 0
        self.texture_change_delay = 0.1

    def update(self, delta_time):
        self.texture_change_time += delta_time
        if self.texture_change_time >= self.texture_change_delay:
            self.texture_change_time = 0
            self.current_texture += 1
            if self.current_texture >= len(self.list_textures):
                self.kill()
                return
            self.texture = self.list_textures[self.current_texture]
