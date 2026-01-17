import vars
import arcade


from arcade.gui import UIManager, UIMessageBox
from Missile import Missile
from Plane import Plane


class PvpView(arcade.View):
    def __init__(self, is_owner, game, x, y, team):
        super().__init__()
        self.is_owner = is_owner
        self.game = game
        arcade.set_background_color(arcade.color.LIGHT_GREEN)

        self.world_camera = arcade.camera.Camera2D(zoom=0.5)  # Камера для игрового мира
        self.gui_camera = arcade.camera.Camera2D() # Камера для интерфейса

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        self.planes_list = arcade.SpriteList()
        self.missiles_list = arcade.SpriteList()
        self.player = Plane("PlanesTexture/F-15", x, y)
        self.is_pause = False
        if team:
            self.player.vx *= -1
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.was_shouted = []

    def on_update(self, delta_time):
        cur = vars.con.cursor()
        lstk = cur.execute(f"SELECT * FROM `session` WHERE `game` = {self.game}").fetchall()
        self.planes_list.clear()
        for lst in lstk:
            if lst[1] != vars.id:
                k = lst[3]
                if k == 0:
                    texture = "PlanesTexture/F-15"
                x = lst[5]
                y = lst[6]
                v = lst[7]
                angle = lst[8]
                plane = Plane(texture, x, y)
                plane.set_speed(v)
                plane.rotate(angle)
                self.planes_list.append(plane)
            else:
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
                self.planes_list.append(self.player)
                texture = 0
                x = self.player.center_x
                y = self.player.center_y
                v = self.player.v
                angle = self.player.angle
                cur = vars.con.cursor()
                cur.execute(f"UPDATE `session` SET `x` = {x}, `y` = {y}, `v` = {v}, `angle` = {angle}"
                            + f" WHERE `game` = {self.game} AND `player` = {vars.id}")
                vars.con.commit()
                position = (
                    self.player.center_x,
                    self.player.center_y
                )
                '''self.world_camera.position = arcade.math.lerp_2d(  # Изменяем позицию камеры
                    self.world_camera.position,
                    position,
                    1,  # Плавность следования камеры
                )'''
        for el in self.missiles_list:
            el.update(delta_time)
        lst = cur.execute(f"SELECT * FROM `shouting` WHERE `game` = {self.game}").fetchall()
        for el in lst:
            if el[0] not in self.was_shouted:
                missile = Missile(el[8], el[5], el[6], el[3], el[4], el[7])
                missile.sender = el[1]
                self.missiles_list.append(missile)
                self.was_shouted.append(el[0])
        #stolk = arcade.check_for_collision_with_list(self.player, self.missiles_list)
        #for el in stolk:
            #if el.sender != vars.id:
                #self.disconnect()
        #stolk = arcade.check_for_collision_with_list(self.player, self.planes_list)
        #if len(stolk) != 0:
            #self.disconnect()

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        self.world_camera.use()
        self.planes_list.draw()
        self.missiles_list.draw()
        self.gui_camera.use()
        self.manager.draw()

    def pause(self):
        self.message_box = UIMessageBox(
            width=300, height=200,
            message_text="Пауза",
            buttons=("Продолжить", "Выйти из игры")
        )
        self.message_box.on_action = self.stop_pause
        self.manager.add(self.message_box)

    def disconnect(self):
        if self.is_owner:
            cur = vars.con.cursor()
            cur.execute(f"DELETE FROM `games` WHERE `id` = {self.game}")
            cur.execute(f"DELETE FROM `session` WHERE `game` = {self.game}")
            cur.execute(f"DELETE FROM `shouting` WHERE `game` = {self.game}")
            vars.con.commit()
            from start import StartView
            start_view = StartView()
            self.window.show_view(start_view)
        else:
            cur = vars.con.cursor()
            cur.execute(f"DELETE FROM `session` WHERE `player` = {vars.id}")
            vars.con.commit()
            from start import StartView
            start_view = StartView()
            self.window.show_view(start_view)

    def stop_pause(self, btn):
        if btn.action == "Продолжить":
            self.is_pause = False
        else:
            self.disconnect()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = True
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left = True
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.down = True
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP:
            self.up = False
        if key == arcade.key.A or key == arcade.key.LEFT:
            self.left = False
        if key == arcade.key.S or key == arcade.key.DOWN:
            self.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT:
            self.right = False
        if key == arcade.key.ESCAPE:
            if self.is_pause:
                self.message_box.visible = False
            else:
                self.pause()
            self.is_pause = not self.is_pause

    def on_mouse_press(self, x, y, button, modifiers):
        missile = self.player.shoot()
        game = self.game
        x = missile.center_x
        y = missile.center_y
        vx = missile.vx
        vy = missile.vy
        damage = missile.damage
        time = missile.time_left
        sender = vars.id
        cur = vars.con.cursor()
        cur.execute("INSERT INTO `shouting` (`game`, `x`, `y`, `vx`, `vy`, `damage`, `time`, `player`"
                    + f") VALUES ({game}, {x}, {y}, {vx}, {vy}, {damage}, {time}, {sender})")
        vars.con.commit()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.world_camera.zoom += scroll_y * 0.1
        self.world_camera.zoom = min(1.0, self.world_camera.zoom)
        self.world_camera.zoom = max(0.03, self.world_camera.zoom)
