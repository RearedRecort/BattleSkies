import math

import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from login import LoginView
from settings import SettingsView


class LoseView(arcade.View):
    def __init__(self, kills_friends, kills_enemy, time, reason):
        super().__init__()
        arcade.set_background_color(arcade.color.AQUA)

        # UIManager — сердце GUI
        self.manager = UIManager()
        self.manager.enable()  # Включить, чтоб виджеты работали

        # Layout для организации — как полки в шкафу
        self.anchor_layout = UIAnchorLayout(y=0)  # Центрирует виджеты
        self.box_layout = UIBoxLayout(vertical=True, space_between=10)  # Вертикальный стек

        # Добавим все виджеты в box, потом box в anchor
        self.setup_widgets(kills_friends, kills_enemy, time, kills_enemy - 2 * kills_friends, reason)  # Функция ниже

        self.anchor_layout.add(self.box_layout)  # Box в anchor
        self.manager.add(self.anchor_layout)  # Всё в manager

        self.all_sprites = arcade.SpriteList()

        vars.clear_sessions()

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        self.manager.draw()

    def setup_widgets(self, kills_friends, kills_enemy, time, money, reason):
        vars.add_money(money)
        label = UILabel(text="ПОРАЖЕНИЕ",
                        font_size=40,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Причина: {reason}",
                        font_size=20,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Убито своих: {kills_friends}",
                        font_size=20,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Убито врагов: {kills_enemy}",
                        font_size=20,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Проведено времени: {math.floor(time // 60)} мин {math.floor(time % 60)} сек",
                        font_size=20,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        label = UILabel(text=f"Заработано монет: {money}",
                        font_size=20,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        btn = UIFlatButton(text="В главное меню", width=400, height=40)
        btn.on_click = self.go
        self.box_layout.add(btn)

    def go(self, event):
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)