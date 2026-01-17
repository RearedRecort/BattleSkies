# pvb.py
# Исправленная версия PvbView: поддержка ботов (player=0), скинов, камера, стрельба ботов и корректные коллизии
import math
import random
import vars
import arcade
import pyglet

from arcade.gui import UIManager, UIMessageBox
from arcade.clock import GLOBAL_CLOCK
from arcade.particles import FadeParticle, Emitter, EmitMaintainCount
from Missile import Missile
from Plane import Plane
from Bot import Bot
from boom import Boom
from lose import LoseView
from win import WinView

# Скины: номер -> строка, передается первым аргументом Plane
SKIN_MAP = {
    0: "F-15",
    1: "F-16",
    2: "J-35",
    3: "J-39",
    4: "MiG-31",
    5: "Mig-29",
    6: "Su-27",
    7: "Su-47",
}

SPARK_TEX = [
    arcade.make_soft_circle_texture(32, arcade.color.GRAY),
    arcade.make_soft_circle_texture(32, arcade.color.DARK_GRAY),
    arcade.make_soft_circle_texture(32, arcade.color.LIGHT_GRAY),
    arcade.make_soft_circle_texture(32, arcade.color.BLUE_GRAY),
    arcade.make_soft_circle_texture(32, arcade.color.DARK_BLUE_GRAY)
]

