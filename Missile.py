import arcade
import math


class Missile(arcade.Sprite):
    def __init__(self, damage, vx, vy, x, y, time_left):
        super().__init__()
        # Характеристики пули
        self.damage = damage  # Урон от попадания
        self.vx = vx  # Проекция скорости по X
        self.vy = vy  # Проекция скорости по Y
        self.center_x = x  # Текущая координата X
        self.center_y = y  # Текущая координата Y
        self.time_left = time_left  # Оставшееся время жизни пули


        self.texture = arcade.load_texture("missile.png")


        # Угол поворота пули соответствует направлению полёта
        self.angle = math.degrees(math.atan2(vy, vx))

    def update(self, delta_time: float):
        # Обновляем позицию по текущим проекциям скорости
        self.center_x += self.vx * delta_time
        self.center_y += self.vy * delta_time

        # Уменьшаем оставшееся время жизни
        self.time_left -= delta_time

        # Если время вышло — удаляем пулю из игры
        if self.time_left <= 0:
            self.kill()