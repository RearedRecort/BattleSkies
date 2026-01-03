from pyglet.libs.win32.constants import NULLREGION

import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UISlider, UIDropdown
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

from lobby_pve import LobbyPveView
from lobby_pvp import LobbyPvpView


class CreatingView(arcade.View):
    def __init__(self, code):
        super().__init__()
        self.code = code
        arcade.set_background_color(arcade.color.AQUA)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout(y=0)  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets()  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

        self.all_sprites = arcade.SpriteList()

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        self.manager.draw()

    def on_update(self, delta_time):
        self.count_label.text = "Самолётов в команде: " + str(int(self.count.value))
        self.count.width = 395 - self.count_label.width

    def setup_widgets(self):
        label = UILabel(text="Создать лобби", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)
        lbl = UILabel(text="Код: " + str(self.code), font_size=15,
                      text_color=arcade.color.BLACK, width=300, align="left")
        self.box_layout.add(lbl)
        self.count_layout = UIBoxLayout(vertical=False, space_between=5)
        self.count_label = UILabel(text="Самолётов в команде: ", font_size=15,
                                   text_color=arcade.color.BLACK, align="right")
        self.count = UISlider(x=0, y=0, width=(395 - self.count_label.width),
                              height=40, value=5, min_value=1, max_value=10, step=1)
        self.count_layout.add(self.count_label)
        self.count_layout.add(self.count)
        self.box_layout.add(self.count_layout)
        self.mp_layout = UIBoxLayout(vertical=False, space_between=5)
        mp_label = UILabel(text="Карта:", font_size=15,
                                   text_color=arcade.color.BLACK, align="right")
        self.mp = UIDropdown(x=0, y=0, width=(395 - mp_label.width),
                              height=40, options=["Пустыня", "Горы", "Город"])
        self.mp.value = "Пустыня"
        self.mp_layout.add(mp_label)
        self.mp_layout.add(self.mp)
        self.box_layout.add(self.mp_layout)
        self.mode_layout = UIBoxLayout(vertical=False, space_between=5)
        mode_label = UILabel(text="Режим:", font_size=15,
                           text_color=arcade.color.BLACK, align="right")
        self.mode = UIDropdown(x=0, y=0, width=(395 - mode_label.width),
                             height=40, options=["PVP", "PVE"])
        self.mode.value = "PVP"
        self.mode_layout.add(mode_label)
        self.mode_layout.add(self.mode)
        self.box_layout.add(self.mode_layout)
        self.prv_layout = UIBoxLayout(vertical=False, space_between=5)
        prv_label = UILabel(text="Сервер:", font_size=15,
                             text_color=arcade.color.BLACK, align="right")
        self.prv = UIDropdown(x=0, y=0, width=(395 - prv_label.width),
                               height=40, options=["Приватный", "Публичный"])
        self.prv.value = "Приватный"
        self.prv_layout.add(prv_label)
        self.prv_layout.add(self.prv)
        self.box_layout.add(self.prv_layout)
        crt = UIFlatButton(text="Создать", width=400, height=40)
        crt.on_click = self.create
        self.box_layout.add(crt)
        bck = UIFlatButton(text="Назад", width=400, height=40)
        bck.on_click = self.bck
        self.box_layout.add(bck)
        self.err_label = UILabel(text="", font_size=15, text_color=arcade.color.RED, width=300, align="center")
        self.box_layout.add(self.err_label)

    def create(self, event):
        cur = vars.con.cursor()
        count = int(self.count.value)
        code = self.code
        codes = cur.execute(f"SELECT * FROM `games` WHERE `code` = '{code}'").fetchall()
        if len(codes) > 0:
            self.err_label.text = "Ваш код не уникальный, попробуйте позднее."
            return
        prv = 1
        if self.prv.value == "Публичный":
            prv = 0
        mode = 0
        if self.mode.value == "PVP":
            mode = 1
        mp = 1
        if self.mp.value == "Горы":
            mp = 2
        if self.mp.value == "Город":
            mp = 3
        s = "INSERT INTO `games` (`map`, `players`, `owner`, `mode`, `code`, `private`"
        cur.execute(s + f") VALUES ({mp}, {count}, {vars.id}, {mode}, '{code}', {prv})")
        vars.con.commit()
        game_id = cur.execute(f"SELECT `id` FROM `games` WHERE `code` = '{code}'").fetchall()[0][0]
        cur.execute(f"INSERT INTO `session` (`player`, `game`, `plane`) VALUES ({vars.id}, {game_id}, 0)")
        vars.con.commit()
        if mode:
            lobby_view = LobbyPvpView(True, game_id)
        else:
            lobby_view = LobbyPveView(True, game_id)
        self.window.show_view(lobby_view)

    def bck(self, event):
        from hub import HubView
        hub_view = HubView()
        self.window.show_view(hub_view)
