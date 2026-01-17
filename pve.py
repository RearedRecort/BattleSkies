import math
import random
import arcade

from Missile import Missile
from Plane import Plane
from Bot import Bot
from lose import LoseView


class PveView(arcade.View):

    def __init__(self, plane_index: int = 0):
        super().__init__()

        # Список всех доступных моделей самолётов
        self.plane_types = [
            "F-15", "F-16", "J-35", "J-39",
            "MiG-31", "MiG-29", "Su-27", "Su-47"
        ]

        self.plane_type = self.plane_types[plane_index % len(self.plane_types)]

        arcade.set_background_color(arcade.color.DARK_GREEN)

        # Камеры
        self.world_camera = arcade.Camera2D()
        self.gui_camera   = arcade.Camera2D()

        # Начальный масштаб и границы зума
        self.world_camera.zoom = 0.8
        self.min_zoom = 0.4
        self.max_zoom = 1.8

        # Основные списки спрайтов (взрывы убраны)
        self.planes   = arcade.SpriteList()
        self.missiles = arcade.SpriteList()

        # Игрок в центре экрана
        w, h = self.window.width, self.window.height
        self.player = Plane(self.plane_type, w // 2, h // 2, max_health=120)
        self.planes.append(self.player)

        # Управление
        self.keys = {"left": False, "right": False, "up": False, "down": False}

        # Боты
        self.bots = []
        self.bot_spawn_timer = 0.0
        self.bot_spawn_interval = 3.5
        self.max_bots = 6

        self.score = 0
        self.time_alive = 0.0

        # Первый бот сразу
        self.spawn_bot()

    def spawn_bot(self):
        if len(self.bots) >= self.max_bots:
            return

        margin = 800
        w, h = self.window.width, self.window.height

        side = random.choice(["left", "right", "top", "bottom"])

        if side == "left":
            x = -margin
            y = random.uniform(-margin, h + margin)
        elif side == "right":
            x = w + margin
            y = random.uniform(-margin, h + margin)
        elif side == "top":
            x = random.uniform(-margin, w + margin)
            y = h + margin
        else:
            x = random.uniform(-margin, w + margin)
            y = -margin

        bot = Bot(
            plane_type=random.choice(self.plane_types),
            xcoor=x,
            ycoor=y,
            target=self.player,
            max_health=80 + int(self.score * 0.4)
        )

        bot.turn_rate = 140 + self.score * 1.2
        bot.shoot_interval = max(1.2, 2.2 - self.score * 0.015)

        self.bots.append(bot)
        self.planes.append(bot)

    def on_update(self, delta_time: float):
        self.time_alive += delta_time

        # Управление игроком
        turn_speed = 220
        accel = 380
        decel = 140

        if self.keys["left"]:
            self.player.rotate(turn_speed * delta_time)
        if self.keys["right"]:
            self.player.rotate(-turn_speed * delta_time)
        if self.keys["up"]:
            self.player.v = min(self.player.v + accel * delta_time, 1800)
        if self.keys["down"]:
            self.player.v = max(self.player.v - decel * delta_time, 320)

        self.player.update(delta_time)

        # Спавн ботов
        self.bot_spawn_timer += delta_time
        if self.bot_spawn_timer >= self.bot_spawn_interval:
            self.spawn_bot()
            self.bot_spawn_timer = 0.0

        # Обновление ботов
        for bot in self.bots[:]:
            bot.update(delta_time)

            if bot.target and bot.target.alive and bot.shoot_cooldown <= 0:
                dx = bot.target.center_x - bot.center_x
                dy = bot.target.center_y - bot.center_y
                target_angle = math.degrees(math.atan2(dy, dx))
                diff = (target_angle - bot.angle + 180) % 360 - 180

                if abs(diff) < 12:
                    missile = bot.shoot()
                    self.missiles.append(missile)
                    bot.shoot_cooldown = bot.shoot_interval

            if not bot.alive:
                self.score += 1
                self.bots.remove(bot)
                bot.kill()

        # Ракеты
        for missile in self.missiles[:]:
            missile.update(delta_time)

            if missile.collides_with_sprite(self.player):
                self.player.take_damage(missile.damage)
                missile.kill()
                if self.player.health <= 0:
                    self.game_over()

            for bot in self.bots:
                if missile.collides_with_sprite(bot):
                    bot.take_damage(missile.damage)
                    missile.kill()
                    break

            if missile.time_left <= 0:
                missile.kill()

        # Камера плавно следует за игроком
        target_x = self.player.center_x
        target_y = self.player.center_y

        self.world_camera.position = arcade.math.lerp_2d(
            self.world_camera.position,
            (target_x, target_y),
            0.15
        )

        # Усложнение со временем
        if self.time_alive > 60:
            self.bot_spawn_interval = max(1.8, 3.5 - (self.time_alive - 60) * 0.02)
            self.max_bots = min(10, 6 + int((self.time_alive - 60) // 45))

    def game_over(self):
        view = LoseView(
            kills_friends=0,
            kills_enemy=self.score,
            time=self.time_alive,
            reason="Ваш самолёт сбит"
        )
        self.window.show_view(view)

    def on_draw(self):
        self.clear()

        # Активируем камеру мира
        self.world_camera.use()

        self.planes.draw()
        self.missiles.draw()

        # Переключаемся на камеру интерфейса
        self.gui_camera.use()

        # HUD
        arcade.draw_text(
            f"Здоровье: {int(self.player.health)} / {self.player.max_health}",
            20, self.window.height - 40,
            arcade.color.WHITE, 18, font_name="Kenney Future"
        )

        arcade.draw_text(
            f"Сбито: {self.score}",
            20, self.window.height - 70,
            arcade.color.LIME_GREEN, 18, font_name="Kenney Future"
        )

        minutes = int(self.time_alive // 60)
        seconds = int(self.time_alive % 60)
        arcade.draw_text(
            f"Время: {minutes:02d}:{seconds:02d}",
            20, self.window.height - 100,
            arcade.color.WHITE_SMOKE, 16
        )

        arcade.draw_text(
            f"Самолёт: {self.plane_type}",
            self.window.width - 220, self.window.height - 40,
            arcade.color.CYAN, 16,
            anchor_x="right"
        )

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.keys["left"] = True
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.keys["right"] = True
        if key in (arcade.key.W, arcade.key.UP):
            self.keys["up"] = True
        if key in (arcade.key.S, arcade.key.DOWN):
            self.keys["down"] = True

        if key == arcade.key.ESCAPE:
            self.window.close()

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.A, arcade.key.LEFT):
            self.keys["left"] = False
        if key in (arcade.key.D, arcade.key.RIGHT):
            self.keys["right"] = False
        if key in (arcade.key.W, arcade.key.UP):
            self.keys["up"] = False
        if key in (arcade.key.S, arcade.key.DOWN):
            self.keys["down"] = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            missile = self.player.shoot()
            self.missiles.append(missile)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        # Зум камеры колесом мыши
        self.world_camera.zoom += scroll_y * 0.1
        self.world_camera.zoom = min(1.0, self.world_camera.zoom)
        self.world_camera.zoom = max(0.03, self.world_camera.zoom)