import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UIInputText
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout


class LoginView(arcade.View):
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
        label = UILabel(text="Вход в аккаунт", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)
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
        lgn = UIFlatButton(text="Войти", width=400, height=40)
        lgn.on_click = self.go
        self.box_layout.add(lgn)
        rgs = UIFlatButton(text="Окно регистрации", width=400, height=40)
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
            login = self.login.text
            password = self.password.text
            cur = vars.con.cursor()
            result = cur.execute(
                f"SELECT * FROM `users` WHERE `login` == '{login}' AND `password` == '{password}'").fetchall()
            if len(result) > 0:
                vars.id = result[0][0]
                vars.save_id()
                self.bck(event)
            else:
                self.err_label.text = "Логин или пароль введены неверно"
        except Exception:
            self.err_label.text = "Произошла ошибка, попробуйте позднее"

    def another(self, event):
        from register import RegisterView
        register_view = RegisterView()  # Передаём текущий вид, чтобы вернуться
        self.window.show_view(register_view)

    def clr(self, event):
        self.login.text = ""
        self.password.text = ""

    def bck(self, event):
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)
