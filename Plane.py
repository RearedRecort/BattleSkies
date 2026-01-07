import arcade
import os
import math


class Plane(arcade.Sprite):
    def __init__(self, plane_type, xcoor, ycoor):
        super().__init__()
        # Основные характеристики
        self.plane_type = plane_type  # Тип самолёта (для выбора текстуры)
        self.vx = 350.0  # Проекция скорости по оси X
        self.vy = 0.0  # Проекция скорости по оси Y
        self.vmax = 1500.0  # Максимальная скорость
        self.vmin = 350.0  # Минимальная скорость
        self.center_x = float(xcoor)  # Текущая координата X
        self.center_y = float(ycoor)  # Текущая координата Y
        self.angle = 0.0  # Угол поворота спрайта

        # Загрузка текстуры
        texture_path = os.path.abspath(f'{plane_type}.jpg')
        self.texture = arcade.load_texture(texture_path)


    def update(self, delta_time):
        # Обновляем координаты по текущим проекциям скорости
        self.center_x += self.vx * delta_time
        self.center_y += self.vy * delta_time

        # Вычисляем текущую полную скорость
        current_speed = (self.vx ** 2 + self.vy ** 2) ** 0.5

        # Ограничиваем скорость в пределах vmin и vmax
        if current_speed > self.vmax:
            scale = self.vmax / current_speed
            self.vx *= scale
            self.vy *= scale
        elif 0 < current_speed < self.vmin:
            scale = self.vmin / current_speed
            self.vx *= scale
            self.vy *= scale

    def rotate(self, n):
        # Поворачиваем спрайт
        self.angle -= n

        # Поворачиваем вектор скорости
        radians = math.radians(n)
        cos_val = math.cos(radians)
        sin_val = math.sin(radians)

        new_vx = self.vx * cos_val - self.vy * sin_val
        new_vy = self.vx * sin_val + self.vy * cos_val

        self.vx = new_vx
        self.vy = new_vy

    def shoot(self):
        from Missile import Missile

        damage = 10  # Урон
        missile_speed = 2000.0  # Скорость пули относительно самолёта

        # Направление носа самолёта
        direction_x = math.cos(math.radians(self.angle))
        direction_y = -math.sin(math.radians(self.angle))

        # Скорость пули = скорость самолёта + скорость выстрела в направлении носа
        missile_vx = self.vx + direction_x * missile_speed
        missile_vy = self.vy + direction_y * missile_speed

        time_left = 5.0  # Время жизни пули в секундах

        missile = Missile(
            damage=damage,
            vx=missile_vx,
            vy=missile_vy,
            x=self.center_x,
            y=self.center_y,
            time_left=time_left
        )

        # Угол пули совпадает с направлением полёта
        missile.angle = math.degrees(math.atan2(missile_vy, missile_vx))

        return missile