from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from expensesPage import ExpensesPage
from settingsPage import SettingsPage
from incomePage import IncomePage

class MainPage(Screen):
    # pass
    
    # def on_enter(self):
    #     self.parent.add_widget(ExpensesPage(name="expensesPage"))
    #     self.parent.add_widget(SettingsPage(name="settingsPage"))
    #     self.parent.add_widget(IncomePage(name="incomePage"))
    
    def change_screens(self,screen):
        file = f"kvFiles/{screen}.kv"
        Builder.unload_file(file)
        Builder.load_file(file)
        if self.parent.has_screen(screen):
            self.parent.current = screen
        else:
            if screen == 'expensesPage':
                self.parent.add_widget(ExpensesPage(name=screen))
                self.parent.current = screen
            if screen == 'incomePage':
                self.parent.add_widget(IncomePage(name=screen))
                self.parent.current = screen
            if screen == 'settingsPage':
                self.parent.add_widget(SettingsPage(name=screen))
                self.parent.current = screen