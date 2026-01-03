import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from login import LoginView
from settings import SettingsView
from hub import HubView


class StartView(arcade.View):
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
        label = UILabel(text="БОЕВЫЕ НЕБЕСА",
                        font_size=40,
                        text_color=arcade.color.BLACK,
                        width=300,
                        align="center")
        self.box_layout.add(label)
        single = UIFlatButton(text="Одиночная игра", width=400, height=40)
        single.on_click = self.singleplay
        self.box_layout.add(single)
        multi = UIFlatButton(text="Сетевая игра", width=400, height=40)
        multi.on_click = self.multiplay
        if vars.id == 0:
            multi.disabled = True
        self.box_layout.add(multi)
        account = UIFlatButton(text="Аккаунт и настройки", width=400, height=40)
        account.on_click = self.account
        self.box_layout.add(account)
        ex = UIFlatButton(text="Выйти из игры", width=400, height=40)
        ex.on_click = self.ext
        self.box_layout.add(ex)

    def singleplay(self, event):
        pass

    def multiplay(self, event):
        hub_view = HubView()
        self.window.show_view(hub_view)

    def account(self, event):
        if vars.id == 0:
            login_view = LoginView()  # Передаём текущий вид, чтобы вернуться
            self.window.show_view(login_view)
        else:
            settings_view = SettingsView()
            self.window.show_view(settings_view)

    def ext(self, event):
        vars.clear_sessions()
        arcade.close_window()
