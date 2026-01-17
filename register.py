import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout

from login import LoginView


class RegisterView(arcade.View):
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
        label = UILabel(text="Регистрация", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)
        self.nick_layout = UIBoxLayout(vertical=False, space_between=5)
        nick_label = UILabel(text="Псевдоним:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.nick = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.nick_layout.add(nick_label)
        self.nick_layout.add(self.nick)
        self.box_layout.add(self.nick_layout)
        self.name_layout = UIBoxLayout(vertical=False, space_between=5)
        name_label = UILabel(text="Имя:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.name = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.name_layout.add(name_label)
        self.name_layout.add(self.name)
        self.box_layout.add(self.name_layout)
        self.email_layout = UIBoxLayout(vertical=False, space_between=5)
        email_label = UILabel(text="E-mail:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.email = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.email_layout.add(email_label)
        self.email_layout.add(self.email)
        self.box_layout.add(self.email_layout)
        self.login_layout = UIBoxLayout(vertical=False, space_between=5)
        login_label = UILabel(text="Логин:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.login = UIInputText(x=0, y=0, width=400, height=40, text="", text_color=arcade.color.BLACK)
        self.login_layout.add(login_label)
        self.login_layout.add(self.login)
        self.box_layout.add(self.login_layout)
        self.password_layout = UIBoxLayout(vertical=False, space_between=5)
        password_label = UILabel(text="Пароль:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.password = UIInputText(x=0, y=0, width=400, height=40, text="",
                                    text_color=arcade.color.BLACK, password_label=True)
        self.password_layout.add(password_label)
        self.password_layout.add(self.password)
        self.box_layout.add(self.password_layout)
        self.confirm_layout = UIBoxLayout(vertical=False, space_between=5)
        confirm_label = UILabel(text="Ещё раз:", font_size=15, text_color=arcade.color.BLACK, width=100, align="right")
        self.confirm = UIInputText(x=0, y=0, width=400, height=40, text="",
                                    text_color=arcade.color.BLACK, password_label=True)
        self.confirm_layout.add(confirm_label)
        self.confirm_layout.add(self.confirm)
        self.box_layout.add(self.confirm_layout)
        lgn = UIFlatButton(text="Зарегестрироваться", width=400, height=40)
        lgn.on_click = self.go
        self.box_layout.add(lgn)
        rgs = UIFlatButton(text="Окно входа в аккаунт", width=400, height=40)
        rgs.on_click = self.another
        self.box_layout.add(rgs)
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
            login = self.login.text
            lgns = cur.execute( f"SELECT * FROM `users` WHERE `login` = '{login}'").fetchall()
            password = self.password.text
            confirm = self.confirm.text
            name = self.name.text
            nickname = self.nick.text
            email = self.email.text
            if len(login) * len(password) * len(confirm) * len(name) * len(nickname) * len(email) == 0:
                self.err_label.text = "Не все поля заполнены"
            elif len(lgns) > 0:
                self.err_label.text = "Данный логин уже занят"
            elif len(password) < 8:
                self.err_label.text = "Пароль слишком короткий"
            elif password != confirm:
                self.err_label.text = "Пароли не совпадают"
            elif '@' not in email or '.' not in email:
                self.err_label.text = "E-mail введён неверно"
            else:
                s = "INSERT INTO `users` (`name`, `nickname`, `login`, `password`, `email`"
                cur.execute(s + f") VALUES ('{name}', '{nickname}', '{login}', '{password}', '{email}')")
                vars.con.commit()
                vars.id = cur.execute(f"SELECT `id` FROM `users` WHERE `login` = '{login}'").fetchall()[0][0]
                vars.save_id()
                self.bck(event)
        except Exception:
            self.err_label.text = "Произошла ошибка, попробуйте позднее"

    def another(self, event):
        login_view = LoginView()  # Передаём текущий вид, чтобы вернуться
        self.window.show_view(login_view)

    def clr(self, event):
        self.login.text = ""
        self.password.text = ""
        self.nick.text = ""
        self.name.text = ""
        self.email.text = ""

    def bck(self, event):
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)

    def on_hide_view(self):
        self.manager.clear()