def make_trail(attached_sprite, maintain=100):
    emit = Emitter(
        center_xy=(attached_sprite.center_x, attached_sprite.center_y),
        emit_controller=EmitMaintainCount(maintain),
        particle_factory=lambda e: FadeParticle(
            filename_or_texture=random.choice(SPARK_TEX),
            change_xy=arcade.math.rand_in_circle((0.0, 0.0), max(1, int(attached_sprite.height // 2))),
            lifetime=random.uniform(0.35, 0.6),
            start_alpha=220, end_alpha=0,
            scale=random.uniform(0.25, 0.4),
        ),
    )
    emit.attached = attached_sprite
    return emit

class PvbView(arcade.View):
    def __init__(self, is_owner, game, x, y, team):
        super().__init__()
        self.emitters = []
        self.emitters_by_pid = {}
        self.time_to_dead = 1
        self.team = team
        self.is_owner = is_owner
        self.game = game
        arcade.set_background_color(arcade.color.LIGHT_GREEN)
        self.world_camera = arcade.camera.Camera2D(zoom=0.5)
        self.gui_camera = arcade.camera.Camera2D()
        self.manager = UIManager(); self.manager.enable()
        self.planes_list = arcade.SpriteList(); self.missiles_list = arcade.SpriteList()
        skin_name = SKIN_MAP.get(getattr(vars, 'plane', 0), "F-15")
        self.player = Plane(skin_name, x, y)
        if team:
            self.player.scale_x = -1
        else:
            self.player.vx *= -1
        self.player.vx *= -1

        self.left = self.right = self.up = self.down = False
        self.was_shouted = []
        self.nick_cache = {}
        self.other_players = {}
        self.name_batch = pyglet.graphics.Batch(); self.name_labels = {}
        self.kills_friends = 0; self.kills_enemy = 0
        self.dead_scheduled = False; self.alive_local = True; self.win_scheduled = False
        self.is_pause = False; self.message_box = None; self.local_hp = 100
        self.hud_batch = pyglet.graphics.Batch()
        self.hp_label = pyglet.text.Label("", font_name="Arial", font_size=14, x=0, y=0, anchor_x='left', anchor_y='top', color=(255,255,255,255), batch=self.hud_batch)
        self.friends_label = pyglet.text.Label("", font_name="Arial", font_size=14, x=0, y=0, anchor_x='right', anchor_y='top', color=(255,255,255,255), batch=self.hud_batch)
        self.enemy_label = pyglet.text.Label("", font_name="Arial", font_size=14, x=0, y=30, anchor_x='right', anchor_y='top', color=(255,255,255,255), batch=self.hud_batch)
        self.local_explosions = arcade.SpriteList(); self.explosions = set()

        # Локальные объекты ботов (только у хоста)
        self.bots = {}

        self.boom_sound = arcade.load_sound("Sounds/boom.wav")
        self.max_hear_distance = 1200.0
        self.background_music = arcade.load_sound("Sounds/plane.mp3")
        self.time_start = GLOBAL_CLOCK.time_since(0.0)

        if self.is_owner:
            try:
                self._load_bot_objects()
            except Exception:
                pass

    def on_show_view(self):
        self.backgound_player = self.background_music.play(loop=True, volume=0.5)

    def world_to_screen(self, x, y):
        try:
            win_w, win_h = self.window.width, self.window.height
        except Exception:
            win_w, win_h = 800, 600
        cam_x, cam_y = self.world_camera.position[0], self.world_camera.position[1]
        zoom = self.world_camera.zoom
        return (x - cam_x) * zoom + win_w / 2, (y - cam_y) * zoom + win_h / 2

    def insert_explosion(self, cur, x, y, creator, victim):
        try:
            now = GLOBAL_CLOCK.time_since(0.0)
            cur.execute(f"INSERT INTO explosions (game,x,y,ttl,created_by,created_at,victim) VALUES ({self.game},{x},{y},{self.time_to_dead},{creator},{now},{victim})")
            vars.con.commit()
            return cur.lastrowid
        except Exception:
            return None

    def create_local_explosion(self, x, y, victim=None):
        if victim is None or victim not in self.explosions:
            explosion = Boom(x, y, scale=25)
            self.local_explosions.append(explosion)
            px = self.player.center_x; py = self.player.center_y
            dist = math.hypot(px - x, py - y)
            vol = max(0.0, min(1.0, 1.0 - (dist / self.max_hear_distance)))
            arcade.play_sound(self.boom_sound, volume=vol)
            self.explosions.add(victim)

    def on_hide_view(self):
        try: arcade.stop_sound(self.backgound_player)
        except Exception: pass

    def _load_bot_objects(self):
        cur = vars.con.cursor()
        rows = cur.execute(f"SELECT * FROM session WHERE game = {self.game} AND player = 0").fetchall()
        for r in rows:
            sid = r[0]
            skin_num = r[3] if len(r) > 3 and r[3] is not None else getattr(vars, 'plane', 0)
            skin = SKIN_MAP.get(skin_num, "F-15")
            x = r[5]; y = r[6]
            bot = Bot(skin, x, y)
            bot.player_id = -sid
            bot._session_id = sid
            self.bots[sid] = bot

    def _update_bots(self, delta_time):
        if not self.is_owner:
            return
        cur = vars.con.cursor()
        for sid, bot in list(self.bots.items()):
            try:
                bot.update(delta_time)
                hp = getattr(bot, 'hp', 100)
                cur.execute(f"UPDATE session SET x={bot.center_x},y={bot.center_y},v={bot.v},angle={bot.angle},hp={hp} WHERE id={sid}")
                # Попытка заставить бота стрелять: если Bot реализует shoot(), вызываем и сохраняем выстрел в shouting
                try:
                    missile = bot.shoot()
                    if missile:
                        # Сохраняем выстрел в shouting: shooter player = 0
                        mx = missile.center_x; my = missile.center_y; vx = missile.vx; vy = missile.vy
                        damage = getattr(missile, 'damage', 1); time_left = getattr(missile, 'time_left', 5)
                        cur.execute(f"INSERT INTO shouting (game,x,y,vx,vy,damage,time,player) VALUES ({self.game},{mx},{my},{vx},{vy},{damage},{time_left},0)")
                        vars.con.commit()
                        try:
                            last_id = cur.lastrowid
                            if last_id:
                                self.was_shouted.append(last_id)
                        except Exception:
                            pass
                        missile.sender = 0
                        self.missiles_list.append(missile)
                except Exception:
                    # если бот не поддерживает shoot() — игнорируем
                    pass
            except Exception:
                pass
        vars.con.commit()

    def on_update(self, delta_time):
        try:
            cur = vars.con.cursor()
            if self.is_owner:
                self._update_bots(delta_time)

            rows = cur.execute(f"SELECT * FROM session WHERE game = {self.game}").fetchall()
            self.planes_list.clear(); current_pids = set(); local_present = False

            for r in rows:
                sid = r[0]; pid = r[1]
                skin_num = r[3] if len(r) > 3 and r[3] is not None else getattr(vars, 'plane', 0)
                skin_name = SKIN_MAP.get(skin_num, "F-15")
                x = r[5]; y = r[6]

                if pid == 0:
                    internal_pid = -sid
                    plane = Plane(skin_name, x, y)
                    plane.player_id = internal_pid
                    current_pids.add(internal_pid)
                    name = "ИИ"
                    hp = r[9] if len(r)>9 and r[9] is not None else 100
                    self.other_players[internal_pid] = {'world_x': x, 'world_y': y + plane.height/2 + 8, 'team': 1, 'name': name, 'hp': hp, 'screen_x':0, 'screen_y':0}
                    if internal_pid not in self.name_labels:
                        col = arcade.color.RED
                        self.name_labels[internal_pid] = pyglet.text.Label(name, font_name="Arial", font_size=12, x=0, y=0, anchor_x='center', anchor_y='bottom', color=(col[0],col[1],col[2],255), batch=self.name_batch)
                    self.planes_list.append(plane)
                    # На хосте используем реальный Bot объект для эмиттеров
                    if self.is_owner and sid in self.bots:
                        bot = self.bots[sid]
                        bot.center_x = x; bot.center_y = y
                        if internal_pid in self.emitters_by_pid:
                            self.emitters_by_pid[internal_pid].attached = bot
                        else:
                            em = make_trail(bot, maintain=80); em.attached = bot
                            self.emitters.append(em); self.emitters_by_pid[internal_pid] = em
                else:
                    if pid != vars.id:
                        plane = Plane(skin_name, x, y)
                        plane.player_id = pid
                        current_pids.add(pid)
                        name = self.nick_cache.get(pid)
                        if name is None:
                            q = cur.execute(f"SELECT nickname FROM users WHERE id = {pid}").fetchone()
                            name = q[0] if q and q[0] else f"Player{pid}"
                            self.nick_cache[pid] = name
                        hp = r[9] if len(r)>9 and r[9] is not None else 100
                        self.other_players[pid] = {'world_x': x, 'world_y': y + plane.height/2 + 8, 'team': r[4], 'name': name, 'hp': hp, 'screen_x':0, 'screen_y':0}
                        if pid not in self.name_labels:
                            col = arcade.color.BLUE if r[4] == 0 else arcade.color.RED
                            self.name_labels[pid] = pyglet.text.Label(name, font_name="Arial", font_size=12, x=0, y=0, anchor_x='center', anchor_y='bottom', color=(col[0],col[1],col[2],255), batch=self.name_batch)
                        self.planes_list.append(plane)
                    else:
                        local_present = True
                        try:
                            if len(r) > 9 and r[9] is not None:
                                self.local_hp = int(r[9])
                        except Exception:
                            pass
                        self.player.update(delta_time)
                        if self.up:
                            self.player.vx *= 1.25; self.player.vy *= 1.25
                        if self.down:
                            self.player.vx /= 1.25; self.player.vy /= 1.25
                        if self.left: self.player.rotate(3)
                        if self.right: self.player.rotate(-3)
                        self.player.player_id = vars.id
                        self.planes_list.append(self.player)
                        cur.execute(f"UPDATE session SET x={self.player.center_x},y={self.player.center_y},v={self.player.v},angle={self.player.angle} WHERE game={self.game} AND player={vars.id}")
                        vars.con.commit()
                        # Центрируем камеру на игроке
                        self.world_camera.position = arcade.math.lerp_2d(self.world_camera.position, (self.player.center_x, self.player.center_y), 1)

            # Обработка эксплозий
            try:
                elst = cur.execute(f"SELECT x, y, victim FROM explosions WHERE game={self.game}").fetchall()
                for er in elst:
                    x, y, pid = er
                    self.create_local_explosion(x, y, victim=pid)
            except Exception:
                pass

            # Столкновения снарядов
            missiles_to_remove = []
            for missile in list(self.missiles_list):
                for plane in list(self.planes_list):
                    pid = getattr(plane, 'player_id', None)
                    if pid is None or missile.sender == pid:
                        continue
                    if arcade.check_for_collision(missile, plane):
                        missiles_to_remove.append(missile)
                        try:
                            if pid < 0:
                                sid = -pid
                                victim_row = cur.execute(f"SELECT team,hp FROM session WHERE id = {sid} AND game = {self.game}").fetchone()
                            else:
                                victim_row = cur.execute(f"SELECT team,hp FROM session WHERE player = {pid} AND game = {self.game}").fetchone()
                            if not victim_row:
                                break
                            victim_team, victim_hp = victim_row[0], victim_row[1] or 0
                            new_hp = max(0, victim_hp - getattr(missile, 'damage', 1))
                            if new_hp <= 0:
                                try:
                                    if pid == vars.id:
                                        ex, ey = self.player.center_x, self.player.center_y
                                    else:
                                        info = self.other_players.get(pid)
                                        ex = info['world_x'] if info else plane.center_x
                                        ey = info['world_y'] if info else plane.center_y
                                    self.insert_explosion(cur, ex, ey, missile.sender, pid)
                                except Exception:
                                    pass
                            if pid < 0:
                                sid = -pid
                                cur.execute(f"UPDATE session SET hp={new_hp} WHERE id={sid}")
                            else:
                                cur.execute(f"UPDATE session SET hp={new_hp} WHERE player={pid} AND game={self.game}")
                            vars.con.commit()
                            if new_hp <= 0:
                                # удаляем сессию
                                if pid < 0:
                                    sid = -pid
                                    cur.execute(f"DELETE FROM session WHERE id = {sid}")
                                    # удалить локально бота и эмиттер
                                    try:
                                        self.bots.pop(sid, None)
                                        em = self.emitters_by_pid.pop(pid, None)
                                        if em:
                                            try: self.emitters.remove(em)
                                            except Exception: pass
                                    except Exception:
                                        pass
                                else:
                                    cur.execute(f"DELETE FROM session WHERE player = {pid} AND game = {self.game}")
                                vars.con.commit()
                                if pid == vars.id:
                                    if not self.dead_scheduled:
                                        self.dead_scheduled = True
                                        pyglet.clock.schedule_once(self.do_dead, self.time_to_dead)
                                    return
                        except Exception:
                            pass
                        break
            for m in missiles_to_remove:
                try: self.missiles_list.remove(m)
                except Exception: pass

            # Обновление эмиттеров и загрузка новых выстрелов
            for pid, info in self.other_players.items():
                sx, sy = self.world_to_screen(info['world_x'], info['world_y'])
                lbl = self.name_labels.get(pid)
                if lbl:
                    lbl.x = sx; lbl.y = sy
                info['screen_x'] = sx; info['screen_y'] = sy

            emitters_copy = self.emitters.copy()
            for e in emitters_copy:
                attached = getattr(e, 'attached', None)
                if attached is not None:
                    try: e.center_xy = (attached.center_x, attached.center_y)
                    except Exception: pass
                e.update(delta_time)
            for e in emitters_copy:
                if e.can_reap():
                    try: self.emitters.remove(e)
                    except Exception: pass
                    for pid, em in list(self.emitters_by_pid.items()):
                        if em is e: self.emitters_by_pid.pop(pid, None)

            lst = cur.execute(f"SELECT * FROM shouting WHERE game = {self.game}").fetchall()
            for el in lst:
                if el[0] not in self.was_shouted:
                    # columns: id,player,game,x,y,vx,vy,time,damage
                    missile = Missile(el[8], el[5], el[6], el[3], el[4], el[7])
                    missile.sender = el[1]
                    self.missiles_list.append(missile)
                    self.was_shouted.append(el[0])

        except Exception:
            if self.is_owner:
                try: self.transfer_host()
                except Exception: pass
            lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(0.0), "Потеряно соединение")
            self.manager.clear(); self.window.show_view(lose_view)

    def on_draw(self):
        self.clear(); self.world_camera.use(); self.planes_list.draw(); self.missiles_list.draw()
        for e in self.emitters: e.draw()
        self.local_explosions.draw(); self.gui_camera.use()
        try: self.hud_batch.draw()
        except Exception: pass
        try: self.name_batch.draw()
        except Exception: pass
        try:
            for pid, info in self.other_players.items():
                sx = info.get('screen_x'); sy = info.get('screen_y'); hp = info.get('hp',100)
                if sx is None or sy is None: continue
                bar_w = 50; bar_h = 6; left = sx - bar_w/2; right = sx + bar_w/2; y_bar = sy - 6
                top = y_bar + bar_h/2; bottom = y_bar - bar_h/2
                arcade.draw_rect_filled(arcade.rect.LRBT(left, right, bottom, top), arcade.color.BLACK)
                fg_w = int(bar_w * max(0, min(1, hp/100)))
                if fg_w > 0:
                    left_fg = sx - bar_w/2; right_fg = left_fg + fg_w
                    arcade.draw_rect_filled(arcade.rect.LRBT(left_fg, right_fg, bottom, top), arcade.color.DARK_RED)
        except Exception: pass
        self.manager.draw()

    def pause(self):
        self.message_box = UIMessageBox(width=300, height=200, message_text="Пауза", buttons=("Продолжить", "Выйти из игры"))
        self.message_box.on_action = self.stop_pause; self.manager.add(self.message_box)

    def disconnect(self):
        if self.is_owner: self.transfer_host()
        cur = vars.con.cursor(); cur.execute(f"DELETE FROM session WHERE player = {vars.id}"); vars.con.commit()
        lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(0.0), "Выход из игры")
        self.manager.clear(); self.window.show_view(lose_view)

    def stop_pause(self, btn):
        if btn.action == "Продолжить":
            self.is_pause = False
            if self.message_box: self.message_box.visible = False
        else:
            self.disconnect()

    def on_key_press(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP: self.up = True
        if key == arcade.key.A or key == arcade.key.LEFT: self.left = True
        if key == arcade.key.S or key == arcade.key.DOWN: self.down = True
        if key == arcade.key.D or key == arcade.key.RIGHT: self.right = True

    def on_key_release(self, key, modifiers):
        if key == arcade.key.W or key == arcade.key.UP: self.up = False
        if key == arcade.key.A or key == arcade.key.LEFT: self.left = False
        if key == arcade.key.S or key == arcade.key.DOWN: self.down = False
        if key == arcade.key.D or key == arcade.key.RIGHT: self.right = False
        if key == arcade.key.ESCAPE:
            if self.is_pause:
                if self.message_box: self.message_box.visible = False
            else: self.pause()
            self.is_pause = not self.is_pause

    def on_mouse_press(self, x, y, button, modifiers):
        missile = self.player.shoot()
        game = self.game; mx = missile.center_x; my = missile.center_y; vx = missile.vx; vy = missile.vy
        damage = missile.damage; time = missile.time_left; sender = vars.id
        cur = vars.con.cursor()
        cur.execute(f"INSERT INTO shouting (game,x,y,vx,vy,damage,time,player) VALUES ({game},{mx},{my},{vx},{vy},{damage},{time},{sender})")
        vars.con.commit(); missile.sender = sender; self.missiles_list.append(missile)
        try:
            last_id = cur.lastrowid
            if last_id: self.was_shouted.append(last_id)
        except Exception: pass

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.world_camera.zoom += scroll_y * 0.1; self.world_camera.zoom = min(1.0, self.world_camera.zoom); self.world_camera.zoom = max(0.03, self.world_camera.zoom)

    def transfer_host(self):
        cur = vars.con.cursor()
        row = cur.execute(f"SELECT player FROM session WHERE game = {self.game} AND team = 0 AND player <> {vars.id}").fetchall()
        if not row: return
        nid = row[0][0]
        cur.execute(f"UPDATE games SET owner = {nid} WHERE id = {self.game}")
        vars.con.commit(); self.is_owner = False

    def schedule_dead(self):
        if self.dead_scheduled: return
        self.dead_scheduled = True; pyglet.clock.schedule_once(self.do_dead, 0.0)

    def do_dead(self, dt):
        try:
            if self.is_owner: self.transfer_host()
            cur = vars.con.cursor(); cur.execute(f"DELETE FROM session WHERE player = {vars.id}"); vars.con.commit()
        except Exception: pass
        lose_view = LoseView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(self.time_start), "Ваш самолёт уничтожен")
        self.manager.clear(); self.window.show_view(lose_view)

    def do_win(self, dt):
        try:
            if self.is_owner: self.transfer_host()
        except Exception: pass
        cur = vars.con.cursor(); cur.execute(f"DELETE FROM session WHERE player = {vars.id}"); vars.con.commit()
        win_view = WinView(self.kills_friends, self.kills_enemy, GLOBAL_CLOCK.time_since(self.time_start))
        self.manager.clear(); self.window.show_view(win_view)

    def dead(self):
        self.schedule_dead()
