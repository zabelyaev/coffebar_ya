import sys

from PyQt5 import uic
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableView, QHeaderView


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.initUI()

    def initUI(self):
        self.showMaximized()

        db = QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('coffee.sqlite')
        db.open()

        model = QSqlTableModel(self, db)
        model.setTable('coffee')
        query = QSqlQuery('''SELECT 
                            id AS ID, 
                            title AS 'название сорта',
                            roasting AS 'степень обжарки',
                            CASE
                                WHEN is_ground = 0 
                                    THEN 'в зернах'
                                WHEN is_ground = 1 
                                    THEN 'молотый'
                            END AS 'молотый/в зернах',
                            toast_description AS 'описание вкуса',
                            price AS 'цена',
                            weight AS 'объем упаковки' 
                            FROM coffee''')
        model.setQuery(query)

        self.tableView.setModel(model)
        self.tv: QTableView = self.tableView
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # .horizontalHeader().setSectionResizeMode()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
