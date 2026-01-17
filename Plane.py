import arcade
import math
import vars


class Plane(arcade.Sprite):
    def __init__(self, plane_type, xcoor, ycoor, max_health=100):
        super().__init__()
        # Основные характеристики
        self.plane_type = plane_type  # Тип самолёта (для выбора текстуры)
        self.vx = 350.0  # Проекция скорости по оси X
        self.vy = 0.0  # Проекция скорости по оси Y
        self.vmax = 1500.0  # Максимальная скорость
        self.vmin = 350.0  # Минимальная скорость
        self.v = 350.0
        self.center_x = float(xcoor)  # Текущая координата X
        self.center_y = float(ycoor)  # Текущая координата Y
        self.angle = 0.0  # Угол поворота спрайта
        self.max_health = max_health  # Максимальное здоровье
        self.health = max_health  # Текущее здоровье

        # Загрузка текстуры
        texture_path = f"{plane_type}.png"
        self.texture = arcade.load_texture(texture_path)

    def update(self, delta_time):
        # Обновляем координаты по текущим проекциям скорости
        self.center_x += self.vx * delta_time
        self.center_y += self.vy * delta_time

        # Вычисляем текущую полную скорость
        self.v = (self.vx ** 2 + self.vy ** 2) ** 0.5

        # Ограничиваем скорость в пределах vmin и vmax
        if self.v > self.vmax:
            scale = self.vmax / self.v
            self.vx *= scale
            self.vy *= scale
        elif 0 < self.v < self.vmin:
            scale = self.vmin / self.v
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
        direction_x = abs(math.cos(math.radians(self.angle))) * vars.num_sign(self.vx)
        direction_y = abs(math.sin(math.radians(self.angle))) * vars.num_sign(self.vy)

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

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.kill()

    @property
    def health_percent(self):
        return self.health / self.max_health if self.max_health > 0 else 0

    @property
    def alive(self):
        return self.health > 0

    def set_speed(self, k):
        scale = k / self.v
        self.v *= scale
        self.vx *= scale
        self.vy *= scale