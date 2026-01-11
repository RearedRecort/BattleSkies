import arcade
import random

from arcade.gui import UIManager, UIMessageBox
from Missile import Missile
from Plane import Plane
from Bot import Bot
from start import StartView


class PveView(arcade.View):
    def __init__(self, plane_texture, start_x, start_y):
        super().__init__()
        arcade.set_background_color(arcade.color.LIGHT_GREEN)

        self.world_camera = arcade.Camera2D(zoom=0.5)
        self.gui_camera = arcade.Camera2D()

        self.manager = UIManager()
        self.manager.enable()

        self.planes_list = arcade.SpriteList()
        self.missiles_list = arcade.SpriteList()

        # Игрок
        self.player = Plane(plane_texture, start_x, start_y)
        self.planes_list.append(self.player)

        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.is_pause = False

        # Бот и респавн
        self.current_bot = None
        self.bot_spawn_timer = 0
        self.bot_spawn_delay = 2.0  # секунды задержки между спавнами

        self.spawn_new_bot()

    def spawn_new_bot(self):
        # Случайное появление бота где-то подальше от игрока
        side = random.choice([-1, 1])
        spawn_x = self.player.center_x + random.randint(600, 1200) * side
        spawn_y = random.randint(200, 1000)

        self.current_bot = Bot(
            "F16",
            spawn_x,
            spawn_y,
            target=self.player,
            max_health=80
        )
        self.current_bot.turn_rate = 180
        self.current_bot.shoot_interval = 1.8
        self.planes_list.append(self.current_bot)

    def on_update(self, delta_time):
        # Управление игроком
        self.player.update(delta_time)

        if self.up:
            self.player.vx *= 1.25
            self.player.vy *= 1.25
        if self.down:
            self.player.vx //= 1.25
            self.player.vy //= 1.25
        if self.left:
            self.player.rotate(3)
        if self.right:
            self.player.rotate(-3)

        # Камера следует за игроком
        self.world_camera.position = (
            self.player.center_x,
            self.player.center_y
        )

        # Обновление бота
        if self.current_bot and self.current_bot.alive:
            self.current_bot.update(delta_time)

            # Бот стреляет -> добавляем ракету
            if self.current_bot.shoot_cooldown <= 0:
                missile = self.current_bot.shoot()
                if missile:
                    self.missiles_list.append(missile)
                    self.current_bot.shoot_cooldown = self.current_bot.shoot_interval

        # Обновляем все ракеты
        self.missiles_list.update(delta_time)

        # Проверяем попадания
        # 1. Ракеты -> игрок
        hits_player = arcade.check_for_collision_with_list(self.player, self.missiles_list)
        for missile in hits_player:
            if hasattr(missile, 'sender') and missile.sender == "bot":  # чтобы не попадали свои
                self.player.take_damage(missile.damage)
                missile.kill()

        # 2. Ракеты -> бот
        if self.current_bot and self.current_bot.alive:
            hits_bot = arcade.check_for_collision_with_list(self.current_bot, self.missiles_list)
            for missile in hits_bot:
                if hasattr(missile, 'sender') and missile.sender == "player":
                    self.current_bot.take_damage(missile.damage)
                    missile.kill()

        # Бот умер -> запускаем таймер респавна
        if self.current_bot and not self.current_bot.alive:
            self.current_bot.remove_from_sprite_lists()
            self.current_bot = None
            self.bot_spawn_timer = self.bot_spawn_delay

        # Таймер респавна
        if self.bot_spawn_timer > 0:
            self.bot_spawn_timer -= delta_time
            if self.bot_spawn_timer <= 0:
                self.spawn_new_bot()

        # Игрок умер -> конец игры
        if not self.player.alive:
            self.game_over()

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.planes_list.draw()
        self.missiles_list.draw()

        # Здоровье игрока
        self.gui_camera.use()
        arcade.draw_text(
            f"HP: {self.player.health}/{self.player.max_health}",
            20, 40, arcade.color.BLACK, 18
        )
        self.manager.draw()

    def game_over(self):
        message = UIMessageBox(
            width=400,
            height=250,
            message_text="ИГРА ОКОНЧЕНА\nВы были сбиты!",
            buttons=["В меню"]
        )
        message.on_action = lambda btn: self.window.show_view(StartView())
        self.manager.add(message)

    def pause(self):
        self.message_box = UIMessageBox(
            width=300, height=200,
            message_text="ПАУЗА",
            buttons=("Продолжить", "Выйти в меню")
        )
        self.message_box.on_action = self.stop_pause
        self.manager.add(self.message_box)

    def stop_pause(self, btn):
        if btn.action == "Продолжить":
            self.is_pause = False
        else:
            from start import StartView
            self.window.show_view(StartView())

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = True
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.down = True
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left = True
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = True
        if key == arcade.key.ESCAPE:
            if self.is_pause:
                self.message_box.visible = False
            else:
                self.pause()
            self.is_pause = not self.is_pause

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.down = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = False

    def on_mouse_press(self, x, y, button, modifiers):
        if button == arcade.MOUSE_BUTTON_LEFT:
            missile = self.player.shoot()
            missile.sender = "player"          # метка, что это ракета игрока
            self.missiles_list.append(missile)