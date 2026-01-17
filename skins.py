import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from login import LoginView
from settings import SettingsView
from hub import HubView


class SkinView(arcade.View):
    def __init__(self):
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

    def setup_widgets(self):
        label = UILabel(text="Выбор скина",
                        font_size=30,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        lyt = UIBoxLayout(vertical=True, space_between=10)
        for i in range(8):
            btn = UIFlatButton(text=SKIN_MAP[i], width=400, height=40)
            f = lambda e, s = i: self.choose(e, s)
            btn.on_click = f
            self.box_layout.add(btn)

    def choose(self, event, skin):
        vars.plane = skin
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)

    def on_hide_view(self):
        self.manager.clear()


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
