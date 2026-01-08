import arcade
from Plane import Plane
from Missile import Missile
from Bot import Bot

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_TITLE = "Тест боя: Plane + Missile + Bot"

class BattleTest(arcade.View):
    def __init__(self):
        super().__init__()
        arcade.set_background_color(arcade.color.SKY_BLUE)

        # Списки спрайтов
        self.planes = arcade.SpriteList()
        self.missiles = arcade.SpriteList()

        # Игрок (управление стрелками + пробел)
        self.player = Plane('Su-27', SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, max_health=150)
        self.player.vx = 0  # Начинаем без движения
        self.player.vy = 0
        self.planes.append(self.player)

        # Бот (преследует игрока)
        self.bot = Bot('F-15', 200, 500, target=self.player, max_health=100)
        self.bot.turn_rate = 200  # Средне-жёсткий
        self.bot.shoot_interval = 1.2
        self.planes.append(self.bot)


    def on_draw(self):
        self.clear()
        self.planes.draw()
        self.missiles.draw()

    def on_update(self, delta_time):
        self.planes.update(delta_time)
        self.missiles.update(delta_time)

        # Bots shoot missiles - add to list
        # Note: In real code, modify Bot to return missile from shoot_at_target
        # For now, assume it's handled or skip

        # Collisions
        for missile in self.missiles[:]:
            hit_list = arcade.check_for_collision_with_list(missile, self.planes)
            for plane in hit_list:
                plane.take_damage(missile.damage)
                missile.kill()

            if (missile.center_x < 0 or missile.center_x > SCREEN_WIDTH or
                missile.center_y < 0 or missile.center_y > SCREEN_HEIGHT):
                missile.kill()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.LEFT:
            self.player.rotate(-5)  # Поворот влево (по часовой)
        elif key == arcade.key.RIGHT:
            self.player.rotate(5)   # Поворот вправо (против часовой)
        elif key == arcade.key.SPACE:
            missile = self.player.shoot()
            self.missiles.append(missile)

    def on_key_release(self, key, modifiers):
        pass

def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, fullscreen=False)
    battle_view = BattleTest()
    window.show_view(battle_view)
    arcade.run()

if __name__ == "__main__":
    main()