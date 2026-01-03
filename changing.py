import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout


class ChangingView(arcade.View):
    def __init__(self, changer):
        super().__init__()
        self.changer = changer
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
        label = UILabel(text="Изменение ", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        if self.changer == "password":
            label.text += "пароля"
        if self.changer == "nickname":
            label.text += "псевдонима"
        if self.changer == "email":
            label.text += "почты"
        self.box_layout.add(label)
        self.password_layout = UIBoxLayout(vertical=False, space_between=5)
        password_label = UILabel(text="Пароль:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        if self.changer == "password":
            password_label.text = "Старый пароль:"
        self.password = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.password_layout.add(password_label)
        self.password_layout.add(self.password)
        self.box_layout.add(self.password_layout)

        self.new_layout = UIBoxLayout(vertical=False, space_between=5)
        new_label = UILabel(text="Новый ", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        if self.changer == "password":
            new_label.text += "пароль:"
        if self.changer == "nickname":
            new_label.text += "псевдоним:"
        if self.changer == "email":
            new_label.text += "email:"
        self.new_field = UIInputText(x=0, y=0, width=400, height=40, text="",
                                    text_color=arcade.color.BLACK, password_label=True)
        self.new_layout.add(new_label)
        self.new_layout.add(self.new_field)
        self.box_layout.add(self.new_layout)
        self.confirm_layout = UIBoxLayout(vertical=False, space_between=5)
        confirm_label = UILabel(text="Ещё раз:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.confirm = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.confirm_layout.add(confirm_label)
        self.confirm_layout.add(self.confirm)
        if self.changer == "password":
            self.box_layout.add(self.confirm_layout)
        lgn = UIFlatButton(text="Изменить", width=400, height=40)
        lgn.on_click = self.go
        self.box_layout.add(lgn)
        clr = UIFlatButton(text="Очистить", width=400, height=40)
        clr.on_click = self.clr
        self.box_layout.add(clr)
        bck = UIFlatButton(text="Назад", width=400, height=40)
        bck.on_click = self.bck
        self.box_layout.add(bck)
        self.err_label = UILabel(text="", font_size=15, text_color=arcade.color.RED, width=300, align="center")
        self.box_layout.add(self.err_label)

    def go(self, event):
        try:
            cur = vars.con.cursor()
            right_old = cur.execute(f"SELECT `password` FROM `users` WHERE `id` = '{vars.id}'").fetchall()[0][0]
            old = self.password.text
            if old != right_old and self.changer != "password":
                self.err_label.text = "Пароль введён неверно"
                return
            if old != right_old and self.changer == "password":
                self.err_label.text = "Старый пароль введён неверно"
                return
            new = self.new_field.text
            if self.changer == "password":
                confirm = self.confirm.text
                if confirm != new:
                    self.err_label.text = "Новые пароли не совпадают"
                    return
            if self.changer == "email" and ('@' not in new or '.' not in new):
                self.err_label.text = "E-mail введён неверно"
                return
            cur.execute(f"UPDATE `users` SET `{self.changer}` = '{new}' WHERE `id` = '{vars.id}'")
            vars.con.commit()
            self.bck(event)
        except Exception:
            self.err_label.text = "Произошла ошибка, попробуйте позднее"

    def clr(self, event):
        self.password.text = ""
        self.new_field.text = ""
        self.confirm.text = ""

    def bck(self, event):
        from settings import SettingsView
        settings_view = SettingsView()
        self.window.show_view(settings_view)
