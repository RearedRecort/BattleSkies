import vars
import arcade
import pyglet

from arcade.gui import UIManager, UIMessageBox
from arcade.clock import GLOBAL_CLOCK
from Missile import Missile
from Plane import Plane
from lose import LoseView
from win import WinView


class PvpView(arcade.View):
    def __init__(self, is_owner, game, x, y, team):
        super().__init__()
        self.is_owner = is_owner
        self.game = game
        arcade.set_background_color(arcade.color.LIGHT_GREEN)
        self.world_camera = arcade.camera.Camera2D(zoom=0.5)
        self.gui_camera = arcade.camera.Camera2D()
        self.manager = UIManager()
        self.manager.enable()
        self.planes_list = arcade.SpriteList()
        self.missiles_list = arcade.SpriteList()
        self.player = Plane("PlanesTexture/F-15", x, y)
        self.is_pause = False
        if team:
            self.player.scale_x = -1
        else:
            self.player.vx *= -1
        self.player.vx *= -1
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.was_shouted = []
        self.nick_cache = {}
        self.other_players = {}
        self.name_batch = pyglet.graphics.Batch()
        self.name_labels = {}
        self.kills_friends = 0
        self.kills_enemy = 0

    def world_to_screen(self, x, y):
        try:
            win_w = self.window.width
            win_h = self.window.height
        except Exception:
            win_w, win_h = 800, 600
        cam_pos = getattr(self.world_camera, "position", (0, 0))
        cam_x, cam_y = cam_pos[0], cam_pos[1]
        zoom = getattr(self.world_camera, "zoom", 1.0)
        screen_x = (x - cam_x) * zoom + win_w / 2
        screen_y = (y - cam_y) * zoom + win_h / 2
        return screen_x, screen_y

    def on_update(self, delta_time):
        try:
            cur = vars.con.cursor()
            lstk = cur.execute(f"SELECT * FROM `session` WHERE `game` = {self.game}").fetchall()
            self.planes_list.clear()
            current_pids = set()
            for lst in lstk:
                if lst[1] != vars.id:
                    texture = "PlanesTexture/F-15"
                    k = lst[3]
                    if k == 0:
                        texture = "PlanesTexture/F-15"
                    t = lst[4]
                    x = lst[5]
                    y = lst[6]
                    v = lst[7]
                    angle = lst[8]
                    plane = Plane(texture, x, y)
                    if t:
                        plane.scale_x = -1
                    plane.set_speed(v)
                    plane.rotate(angle)
                    self.planes_list.append(plane)
                    pid = lst[1]
                    current_pids.add(pid)
                    name = self.nick_cache.get(pid)
                    if name is None:
                        row = cur.execute("SELECT nickname FROM `users` WHERE `id` = ?", (pid,)).fetchone()
                        if row and row[0]:
                            name = row[0]
                        else:
                            name = f"Player{pid}"
                        self.nick_cache[pid] = name
                    world_x = plane.center_x
                    world_y = plane.center_y + plane.height / 2 + 8
                    self.other_players[pid] = {
                        'world_x': world_x,
                        'world_y': world_y,
                        'team': t,
                        'name': name
                    }
                    color = arcade.color.BLUE if t == 0 else arcade.color.RED
                    if pid not in self.name_labels:
                        r, g, b = color[0], color[1], color[2]
                        lbl = pyglet.text.Label(
                            name,
                            font_name="Arial",
                            font_size=12,
                            x=0,
                            y=0,
                            anchor_x="center",
                            anchor_y="bottom",
                            color=(r, g, b, 255),
                            batch=self.name_batch
                        )
                        self.name_labels[pid] = lbl
                    else:
                        lbl = self.name_labels[pid]
                        lbl.text = name
                        r, g, b = color[0], color[1], color[2]
                        lbl.color = (r, g, b, 255)
                else:
                    self.player.update(delta_time)
                    if self.up:
                        self.player.vx *= 1.25
                        self.player.vy *= 1.25
                    if self.down:
                        self.player.vx /= 1.25
                        self.player.vy /= 1.25
                    if self.left:
                        self.player.rotate(3)
                    if self.right:
                        self.player.rotate(-3)
                    self.planes_list.append(self.player)
                    x = self.player.center_x
                    y = self.player.center_y
                    v = self.player.v
                    angle = self.player.angle
                    cur.execute(f"UPDATE `session` SET `x` = {x}, `y` = {y}, `v` = {v}, `angle` = {angle} WHERE `game` = {self.game} AND `player` = {vars.id}")
                    vars.con.commit()
                    position = (self.player.center_x, self.player.center_y)
                    self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, position, 1)
            for pid in list(self.name_labels.keys()):
                if pid not in current_pids:
                    lbl = self.name_labels.pop(pid, None)
                    try:
                        if lbl and hasattr(lbl, "delete"):
                            lbl.delete()
                    except Exception:
                        pass
                    self.nick_cache.pop(pid, None)
                    self.other_players.pop(pid, None)
            for pid, info in self.other_players.items():
                wx = info['world_x']
                wy = info['world_y']
                sx, sy = self.world_to_screen(wx, wy)
                lbl = self.name_labels.get(pid)
                if lbl:
                    lbl.x = sx
                    lbl.y = sy
            for el in self.missiles_list:
                el.update(delta_time)
            lst = cur.execute(f"SELECT * FROM `shouting` WHERE `game` = {self.game}").fetchall()
            for el in lst:
                if el[0] not in self.was_shouted:
                    missile = Missile(el[8], el[5], el[6], el[3], el[4], el[7])
                    missile.sender = el[1]
                    self.missiles_list.append(missile)
                    self.was_shouted.append(el[0])
        except Exception:
            if self.is_owner:
                self.transfer_host()
            lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(0.0), "Потеряно соединение")
            self.manager.clear()
            self.window.show_view(lose_view)

    def on_draw(self):
        self.clear()
        self.world_camera.use()
        self.planes_list.draw()
        self.missiles_list.draw()
        self.gui_camera.use()
        try:
            self.name_batch.draw()
        except Exception:
            pass
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
            self.transfer_host()
        cur = vars.con.cursor()
        cur.execute(f"DELETE FROM `session` WHERE `player` = {vars.id}")
        vars.con.commit()
        lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(0.0), "Выход из игры")
        self.manager.clear()
        self.window.show_view(lose_view)

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
        mx = missile.center_x
        my = missile.center_y
        vx = missile.vx
        vy = missile.vy
        damage = missile.damage
        time = missile.time_left
        sender = vars.id
        cur = vars.con.cursor()
        cur.execute("INSERT INTO `shouting` (`game`, `x`, `y`, `vx`, `vy`, `damage`, `time`, `player`" + f") VALUES ({game}, {mx}, {my}, {vx}, {vy}, {damage}, {time}, {sender})")
        vars.con.commit()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.world_camera.zoom += scroll_y * 0.1
        self.world_camera.zoom = min(1.0, self.world_camera.zoom)
        self.world_camera.zoom = max(0.03, self.world_camera.zoom)

    def transfer_host(self):
        cur = vars.con.cursor()
        id = cur.execute("SELECT `player` FROM `session` WHERE `game` =" + f" {self.game} AND `team` = 0 AND `player` <> {vars.id}").fetchall()[0][0]
        cur.execute(f"UPDATE `games` SET `owner` = {id}")
        vars.con.commit()
        self.is_owner = False

    def dead(self):
        if self.is_owner:
            self.transfer_host()
        cur = vars.con.cursor()
        cur.execute(f"DELETE FROM `session` WHERE `player` = {vars.id}")
        vars.con.commit()
        lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(0.0), "Ваш самолёт уничтожен")
        self.manager.clear()
        self.window.show_view(lose_view)
