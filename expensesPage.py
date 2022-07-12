from kivy.uix.screenmanager import Screen
from kivymd.uix.snackbar import Snackbar
from kivy.properties import StringProperty, ObjectProperty, ListProperty
import datetime
import sqlite3
import os
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.list import ThreeLineAvatarIconListItem
from kivy.factory import Factory
from datetime import date,datetime
import uuid
from kivy.core.window import Window as w
import csv
import json
from kivy.utils import platform
import threading
from kivy.clock import Clock

class RVButton(Factory.ThreeLineAvatarIconListItem):
    
    def get_data_index(self):
        return self.parent.get_view_index_at(self.center)

    @property
    def rv(self):
        return self.parent.parent.parent.parent.parent.parent.parent.parent.parent.parent
        
    def editEntry(self):
        self.rv.editEntry(self.id)
    
    def deleteEntry(self):
        self.rv.itemId = self.id
        self.rv.deleteFromDB()
        

class ExpensesPage(Screen):
    rvView = ObjectProperty()
    rvSearch=ObjectProperty()
    rvBy = ObjectProperty()
    dbPath = os.path.join(os.getcwd(), 'xpDb.db')
    newFileIntervalExport = StringProperty("")
    intervalExportList = ListProperty([])
    productType = StringProperty('Stuff')
    editProductType = StringProperty("Stuff")
    listaToate = []
    resultsLabel = StringProperty("0")

    savePath = StringProperty("")
    itemId=StringProperty("")
    totalToSpend=StringProperty("")
    oldCash=StringProperty("")
    currentDay = str(date.today().day)
    currentMonth = str(date.today().month)
    currentYear = str(date.today().year)
    osPaths = {"macosx": "/Users/alin/Desktop",
               "win": "/", "android": "/storage/emulated/0"}
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fileManager = MDFileManager(
            select_path=self.selectPath, 
            exit_manager=self.exit_manager,
            preview=False)
        self.savePath = self.osPaths[platform]
        
    def asyncAllData(self):
        b=threading.Thread(target=self.clockAddData)
        b.start()
        b.join()
        # th = []
        # a=threading.Thread(target=self.spreadData,args=('desc',))
        # b=threading.Thread(target=self.getTotalToSpend)
        # th.append(a)
        # th.append(b)
        # for i in th:
        #     i.start()
        # for i in th:
        #     i.join()
        
        
    def clockAddData(self):
        Clock.schedule_once(lambda x: self.spreadData("desc"))
        Clock.schedule_once(lambda x: self.getTotalToSpend())
        
    def exit_manager(self, *args):
        self.fileManager.close()

    def openFileManager(self):
        self.fileManager.show(self.osPaths[platform])

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

    def check_active(self, val, checkbox, value):
        self.productType = val
        
    def check_active_edit(self, val, checkbox, value):
        self.editProductType = val
        
