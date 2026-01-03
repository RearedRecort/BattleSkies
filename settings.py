import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from changing import ChangingView


class SettingsView(arcade.View):
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
        label = UILabel(text="Настройки", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)

        pass_change = UIFlatButton(text="Сменить пароль", width=400, height=40)
        pass_change.on_click = self.pass_change
        self.box_layout.add(pass_change)
        nickname_change = UIFlatButton(text="Сменить псевдоним", width=400, height=40)
        nickname_change.on_click = self.nickname_change
        self.box_layout.add(nickname_change)
        email_change = UIFlatButton(text="Сменить электронную почту", width=400, height=40)
        email_change.on_click = self.email_change
        self.box_layout.add(email_change)
        bck = UIFlatButton(text="Назад", width=400, height=40)
        bck.on_click = self.bck
        self.box_layout.add(bck)
        logout = UIFlatButton(text="Выйти из аккаунта", width=400, height=40)
        logout.on_click = self.logout
        self.box_layout.add(logout)
        self.err_label = UILabel(text="", font_size=15, text_color=arcade.color.RED, width=300, align="center")
        self.box_layout.add(self.err_label)

    def pass_change(self, event):
        changing_view = ChangingView("password")
        self.window.show_view(changing_view)

    def nickname_change(self, event):
        changing_view = ChangingView("nickname")
        self.window.show_view(changing_view)

    def email_change(self, event):
        changing_view = ChangingView("email")
        self.window.show_view(changing_view)

    def bck(self, event):
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)

    def logout(self, event):
        vars.id = 0
        file = open("BattleSkies.redacc", mode="w", encoding="utf-8")
        print("unloginned", file=file)
        print(0, file=file)
        file.close()
        self.bck(event)
