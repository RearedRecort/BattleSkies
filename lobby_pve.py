import vars
import arcade

from arcade.gui import UIManager, UIFlatButton, UILabel, UISlider, UIDropdown
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout


class LobbyPveView(arcade.View):
    def __init__(self, is_owner, game):
        self.is_owner = is_owner
        self.game = game
        super().__init__()
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
        self.players_list.clear()
        cur = vars.con.cursor()
        lst = cur.execute(f"SELECT `player` FROM `session` WHERE `game` = {self.game}").fetchall()
        for el in lst:
            id = el[0]
            nick = cur.execute(f"SELECT `nickname` FROM `users` WHERE `id` = {id}").fetchall()[0][0]
            lbl = UILabel(text=nick, font_size=15, text_color=arcade.color.BLACK, align="center")
            self.players_list.add(lbl)

    def setup_widgets(self):
        label = UILabel(text="ЛОББИ (PVE)", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)
        self.players_list = UIBoxLayout(vertical=True, space_between=10)
        self.box_layout.add(self.players_list)
        start = UIFlatButton(text="Начать", width=400, height=40)
        start.on_click = self.go
        if not self.is_owner:
            start.disabled = True
        self.box_layout.add(start)
        bck = UIFlatButton(text="Назад", width=400, height=40)
        bck.on_click = self.bck
        self.box_layout.add(bck)
        self.err_label = UILabel(text="", font_size=15, text_color=arcade.color.RED, width=300, align="center")
        self.box_layout.add(self.err_label)

    def bck(self, event):
        vars.clear_sessions()
        from hub import HubView
        hub_view = HubView()
        self.window.show_view(hub_view)

    def go(self, event):
        pass

