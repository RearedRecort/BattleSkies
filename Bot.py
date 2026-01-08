import arcade
import math
from typing import Optional
import random

from Plane import Plane


class Bot(Plane):
    def __init__(self, plane_type, xcoor, ycoor, target: Optional['Plane'] = None,
                 max_health=100):
        super().__init__(plane_type, xcoor, ycoor, max_health)

        # Характеристики ИИ
        self.target = target  # Цель
        self.shoot_cooldown = 0.0  # Кулдаун стрельбы
        self.shoot_interval = 1.5  # Интервал между выстрелами
        self.turn_rate = 180.0  # Скорость поворота

    def update(self, delta_time):
        super().update(delta_time)  # Движение и ограничение скорости

        # Обновляем кулдаун стрельбы
        self.shoot_cooldown = max(0.0, self.shoot_cooldown - delta_time)

        # Если нет цели или цель мертва — случайный полёт
        if not self.target or not self.target.alive:
            self.random_fly(delta_time)
            return

        # Логика преследования
        dx = self.target.center_x - self.center_x
        dy = self.target.center_y - self.center_y

        # Угол к цели
        target_angle = math.degrees(math.atan2(dy, dx))

        # Разница углов
        angle_diff = (target_angle - self.angle + 180) % 360 - 180

        # Поворачиваем к цели с ограниченной скоростью
        turn_amount = max(min(angle_diff, self.turn_rate * delta_time),
                          -self.turn_rate * delta_time)
        self.rotate(turn_amount)

        # Стрельба при хорошем наведении
        if abs(angle_diff) < 10.0 and self.shoot_cooldown <= 0.0:
            self.shoot_at_target()

    def random_fly(self, delta_time: float):
        if random.random() < 0.02:  # ~1 раз в секунду
            random_turn = random.uniform(-3.0, 3.0)
            self.rotate(random_turn)

    def shoot_at_target(self):
        missile = self.shoot()  # Метод из Plane
        # В BattleView нужно добавить: missiles_list.append(missile)
        self.shoot_cooldown = self.shoot_interval

    def set_target(self, new_target: 'Plane'):
        self.target = new_target

    @property
    def ai_level(self) -> str:
        if self.turn_rate < 120:
            return 'Easy'
        elif self.turn_rate < 200:
            return 'Medium'
        else:
            return 'Hard'