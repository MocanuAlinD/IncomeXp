from kivy.uix.screenmanager import Screen
from kivymd.uix.snackbar import Snackbar
from kivy.properties import StringProperty, ObjectProperty, ListProperty
import datetime
import sqlite3
import os
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import ThreeLineListItem, ThreeLineAvatarIconListItem
from kivy.factory import Factory
from datetime import date, datetime
import uuid
from kivy.core.window import Window as w
import csv
import json
from kivy.utils import platform
import threading
from kivy.clock import Clock


class IncomeRVButton(Factory.ThreeLineAvatarIconListItem):

    def get_data_index(self):
        return self.parent.get_view_index_at(self.center)

    @property
    def rv(self):
        return self.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent

    # def on_release(self):
        # self.rv.editEntry(self.id)

    def editEntry(self):
        self.rv.editEntry(self.id)

    def deleteEntry(self):
        self.rv.itemId = self.id
        self.rv.deleteFromDB()


class IncomePage(Screen):
    listaToate = []
    intervalExportList = ListProperty([])
    newFileIntervalExport = StringProperty("")
    savePath = StringProperty("")
    rvViewIncome = ObjectProperty()
    rvSearchIncome = ObjectProperty()
    rvByIncome = ObjectProperty()
    dbPath = os.path.join(os.getcwd(), 'xpDb.db')
    itemId = StringProperty("")
    totalAvailable = StringProperty("")
    oldIncome = StringProperty("")
    resultsLabel = StringProperty("0")
    currentYear = str(date.today().year)
    currentMonth = str(date.today().month)
    currentDay = str(date.today().day)
    osPaths = {"macosx": "/Users/alin/Desktop",
               "win": "/", "android": "/storage/emulated/0"}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fileManager = MDFileManager(
            select_path=self.selectPath,
            exit_manager=self.exitManager)
        self.savePath = self.osPaths[platform]
        
    def asyncAllData(self):
        b=threading.Thread(target=self.clockAllData)
        b.start()
        b.join()
        # th = []
        # a=threading.Thread(target=self.spreadData,args=('desc',))
        # b=threading.Thread(target=self.getTotalAvailable)
        # th.append(a)
        # th.append(b)
        # for i in th:
        #     i.start()
        # for i in th:
        #     i.join()
            
    def clockAllData(self):
        Clock.schedule_once(lambda x: self.spreadData('desc'))
        Clock.schedule_once(lambda x: self.getTotalAvailable())
        
    def openFileManager(self):
        self.fileManager.show(self.osPaths[platform])
        
    def exitManager(self, *args):
        self.fileManager.close()

    def selectPath(self, pth):
        if os.path.isfile(pth):
            Snackbar(text="Cannot save file to file. Select a folder.").open()
        elif os.path.isdir(pth):
            self.savePath = pth
            self.fileManager.close()

    def clearPath(self):
        self.savePath = self.osPaths[platform]
        self.ids.fileName.text = ""

    def change_screens(self, screen):
        self.parent.current = screen

