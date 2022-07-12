from mainPage import MainPage
from kivy.core.window import Window as w
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy import utils
from kivy.utils import platform
import sqlite3


KV="""
#: import FadeTransition kivy.uix.screenmanager.FadeTransition
ScreenManager:
    id: sm
    transition: FadeTransition()
    MainPage:
        name: 'mainpage'
"""


if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
    
class Main(MDApp):
    pad = "10dp"
    
    def build(self):
        self.colorBg = utils.get_color_from_hex("#004E64")
        self.bg_color = utils.get_color_from_hex("#006494")
        self.fg_color = utils.get_color_from_hex("#247ba0")
        self.login_bg = utils.get_color_from_hex("#1b98e0")
        self.green_bg = utils.get_color_from_hex("#1D353F")
        self.green_fg = utils.get_color_from_hex("#2a9d8f")
        self.green = utils.get_color_from_hex("#7AE582")
        self.check_active_color = utils.get_color_from_hex('#457F96')
        self.white = utils.get_color_from_hex('#e8f1f2')
        self.orange = utils.get_color_from_hex('#e76f51')
        w.softinput_mode = 'below_target'
        if platform != "android":
            w.size = (360, 740)
            w.top = 50
            w.left = 0
        Builder.load_file('kvFiles/mainPage.kv')
        Builder.load_file('kvFiles/appKv.kv')
        screen = Builder.load_string(KV)
        return screen
    
    # COMING SOON
    # def create_db(self):
    #     conn = sqlite3.connect("xpDb.db")
    #     c = conn.cursor()
    #     c.execute("CREATE TABLE IF NOT EXISTS income_table ")

if __name__ == '__main__':
    Main().run()
