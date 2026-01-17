import arcade
import math

from arcade.math import rand_vec_spread_deg
from arcade.particles import FadeParticle, Emitter, EmitBurst, EmitInterval, EmitMaintainCount, LifetimeParticle


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.BLACK)
        self.planes_list = arcade.SpriteList()
        self.plane = arcade.Sprite("path/to/your/plane.png") # Замени на путь к своей текстуре самолёта
        self.plane.center_x = 100
        self.plane.center_y = 100
        self.plane.scale = 1
        self.planes_list.append(self.plane)
        self.emitter = None
        self.particle_list = arcade.SpriteList()

    def setup(self):
        pass

    def create_rotated_emitter(self, sprite):
        """
        Создает эмиттер частиц, учитывая угол поворота и масштаб спрайта.
        """
        # Настройки эмиттера
        rate = 20 # Частиц в секунду
        particle_speed = 50
        particle_lifetime = 1.5
        particle_scale = 0.5

        # Определяем смещение точки испускания частиц от центра спрайта
        # (где находится "главная" сторона)
        main_side_offset = 50  # Расстояние от центра спрайта до главной стороны
        angle_radians = math.radians(sprite.angle)

        # Учитываем масштаб по X для определения стороны испускания
        if sprite.scale_x < 0:
            main_side_offset *= -1

        # Вычисляем позицию эмиттера с учетом поворота спрайта
        emitter_x = sprite.center_x + main_side_offset * math.cos(angle_radians)
        emitter_y = sprite.center_y + main_side_offset * math.sin(angle_radians)

        # Создаем эмиттер
        self.emitter = Emitter(
            center_xy=(emitter_x, emitter_y),
            emit_controller=EmitInterval(rate),
            particle_factory=lambda emitter: LifetimeParticle(
                filename_or_texture="path/to/your/particle.png",  # Замени на путь к текстуре частицы
                change_xy=rand_vec_spread_deg(particle_speed, 90), # Разброс в 90 градусов
                lifetime=particle_lifetime,
                scale=particle_scale
            )
        )
        
        # Добавляем эмиттер в список спрайтов для отрисовки
        self.particle_list = arcade.SpriteList() # Создаем список частиц
        self.particle_list.append(self.emitter)

    def update_emitter(self, sprite):
        """
        Обновляет позицию эмиттера, учитывая угол поворота и масштаб спрайта.
        """
        if self.emitter is None:
            self.create_rotated_emitter(sprite)

        main_side_offset = 50
        angle_radians = math.radians(sprite.angle)

        if sprite.scale_x < 0:
            main_side_offset *= -1

        emitter_x = sprite.center_x + main_side_offset * math.cos(angle_radians)
        emitter_y = sprite.center_y + main_side_offset * math.sin(angle_radians)

        self.emitter.center_x = emitter_x
        self.emitter.center_y = emitter_y
        self.emitter.angle = sprite.angle  # Поворачиваем эмиттер вместе со спрайтом
        self.emitter.update()  # Обновляем эмиттер для генерации новых частиц

        # Обновляем частицы
        for particle in self.emitter.particle_list:
            particle.update()
            
    def on_update(self, delta_time):
        # ВАЖНО: Сначала обновляем спрайт самолета (например, поворачиваем)
        self.plane.angle += 1
        self.update_emitter(self.plane)
        self.planes_list.update() # Обновляем список спрайтов

    def on_draw(self):
        arcade.start_render()
        self.planes_list.draw()

        # Отрисовываем частицы
        if self.emitter:
            self.emitter.draw()
            for particle in self.emitter.particle_list:
                particle.draw()

window = MyGame(600, 600, "Particle Example")
arcade.run()