# ============================================================================


    def add_data(self, day, month, year, cash, product):
        product = product.strip()
        if not day or not month or not year:
            Snackbar(text="Invalid date.").open()
            return
        if not cash:
            Snackbar(text="Cash cannot be empty.").open()
            return
        if float(cash) < 0:
            Snackbar(text="Cash cannot be lower than '0'.").open()
            return
        if not product:
            Snackbar(text="Product cannot be empty.").open()
            return
        day = int(day.strip())
        month = int(month.strip())
        year = int(year.strip())
        cash = float(cash.strip())
        try:
            date_string = f"{year}-{month}-{day}"
            formatDate = "%Y-%m-%d"
            datetime.strptime(date_string, formatDate).date()
            if day < 10:
                day = f"0{day}"
            if int(month) < 10:
                month = f"0{month}"
            self.saveToDB(day, month, year, cash, product)
        except ValueError:
            Snackbar(text="Invalid date.").open()
            return
    
    
    def saveToDB(self,day,month,year,cash,product):
        id = str(uuid.uuid1())
        conn=sqlite3.connect(self.dbPath)
        cur=conn.cursor()
        cur.execute("INSERT INTO exp_table VALUES (:id, :dt, :amount, :product, :category)",
            {
            "id": id,
            'dt': f"{year}-{month}-{day}",
            'amount': cash,
            'product': product,
            'category': self.productType
            })
        conn.commit()
        conn.close()
        Snackbar(text=f"Successfuly added to database.").open()
        self.refreshChanges('add', cash)

    def saveFile(self, fileType):
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        cur.execute("SELECT * FROM exp_table")
        all = cur.fetchall()
        for i in all:
            moc = {
                "id": i[0],
                "dt": i[1],
                "amount": i[2],
                "product": i[3],
                "category": i[4],
                "db": "expenses"
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
                    fieldnames = ['id','dt','amount','product','category','db']
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


    def spreadData(self,*args):
        temp = ''
        if args and args[0] == 'desc':
            temp = 'desc'
        elif args and args[0] == 'asc':
            temp = 'asc'
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        cur.execute('SELECT * FROM exp_table ORDER BY dt ' + temp)
        all = cur.fetchall()
        conn.close()
        self.rvView.data = []
        for i in all:
            self.rvView.data.append({'text': f"{i[1]}", 'secondary_text': f"{i[2]} - {i[3]}", 'tertiary_text': f"{i[4]}", "id": str(i[0])})
        self.getByYMD('month')


    def deleteFromDB(self):
        conn=sqlite3.connect(self.dbPath)
        cur=conn.cursor()
        item = cur.execute("select amount from exp_table where id=?",(self.itemId,))
        tempIncome = item.fetchone()[0]
        cur.execute('DELETE FROM exp_table WHERE id= ? ', (self.itemId,))
        conn.commit()
        conn.close()
        self.refreshChanges('delete', tempIncome)
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
            self.ids.idcash.text = ""
            self.ids.idproduct.text = ""
        self.spreadData("desc")
        if self.ids.idSearch.text and self.rvSearch.data != []:
            self.search()

    def editEntry(self, id):
        self.ids.tabsContainer.switch_tab("Edit")
        self.itemId = id
        conn = sqlite3.connect(self.dbPath)
        cur = conn.cursor()
        all = cur.execute("SELECT * FROM exp_table WHERE id = ?", (self.itemId,))
        oneItem = all.fetchone()
        allDate = oneItem[1].split('-')
        year = allDate[0]
        month = allDate[1]
        day = allDate[2]
        self.ids.editday.text = day
        self.ids.editmonth.text = month
        self.ids.edityear.text = year
        self.ids.editprice.text = str(oneItem[2])
        self.ids.editproduct.text = oneItem[3]
        self.ids.editid.text = oneItem[0]
        self.productType = oneItem[4]
        self.oldCash = str(oneItem[2])
        conn.close()
        
    def saveEditedEntry(self):
        product = self.ids.editproduct.text.strip()
        if not self.ids.editday.text or not self.ids.editmonth.text or not self.ids.edityear.text:
            Snackbar(text="Invalid date.").open()
            return
        if not self.ids.editprice.text:
            Snackbar(text="Cash cannot be empty. Minimum '0'.").open()
            return
        if float(self.ids.editprice.text) < 0:
            Snackbar(text="Cash cannot be lower than '0'.").open()
            return
        if not product:
            Snackbar(text="Product cannot be empty.").open()
            return
        day = int(self.ids.editday.text.strip())
        month = int(self.ids.editmonth.text.strip())
        year = int(self.ids.edityear.text.strip())
        price = float(self.ids.editprice.text.strip())
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
            cur.execute('''UPDATE exp_table SET
                dt = ?,
                amount = ?,
                product = ?,
                category = ?
                WHERE id=?''',(f"{year}-{month}-{day}",price,product,self.editProductType,self.itemId,))
            conn.commit()
            conn.close()
            self.refreshChanges('edit', price)
        except ValueError:
            Snackbar(text="Invalid date.").open()
            return
        
        
    def emptyEditFields(self):
        self.ids.editday.text = ''
        self.ids.editmonth.text = ''
        self.ids.edityear.text = ''
        self.ids.editprice.text = ''
        self.ids.editproduct.text = ''
        self.ids.editid.text = ''
        self.productType = 'Stuff'
        self.itemId = ""


    def search(self):
        txt = self.ids.idSearch.text.strip().lower()
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        self.rvSearch.data=[]
        if txt == "":
            self.resultsLabel = "0"
            return
        else:
            d=c.execute(f"SELECT * FROM exp_table where dt || amount || product || category LIKE '%{txt}%' ")
            all = d.fetchall()
            self.resultsLabel = str(len(all))
            for i in reversed(all):
                self.rvSearch.data.append({'text': f"{i[1]}", 'secondary_text': f"{i[2]} - {i[3]}", 'tertiary_text': f"{i[4]}", "id": str(i[0])})
        conn.close()
        
        
    def getByYMD(self,item):
        self.rvBy.data = []
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("select dt,amount from exp_table")
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

        if item =='year':
            for i in reversed(allyears):
                c.execute(f"select dt, sum(amount) from exp_table where dt like '{i}%' ")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(i, j[1])
                    self.rvBy.data.append({"text": tmp})
        if item == "month":
            for i in reversed(allmonths):
                c.execute(f"select sum(amount) from exp_table where dt like '{i}%'")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(i, j[0])
                    self.rvBy.data.append({"text": tmp})
        if item =='day':
            for i in reversed(alldays):
                c.execute(f"select sum(amount) from exp_table where dt like '{i}%'")
                for j in c.fetchall():
                    tmp = "{} : [color=#fb8500]{:.2f}[/color] lei".format(i, j[0])
                    self.rvBy.data.append({"text": tmp})
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
        
        fromDate = datetime.strptime(fromDate,"%Y-%m-%d").date()
        toDate = datetime.strptime(toDate,"%Y-%m-%d").date()
        if fromDate > toDate:
            Snackbar(text='FROM date cannot be greater than TO date.',font_size="12sp").open()
            return
        
        self.newFileIntervalExport = f"intervalExport-{dayFrom}-{monthFrom}-{yearFrom}_{dayTo}-{monthTo}-{yearTo}.csv"
        self.intervalToList(fromDate,toDate)
        
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute(f"select sum(amount) from exp_table where dt >='{fromDate}' and dt <='{toDate}'")
        try:
            all = d.fetchall()
            total = "{:.2f}".format(all[0][0])
            self.ids.totalLabel.text = f"Total:     {total}"
        except:
            Snackbar(text="DB is empty.").open()
            return
        finally:
            conn.close()
        
    def intervalToList(self,fromDate,toDate):
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute(f"select * from exp_table where dt >='{fromDate}' and dt <='{toDate}' order by dt desc")
        all = d.fetchall()
        for i in all:
            tmp = {
                "id": i[0],
                "dt": i[1],
                "amount": i[2],
                "product": i[3],
                "category": i[4],
                "db": "expenses"
            }
            self.intervalExportList.append(tmp)
        conn.close()
        
    def exportIntervalToFile(self):
        try:
            with open(os.path.join(self.savePath, self.newFileIntervalExport), 'x') as f:
                fieldnames = ['id','dt','amount','product','category','db']
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
        
        
    def getTotalToSpend(self):
        conn = sqlite3.connect(self.dbPath)
        c=conn.cursor()
        d=c.execute("select total from total_money where id='1' ")
        all = d.fetchall()[0][0]
        self.totalToSpend = str(all)
        conn.close()
        
    def newTotalAfterAdd(self,cash):
        cash = float(cash)
        conn = sqlite3.connect(self.dbPath)
        c=conn.cursor()
        d=c.execute("SELECT total FROM total_money")
        all = float(d.fetchall()[0][0])
        newTotal = all - (cash)
        c.execute("update total_money set total=? where id='1'", (str(newTotal),))
        conn.commit()
        self.totalToSpend = str(newTotal)
        conn.close()
        
    def newTotalAfterEdit(self,newCash):
        conn = sqlite3.connect(self.dbPath)
        c=conn.cursor()
        newTotal = float(self.totalToSpend) + (float(self.oldCash) - float(newCash))
        c.execute("update total_money set total=? where id='1'", (str(newTotal),))
        conn.commit()
        conn.close()
        self.totalToSpend = str(newTotal)
        self.oldCash = ""
        
    def newTotalAfterDelete(self,income):
        income = float(income)
        conn = sqlite3.connect(self.dbPath)
        c = conn.cursor()
        d = c.execute("SELECT total FROM total_money")
        all = float(d.fetchall()[0][0])
        newTotal = all + (income)
        c.execute("update total_money set total=? where id='1'", (str(newTotal),))
        conn.commit()
        conn.close()
        self.totalToSpend = str(newTotal)
            
    # def checkTable(self):
    #     """income_table: id,dt,income,details,other"""
    #     """exp_table: id,dt,amount,product,category"""
    #     """income_table:
    #         id varchar(100)
    #         dt text
    #         income real
    #         details text
    #         other text
    #     """
    #     """
    #     exp_table:
    #         id varchar(100)
    #         dt text
    #         amount real
    #         product text
    #         category text
    #     """
    #     """total_money: id 1 total real"""
    #     conn = sqlite3.connect(self.dbPath)
    #     c= conn.cursor()
    #     d = c.execute("select * from total_money")
    #     all = d.fetchall()
    #     names = list(map(lambda x: x[0], c.description))
    #     conn.close()