# ============================================================================

    def add_data(self, day, month, year, income, details, other):
        details = details.strip()
        other = other.strip()
        if not day or not month or not year:
            Snackbar(text="Invalid date.").open()
            return
        if not income:
            Snackbar(text="Income cannot be empty.").open()
            return
        if float(income) < 0:
            Snackbar(text="Income cannot be lower than '0'.").open()
            return
        if not details:
            Snackbar(text="Details cannot be empty.").open()
            return
        if not other:
            Snackbar(text="Description cannot be empty.").open()
            return
        day = int(day.strip())
        month = int(month.strip())
        year = int(year.strip())
        income = float(income.strip())

        try:
            date_string = f"{year}-{month}-{day}"
            formatDate = "%Y-%m-%d"
            datetime.strptime(date_string, formatDate).date()
            if day < 10:
                day = f"0{day}"
            if int(month) < 10:
                month = f"0{month}"

            self.saveToDB(day, month, year, income, details, other)

        except ValueError:
            Snackbar(text="Invalid date.").open()
            return

    def saveToDB(self, day, month, year, income, details, other):
        id = str(uuid.uuid1())
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        cur.execute("INSERT INTO income_table VALUES (:id, :dt, :income, :details, :other)",
                    {
                        "id": id,
                        'dt': f"{year}-{month}-{day}",
                        'income': income,
                        'details': details,
                        'other': other
                    })
        conn.commit()
        conn.close()
        Snackbar(text=f"Successfuly added to database.").open()
        # self.newTotalAfterAdd(income)
        # self.spreadData("desc")
        # self.ids.idincome.text = ''
        # self.ids.iddetails.text = ''
        # self.ids.iddescription.text = ''
        self.refreshChanges('add',income)

    # MERGE
    def saveFile(self, fileType):
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        cur.execute("SELECT * FROM income_table")
        all = cur.fetchall()
        for i in all:
            moc = {
                "id": i[0],
                "dt": i[1],
                "income": i[2],
                "details": i[3],
                "other": i[4],
                "db": "income"
            }
            self.listaToate.append(moc)
        conn.close()
        txt = self.ids.fileName.text

        if fileType == 'txt':
            txt = txt + ".txt"
            try:
                with open(os.path.join(self.savePath, txt), 'x') as f:
                    json.dump(self.listaToate, f)
                Snackbar(text=f"Saved in {self.savePath}/{txt}").open()
                self.listaToate = []
                return
            except:
                Snackbar(text=f"File {txt} already exists.").open()
                self.listaToate = []
                return

        if fileType == 'csv':
            txt = txt + ".csv"
            try:
                with open(os.path.join(self.savePath, txt), 'x', newline='') as f:
                    fieldnames = ['id', 'dt', 'income',
                                  'details', 'other', 'db']
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    for i in self.listaToate:
                        writer.writerow(i)
                Snackbar(text=f"Saved in {self.savePath}/{txt}").open()
                self.listaToate = []
                return
            except:
                Snackbar(text=f"File {txt} already exists.").open()
                self.listaToate = []
                return

    # MERGE
    def spreadData(self, *args):
        self.rvViewIncome.data = []
        temp = ''
        if args[0] == 'desc':
            temp = 'desc'
        elif args[0] == 'asc':
            temp = 'asc'
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        d = cur.execute('SELECT * FROM income_table ORDER BY dt ' + temp)
        all = d.fetchall()
        for i in all:
            self.rvViewIncome.data.append(
                {'text': f"{i[1]} - {i[2]}", 'secondary_text': f"{i[3]}", 'tertiary_text': f"{i[4]}", "id": str(i[0])})
        conn.close()
        self.getByYMD('month')

    # MERGE
    def deleteFromDB(self):
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        item = cur.execute("select income from income_table where id=?",(self.itemId,))
        tempIncome = item.fetchone()[0]
        cur.execute('DELETE FROM income_table WHERE id= ? ', (self.itemId,))
        conn.commit()
        conn.close()
        # self.newTotalAfterDelete(tempIncome)
        # self.emptyAddFields()
        # self.spreadData('desc')
        self.refreshChanges('delete',tempIncome)
        Snackbar(text="Item removed from database").open()
        
    def refreshChanges(self,*args):
        if args[0] == 'edit':
            self.newTotalAfterEdit(args[1])
            self.emptyEditFields()
        if args[0] == 'delete':
            self.newTotalAfterDelete(args[1])
            self.emptyEditFields()
        if args[0] == 'add':
            self.newTotalAfterAdd(args[1])
            self.ids.idincome.text = ''
            self.ids.iddetails.text = ''
            self.ids.iddescription.text = ''
        self.spreadData("desc")
        if self.ids.idSearch.text and self.rvSearchIncome.data != []:
            self.search()

    def editEntry(self, id):
        self.ids.tabsContainer.switch_tab("Edit")
        self.itemId = id
        conn = sqlite3.connect(os.path.join(os.getcwd(), self.dbPath))
        cur = conn.cursor()
        all = cur.execute(
            "SELECT * FROM income_table WHERE id = ?", (self.itemId,))
        oneItem = all.fetchone()
        allDate = oneItem[1].split('-')
        year = allDate[0]
        month = allDate[1]
        day = allDate[2]
        self.ids.editday.text = day
        self.ids.editmonth.text = month
        self.ids.edityear.text = year
        self.ids.editincome.text = str(oneItem[2])
        self.ids.editdetails.text = oneItem[3]
        self.ids.editdescription.text = oneItem[4]
        self.ids.editid.text = oneItem[0]
        conn.close()
        self.oldIncome = str(oneItem[2])

    def saveEditedEntry(self):
        details = self.ids.editdetails.text.strip()
        description = self.ids.editdescription.text.strip()
        if not self.ids.editday.text or not self.ids.editmonth.text or not self.ids.edityear.text:
            Snackbar(text="Invalid date.").open()
            return
        if not self.ids.editincome.text:
            Snackbar(text="Income cannot be empty. Minimum '0'.").open()
            return
        if float(self.ids.editincome.text) < 0:
            Snackbar(text="Income cannot be lower than '0'.").open()
            return
        if not self.ids.editdetails.text:
            Snackbar(text="Details cannot be empty.").open()
            return
        if not self.ids.editdescription.text:
            Snackbar(text="Description cannot be empty.").open()
            return
        day = int(self.ids.editday.text.strip())
        month = int(self.ids.editmonth.text.strip())
        year = int(self.ids.edityear.text.strip())
        income = float(self.ids.editincome.text.strip())

        try:
            date_string = f"{year}-{month}-{day}"
            formatDate = "%Y-%m-%d"
            datetime.strptime(date_string, formatDate).date()
            if day < 10:
                day = f"0{day}"
            if month < 10:
                month = f"0{month}"
            conn = sqlite3.connect(self.dbPath)
            cur = conn.cursor()
            cur.execute('''UPDATE income_table SET
                dt = ?,
                income = ?,
                details = ?,
                other = ?
                WHERE id=?''', (f"{year}-{month}-{day}", income, details, description, self.itemId,))
            conn.commit()
            conn.close()
            # self.newTotalAfterEdit(income)
            # self.emptyEditFields()
            # self.spreadData("desc")
            self.refreshChanges('edit', income)

        except ValueError:
            Snackbar(text="Invalid date.").open()
            return

    def emptyEditFields(self):
        self.ids.editday.text = ''
        self.ids.editmonth.text = ''
        self.ids.edityear.text = ''
        self.ids.editincome.text = ''
        self.ids.editdetails.text = ''
        self.ids.editdescription.text = ''
        self.ids.editid.text = ''
        self.itemId = ""

    def search(self):
        txt = self.ids.idSearch.text.strip().lower()
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        self.rvSearchIncome.data = []
        if txt == "":
            self.resultsLabel = "0"
            return
        else:
            d = c.execute(
                f"SELECT * FROM income_table where dt || income || details || other LIKE '%{txt}%' ")
            all = d.fetchall()
            self.resultsLabel = str(len(all))
            if len(all) == 0:
                Snackbar(text="Nothing found.").open()
            for i in reversed(all):
                self.rvSearchIncome.data.append(
                    {'text': f"{i[1]} - {i[2]}", 'secondary_text': f"{i[3]}", 'tertiary_text': f"{i[4]}", "id": str(i[0])})
        conn.close()

    def getByYMD(self, item):
        self.rvByIncome.data = []
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("select dt,income from income_table")
        all = d.fetchall()
        allyears = []
        allmonths = []
        alldays = []
        for i in all:
            year = datetime.strptime(i[0], "%Y-%m-%d").year
            month = datetime.strptime(i[0], "%Y-%m-%d").month
            day = datetime.strptime(i[0], "%Y-%m-%d").day

            if month < 10:
                month = f"0{month}"
            if day < 10:
                day = f"0{day}"

            yearmonth = f"{year}-{month}"
            yearmonthday = f"{year}-{month}-{day}"

            if year not in allyears:
                allyears.append(year)
            if yearmonth not in allmonths:
                allmonths.append(yearmonth)
            if yearmonthday not in alldays:
                alldays.append(yearmonthday)

        if item == 'year':
            for i in reversed(allyears):
                c.execute(
                    f"select dt, sum(income) from income_table where dt like '{i}%' ")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(
                        i, j[1])
                    self.rvByIncome.data.append({"text": tmp})
        if item == "month":
            for i in reversed(allmonths):
                c.execute(
                    f"select sum(income) from income_table where dt like '{i}%'")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(
                        i, j[0])
                    self.rvByIncome.data.append({"text": tmp})
        if item == 'day':
            for i in reversed(alldays):
                c.execute(
                    f"select sum(income) from income_table where dt like '{i}%'")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(
                        i, j[0])
                    self.rvByIncome.data.append({"text": tmp})

        conn.close()

    def calculateInterval(self):
        self.intervalExportList = []
        yearFrom = self.ids.yearFromInterval.text
        monthFrom = self.ids.monthFromInterval.text
        dayFrom = self.ids.dayFromInterval.text
        yearTo = self.ids.yearToInterval.text
        monthTo = self.ids.monthToInterval.text
        dayTo = self.ids.dayToInterval.text
        fromDate = f"{yearFrom}-{monthFrom}-{dayFrom}"
        toDate = f"{yearTo}-{monthTo}-{dayTo}"
        try:
            datetime.strptime(fromDate, "%Y-%m-%d").date()
        except ValueError:
            self.ids.totalLabel.text = 'Invalid FROM date format.'
            # Snackbar(text="Invalid FROM date format.",font_size="12sp").open()
            return

        try:
            datetime.strptime(toDate, "%Y-%m-%d").date()
        except ValueError:
            self.ids.totalLabel.text = 'Invalid TO date format.'
            # Snackbar(text="Invalid TO date format.",font_size="12sp").open()
            return

        fromDate = datetime.strptime(fromDate, "%Y-%m-%d").date()
        toDate = datetime.strptime(toDate, "%Y-%m-%d").date()
        if fromDate > toDate:
            Snackbar(text='FROM date cannot be greater than TO date.',
                     font_size="12sp").open()
            return

        self.newFileIntervalExport = f"intervalExport-{dayFrom}-{monthFrom}-{yearFrom}_{dayTo}-{monthTo}-{yearTo}.csv"
        self.intervalToList(fromDate, toDate)

        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute(
            f"select sum(income) from income_table where dt >='{fromDate}' and dt <='{toDate}'")
        try:
            all = d.fetchall()
            total = "{:.2f}".format(all[0][0])
            self.ids.totalLabel.text = f"Total:     {total}"
        except:
            Snackbar(text="DB is empty.").open()
            return
        finally:
            conn.close()

    def intervalToList(self, fromDate, toDate):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute(
            f"select * from income_table where dt >='{fromDate}' and dt <='{toDate}' order by dt desc")
        all = d.fetchall()
        for i in all:
            tmp = {
                "id": i[0],
                "dt": i[1],
                "income": i[2],
                "details": i[3],
                "other": i[4],
                "db": "income"
            }
            self.intervalExportList.append(tmp)
        conn.close()

    def exportIntervalToFile(self):
        try:
            with open(os.path.join(self.savePath, self.newFileIntervalExport), 'x') as f:
                fieldnames = ['id', 'dt', 'income', 'details', 'other', 'db']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                for i in self.intervalExportList:
                    writer.writerow(i)
            self.intervalExportList = []
            return
        except:
            os.remove(os.path.join(self.savePath, self.newFileIntervalExport))
            self.exportIntervalToFile()
            Snackbar(text="File exists.Deleted and created new one.").open()
            return

    def getTotalAvailable(self):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("select total from total_money where id='1' ")
        all = d.fetchall()[0][0]
        self.totalAvailable = all
        conn.close()
        

    def newTotalAfterDelete(self, income):
        income = float(income)
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("SELECT total FROM total_money")
        all = float(d.fetchall()[0][0])
        newTotal = all - (income)
        c.execute("update total_money set total=? where id='1'",
                  (str(newTotal),))
        conn.commit()
        conn.close()
        self.totalAvailable = str(newTotal)


    def newTotalAfterAdd(self, income):
        income = float(income)
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("SELECT total FROM total_money")
        all = float(d.fetchall()[0][0])
        newTotal = all + (income)
        c.execute("update total_money set total=? where id='1'",
                  (str(newTotal),))
        conn.commit()
        self.totalAvailable = str(newTotal)
        conn.close()

    def newTotalAfterEdit(self, newCash):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        newTotal = (float(self.totalAvailable) -
                    float(self.oldIncome)) + float(newCash)
        c.execute("update total_money set total=? where id='1'",
                  (str(newTotal),))
        conn.commit()
        conn.close()
        self.totalAvailable = str(newTotal)
        self.oldIncome = ""
