import vars
import arcade


from arcade.gui import UIManager, UIFlatButton, UILabel, UIInputText, UIMessageBox
from arcade.gui.widgets.layout import UIAnchorLayout, UIBoxLayout
from creating import CreatingView
from lobby_pve import LobbyPveView
from lobby_pvp import LobbyPvpView


class HubView(arcade.View):
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
        self.time = -1

    def on_update(self, delta_time):
        if self.time == -1:
            self.time = 0
        else:
            self.time = (self.time + delta_time) % 60
        if self.time == 0:
            self.list_games.clear()
            cur = vars.con.cursor()
            result = cur.execute("SELECT * FROM `games` WHERE `private` = 0").fetchall()
            for game in result:
                try:
                    lyt = UIBoxLayout(vertical=False, space_between=5)
                    nick = cur.execute(f"SELECT `nickname` FROM `users` WHERE `id` = '{game[3]}'").fetchall()[0][0]
                    code = game[5]
                    maxi = game[2]
                    mp = "Пустыня"
                    if game[1] == 2:
                        mp = "Горы"
                    if game[1] == 3:
                        mp = "Город"
                    lt = 'E'
                    if game[4] == 1:
                        lt = 'P'
                        maxi *= 2
                    txt = f'[{code}] Лобби {nick}, PV{lt} карта "{mp}", игроков: 0/{maxi}.'
                    btn = UIFlatButton(text=txt, font_size=15,
                                       text_color=arcade.color.BLACK, align="right", width=600, height=40)
                    btn.on_click = lambda x, c=code: self.join(x, c)
                    lyt.add(btn)
                    self.list_games.add(lyt)
                except Exception:
                    pass

    def on_draw(self):
        """Отрисовка начального экрана"""
        self.clear()
        self.manager.draw()

    def setup_widgets(self):
        label = UILabel(text="Сетевая игра", font_size=30, text_color=arcade.color.BLACK, width=300, align="center")
        self.box_layout.add(label)
        self.list_games = UIBoxLayout(vertical=True, space_between=7)
        self.box_layout.add(self.list_games)
        lyt = UIBoxLayout(vertical=False, space_between=5)
        lbl = UILabel(text="Код:", font_size=15, text_color=arcade.color.RED, align="center")
        lyt.add(lbl)
        self.field = UIInputText(x=0, y=0, width=(185 - lbl.width), height=40, text="", text_color=arcade.color.BLACK)
        lyt.add(self.field)
        join = UIFlatButton(text="Присоединиться", width=200, height=40)
        f = lambda x: self.join(x, self.field.text)
        join.on_click = f
        lyt.add(join)
        create = UIFlatButton(text="Создать", width=200, height=40)
        create.on_click = self.create
        lyt.add(create)
        self.box_layout.add(lyt)
        bck = UIFlatButton(text="Назад", width=600, height=40)
        bck.on_click = self.bck
        self.box_layout.add(bck)
        self.err_label = UILabel(text="", font_size=15, text_color=arcade.color.RED, width=300, align="center")
        self.box_layout.add(self.err_label)

    def join(self, event, code):
        try:
            cur = vars.con.cursor()
            reses = cur.execute(f"SELECT * FROM `games` WHERE `code` = '{code}'").fetchall()
            game = reses[0][0]
            maxi = reses[0][2]
            mode = reses[0][4]
            if mode == 1:
                maxi *= 2
            pls = len(cur.execute(f"SELECT * FROM `session` WHERE `game` = {game}").fetchall())
            if pls >= maxi:
                self.err_label.text = "Данный сервер переполнен"
            else:
                if mode:
                    a = len(cur.execute(f"SELECT * FROM `session` WHERE `game` = {game} AND `team` = 0").fetchall())
                    b = len(cur.execute(f"SELECT * FROM `session` WHERE `game` = {game} AND `team` = 1").fetchall())
                    lst = [a < maxi // 2, b < maxi // 2]
                    self.sel = -1
                    if lst[0] and lst[1]:
                        message_box = UIMessageBox(
                            width=300, height=200,
                            message_text="Выберите команду",
                            buttons=("Синие", "Красные")
                        )
                        f = lambda a, g=game: self.selec(a, g)
                        message_box.on_action = f
                        self.manager.add(message_box)
                    else:
                        self.sel = int(lst[1])
                        cur.execute("INSERT INTO `session` (`player`, `game`, `plane`, `team`"
                                    + f") VALUES ({vars.id}, {game}, {vars.plane}, {self.sel})")
                        lobby_view = LobbyPvpView(False, game)
                        vars.con.commit()
                        self.window.show_view(lobby_view)
                else:
                    cur.execute(f"INSERT INTO `session` (`player`, `game`, `plane`) VALUES ({vars.id}, {game}, {vars.plane})")
                    lobby_view = LobbyPveView(False, game)
                    vars.con.commit()
                    self.window.show_view(lobby_view)
        except Exception:
            self.err_label.text = "Лобби не найдено"

    def create(self, event):
        creating_view = CreatingView(self.field.text)
        self.window.show_view(creating_view)

    def bck(self, event):
        from start import StartView
        start_view = StartView()
        self.window.show_view(start_view)

    def selec(self, text, game):
        if text.action == "Синие":
            self.sel = 0
        else:
            self.sel = 1
        cur = vars.con.cursor()
        cur.execute("INSERT INTO `session` (`player`, `game`, `plane`, `team`"
                    + f") VALUES ({vars.id}, {game}, {vars.plane}, {self.sel})")
        lobby_view = LobbyPvpView(False, game)
        vars.con.commit()
        self.window.show_view(lobby_view)

    def on_hide_view(self):
        self.manager.clear()
