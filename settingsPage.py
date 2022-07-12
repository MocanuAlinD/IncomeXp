from kivy.uix.screenmanager import Screen
from kivy.core.window import Window as w
from kivy.properties import StringProperty,ListProperty,BooleanProperty
import sqlite3
from kivymd.uix.filemanager import MDFileManager
import os
from kivymd.uix.snackbar import Snackbar
import json
import csv
from kivy.utils import platform
import threading
from kivy.clock import Clock


class SettingsPage(Screen):
    oldTotal = StringProperty("")
    filePathIncome = StringProperty("")
    filePathExpenses = StringProperty("")
    demoTextIncome = StringProperty("Demo text")
    demoTextExpenses = StringProperty("Demo text")
    tempListIncome = ListProperty([])
    tempListExpenses = ListProperty([])
    dbPath = os.path.join(os.getcwd(), 'xpDb.db')
    loadingIncome = BooleanProperty(True)
    loadingExpenses = BooleanProperty(True)
    osPaths = {"macosx": "/Users/alin/Desktop",
               "win": "/", "android": "/storage/emulated/0"}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fileManagerIncome = MDFileManager(
            select_path=self.selectPathIncome,
            exit_manager=self.exit_managerIncome,
            preview=False)
        self.fileManagerExpenses = MDFileManager(
            select_path=self.selectPathExpenses,
            exit_manager=self.exit_managerExpenses,
            preview=False)
        
    def exit_managerIncome(self,*args):
        self.fileManagerIncome.close()
    
    def exit_managerExpenses(self,*args):
        self.fileManagerExpenses.close()

    def openFileManagerIncome(self):
        self.fileManagerIncome.show(self.osPaths[platform])
        
    def openFileManagerExpenses(self):
        self.fileManagerExpenses.show(self.osPaths[platform])
        
        
    # PATH INCOME
    def selectPathIncome(self, pth):
        self.loadingIncome = True
        self.demoTextIncome = 'demo text'
        self.tempListIncome = []
        if os.path.isfile(pth):
            if pth.endswith(".txt"):
                self.filePathIncome = pth
                self.exit_managerIncome()
                self.getFromIncomeNewTextFile()
            if pth.endswith(".csv"):
                self.filePathIncome = pth
                self.exit_managerIncome()
                self.getFromIncomeNewCsvFile()
        elif os.path.isdir(pth):
            Snackbar(text="Cannot open a folder.Select a txt file").open()
            return
        
    # PATH EXPENSES
    def selectPathExpenses(self, pth):
        self.loadingExpenses = True
        self.demoTextExpenses = 'demo text'
        self.tempListExpenses = []
        if os.path.isfile(pth):
            if pth.endswith(".txt"):
                self.filePathExpenses = pth
                self.exit_managerExpenses()
                self.getFromExpensesNewTextFile()
            if pth.endswith(".csv"):
                self.filePathExpenses = pth
                self.exit_managerExpenses()
                self.getFromExpensesNewCsvFile()
        elif os.path.isdir(pth):
            Snackbar(text="Cannot open a folder.Select a txt file").open()
            return

    # INCOME TEXT FROM FILE
    def getFromIncomeNewTextFile(self):
        with open(self.filePathIncome, 'r') as f:
            readedData = f.read()
            try:
                toList = json.loads(readedData)
                if not len(toList):
                    return
                x = toList[-1]
                if 'income' == x['db']:
                    tmp = f"Date: {x['dt']}\nIncome: {x['income']}\nDetails: {x['details']}\nDescription: {x['other']}"
                    self.demoTextIncome = tmp
                    self.tempListIncome = toList
                    self.loadingIncome = False
                else:
                    Snackbar(text="Wrong file format.").open()
                    return
            except:
                Snackbar(text='Something went wrong.').open()
                return
            
    
    # EXPENSES TEXT FROM FILE
    def getFromExpensesNewTextFile(self):
        with open(self.filePathExpenses, 'r') as f:
            readedData = f.read()
            try:
                toList = json.loads(readedData)
                if not len(toList):
                    return
                x = toList[-1]
                if 'expenses' == x['db']:
                    tmp = f"Date: {x['dt']}\nAmount: {x['amount']}\nProduct: {x['product']}\nCategory: {x['category']}"
                    self.demoTextExpenses = tmp
                    self.tempListExpenses = toList
                    self.loadingExpenses = False
                else:
                    Snackbar(text="Wrong file format.").open()
                    return
            except:
                Snackbar(text='Something went wrong.').open()
                return
    
    # INCOME CSV FROM FILE
    def getFromIncomeNewCsvFile(self):
        with open(self.filePathIncome, 'r') as f:
            allData = csv.DictReader(f)
            for i in allData:
                if i['db'] == 'income':
                    tmp = {
                        'id': i['id'],
                        'dt': i['dt'],
                        'income': float(i['income']),
                        'details': i['details'],
                        'other': i['other']
                    }
                    self.tempListIncome.append(tmp)
        if not len(self.tempListIncome):
            return
        self.loadingIncome = False
        x = self.tempListIncome[-1]
        self.demoTextIncome = f"Date: {x['dt']}\nIncome: {x['income']}\nDetails: {x['details']}\nDescription: {x['other']}"
    
    # EXPENSES CSV FROM FILE
    def getFromExpensesNewCsvFile(self):
        with open(self.filePathExpenses, 'r') as f:
            allData = csv.DictReader(f)
            for i in allData:
                if i['db'] == 'expenses':
                    tmp = {
                        'id': i['id'],
                        'dt': i['dt'],
                        'amount': i['amount'],
                        'product': i['product'],
                        'category': i['category']
                    }
                    self.tempListExpenses.append(tmp)
        if not len(self.tempListExpenses):
            return
        self.loadingExpenses = False
        x = self.tempListExpenses[-1]
        self.demoTextExpenses = f"Date: {x['dt']}\nAmount: {x['amount']}\nProduct: {x['product']}\nCategory: {x['category']}"
    
    def asyncaddIncome(self):
        self.loadingIncome = True
        a=threading.Thread(target=self.clockaddIncome)
        a.daemon = True
        a.start()
        
    def clockaddIncome(self):
        Clock.schedule_once(self.fromFileToIncomeDb())
    
    
    # INCOME TO DB
    def fromFileToIncomeDb(self):
        self.ids.importIncomeBtn.disabled = True
        self.ids.importExpensesBtn.disabled = True
        self.ids.btnDeleteIncomeDB.disabled = True
        self.ids.btnDeleteExpensesDB.disabled = True
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        self.clearIncomeTable()
        ind = len(self.tempListIncome)
        for i in self.tempListIncome:
            c.execute("INSERT INTO income_table VALUES (:id, :dt, :income, :details, :other)",
            {
            "id": i['id'],
            'dt': i['dt'],
            'income': i['income'],
            'details': i['details'],
            'other': i['other']
            })
            conn.commit()
            ind -= 1
            self.demoTextIncome = f"Remaining: {ind}"
        conn.close()
        Snackbar(text="Income DB updated.").open()
        self.tempListIncome = []
        self.ids.importIncomeBtn.disabled = False
        self.ids.importExpensesBtn.disabled = False
        self.ids.btnDeleteIncomeDB.disabled = False
        self.ids.btnDeleteExpensesDB.disabled = False
        
    def asyncaddExpenses(self):
        self.loadingExpenses = True
        b=threading.Thread(target=self.clockaddExpenses)
        b.daemon = True
        b.start()
        
    def clockaddExpenses(self):
        Clock.schedule_once(self.fromFileToExpensesDb())
        
    # EXPENSES TO DB
    def fromFileToExpensesDb(self):
        self.ids.importExpensesBtn.disabled = True
        self.ids.importIncomeBtn.disabled = True
        self.ids.btnDeleteIncomeDB.disabled = True
        self.ids.btnDeleteExpensesDB.disabled = True
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        self.clearExpensesTable()
        ind = len(self.tempListExpenses)
        for i in self.tempListExpenses:
            ind -= 1
            self.demoTextExpenses = f"Remaining: {ind}"
            c.execute("INSERT INTO exp_table VALUES (:id, :dt, :amount, :product, :category)",
            {
            'id': i['id'],
            'dt': i['dt'],
            'amount': i['amount'],
            'product': i['product'],
            'category': i['category']
            })
            conn.commit()
        conn.close()
        Snackbar(text="Expenses DB updated.").open()
        self.tempListExpenses = []
        self.ids.importExpensesBtn.disabled = False
        self.ids.importIncomeBtn.disabled = False
        self.ids.btnDeleteIncomeDB.disabled = False
        self.ids.btnDeleteExpensesDB.disabled = False
        
    def change_screens(self, screen):
        self.parent.current = screen
        
    def getOldTotal(self):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("select * from total_money where id=='1'")
        all = d.fetchall()[0][1]
        self.oldTotal = str(all)
        conn.close()
        
    def newTotal(self):
        newTotal = float(self.ids.idOldTotal.text)
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        c.execute("update total_money set total = ? where id == '1'", (str(newTotal),))
        conn.commit()
        conn.close()
        self.ids.idOldTotal.hint_text = f"before {newTotal} lei"
        self.ids.idOldTotal.text = ''
        
    def clearIncomeTable(self):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        c.execute("delete from income_table")
        conn.commit()
        conn.close()
        
    def clearExpensesTable(self):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        c.execute("delete from exp_table")
        conn.commit()
        conn.close()


    # def showTable(self, item):
    #     conn = sqlite3.connect(self.dbPath)
    #     c=conn.cursor()
    #     d=c.execute("select * from "+ item)
    #     all = d.fetchall()
    #     print(len(all))
    #     for i in all:
    #         print(i[1], i[2])
    #     print(len(all))
    #     conn.close()
        
    # def showTotal(self):
    #     conn = sqlite3.connect(self.dbPath)
    #     c=conn.cursor()
    #     d=c.execute("select * from total_money")
    #     all = d.fetchall()[0][1]
    #     print(all)
    #     conn.close()
    
    # def showTotal(self):
    #     conn = sqlite3.connect(self.dbPath)
    #     c=conn.cursor()
    #     c.execute("SELECT * FROM sqlite_master WHERE type = 'table'")
    #     print(c.fetchall())
    #     # d=c.execute("select * from total_money")
    #     # all = d.fetchall()[0][1]
    #     # print(all)
    #     conn.close()