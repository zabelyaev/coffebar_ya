import sys

from PyQt5 import uic
from PyQt5.QtCore import QModelIndex
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QHeaderView, QWidget, QComboBox, QAbstractItemView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.model = None
        self.row = None

        self.initUI()

    def initUI(self):
        self.addButton.clicked.connect(self.addBtnClick)
        self.editButton.clicked.connect(self.editBtnClick)
        self.delButton.clicked.connect(self.delBtnClick)

        self.tableView.clicked.connect(self.viewClicked)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)  # запрет на редактирование

    # событие, возникающее при клике на строку в Table View
    def viewClicked(self, clickedIndex: QModelIndex):
        self.model = clickedIndex.model()
        self.row = clickedIndex.row()

    def addBtnClick(self):
        # вызываем окно добавления/редактирования и передаем parent
        AddEditWindow(self)

    def editBtnClick(self):
        # если кликнули на редактирование, то передаем model и row
        if self.model is not None and self.row is not None:
            AddEditWindow(self, self.model, self.row)
        self.model = None
        self.row = None

    def delBtnClick(self):
        if self.model is not None and self.row is not None:
            db = QSqlDatabase.addDatabase('QSQLITE')
            db.setDatabaseName('coffee.sqlite')
            db.open()

            model = QSqlTableModel(self, db)
            model.setTable('coffee')

            query = QSqlQuery()
            query.exec_(f'''DELETE FROM coffee WHERE id={self.model.index(self.row, 0).data()}''')

            db.close()

            self.updateTableView()

    # событие возникает, когда окно отображается
    def showEvent(self, event):
        self.showMaximized()
        self.updateTableView()

    # функция для обновления данных в Tabel View
    def updateTableView(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('coffee.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('coffee')
        query = QSqlQuery('''SELECT 
                                    id AS ID, 
                                    title AS 'Название сорта',
                                    roasting AS 'Степень обжарки',
                                    CASE
                                        WHEN is_ground = 0 
                                            THEN 'Зерновой'
                                        WHEN is_ground = 1 
                                            THEN 'Молотый'
                                    END AS 'Молотый/Зерновой',
                                    toast_description AS 'Описание вкуса',
                                    price AS 'Цена',
                                    weight AS 'Объем упаковки' 
                                    FROM coffee''')
        model.setQuery(query)
        self.tableView.setModel(model)
        db.close()


# окно добавления/редактирования
class AddEditWindow(QMainWindow):
    def __init__(self, parent=None, model=None, row=None):
        super(AddEditWindow, self).__init__(parent)
        uic.loadUi('addEditCoffeeForm.ui', self)

        self.showMaximized()
        self.show()

        parent.window().hide()
        self.model = model
        self.row = row

        self.id = None

        self.addEditButton.clicked.connect(self.addEditBtnClick)
        self.is_add = True  # флаг определяющий добавления/изменение

        # если переданы model и row, то переключаемся в состояние редактирования
        if self.model is not None and self.row is not None:
            self.is_add = False
            self.showEditWindow()

    def closeEvent(self, event):
        self.parent().show()

    # функция, заполняющая поля ввода, при режиме Редактирование
    def showEditWindow(self):
        self.addEditButton.setText('Изменить')

        self.id: int = self.model.index(self.row, 0).data()
        title: str = self.model.index(self.row, 1).data()
        roasting: str = self.model.index(self.row, 2).data()
        ground_str: str = self.model.index(self.row, 3).data()

        is_ground = 0
        if ground_str == 'Молотый':
            is_ground = 1
        else:
            is_ground = 0

        toast_description: str = self.model.index(self.row, 4).data()
        price: int = self.model.index(self.row, 5).data()
        weight: int = self.model.index(self.row, 6).data()

        self.titleLE.setText(title)
        self.roastingLE.setText(roasting)
        self.isGroundCB.setCurrentIndex(is_ground)
        self.toastDescriptionLE.setText(toast_description)
        self.priceLE.setText(str(price))
        self.weightLE.setText(str(weight))

    # функция для получения данных с формы
    def getDataFromForm(self):
        data = {'title': self.titleLE.text(), 'roasting': self.roastingLE.text(),
                'isGround': self.isGroundCB.currentIndex(),
                'toastDescription': self.toastDescriptionLE.text(), 'price': self.priceLE.text(),
                'weight': self.weightLE.text()}

        return data

    def addEditBtnClick(self):
        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('coffee.sqlite')
        db.open()

        data = self.getDataFromForm()
        query = QSqlQuery()

        if self.is_add:
            query.exec_(f'''INSERT INTO coffee (id, title, roasting, is_ground, toast_description, price, weight)
                                        VALUES 
                                        (
                                            NULL,
                                            '{data['title']}',
                                            '{data['roasting']}',
                                            {int(data['isGround'])},
                                            '{data['toastDescription']}',
                                            {int(data['price'])},
                                            {int(data['weight'])}
                                        )
                                        ''')
        else:
            query.exec_(f'''UPDATE coffee 
                                    SET
                                        title='{data['title']}',
                                        roasting='{data['roasting']}',
                                        is_ground={int(data['isGround'])},
                                        toast_description='{data['toastDescription']}',
                                        price={int(data['price'])},
                                        weight={int(data['weight'])}
                                    WHERE id={self.id}''')
        db.commit()
        db.close()
        self.window().close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
