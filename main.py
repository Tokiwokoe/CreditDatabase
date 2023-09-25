import sys
import psycopg2
import openpyxl
import datetime
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QGraphicsScene
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from UIclass import LoginScreen, DeleteMessage, delete, main_window, Add, queries, graphics, add_worker, worker, bank, client, credit, return_credit


class AuthWindow(QMainWindow, LoginScreen.Ui_Auth):
    def __init__(self):
        super(AuthWindow, self).__init__()
        self.setupUi(self)
        self.login.clicked.connect(self.to_login)

    def to_login(self):
        try:
            self.user = self.loginfield.text()
            self.password = self.passwordfield.text()
            self.connection = psycopg2.connect(
                host='localhost',
                database='Credit',
                user=self.user,
                password=self.password
            )
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT current_user;")
            self.current_user = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT rolname FROM pg_user JOIN pg_auth_members ON pg_user.usesysid = pg_auth_members.member JOIN pg_roles ON pg_roles.oid = pg_auth_members.roleid WHERE pg_user.usename = current_user;")
            self.role_group = self.cursor.fetchone()[0]
            print(f'{self.current_user} из группы {self.role_group} вошёл в систему')
            if self.role_group == 'bank':
                self.admin_menu = MainMenu(self.connection, self.cursor, self.current_user, self.role_group)
                self.admin_menu.show()
            elif self.role_group == 'bank_worker':
                self.cursor.execute(f"SELECT departament FROM \"bank_worker\" WHERE login = '{self.user}'")
                self.departament = self.cursor.fetchone()[0]
                self.bank_menu = BankMenu(self.connection, self.cursor, self.current_user, self.departament, self.role_group)
                self.bank_menu.show()
            elif self.role_group == 'client_acc':
                self.cursor.execute(f"SELECT departament FROM \"client_acc\" WHERE login = '{self.user}'")
                self.departament = self.cursor.fetchone()[0]
                self.client_menu = ClientMenu(self.connection, self.cursor, self.current_user, self.role_group, self.departament)
                self.client_menu.show()
            else:
                self.error.setText('Такого пользователя нет')
            self.close()

        except psycopg2.Error as err:
            print(err)
            self.error.setText('Ошибка подключения')


class PrintTable(QMainWindow):
    def __init__(self):
        super(PrintTable, self).__init__()

    def to_print_table(self, query):
        self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        self.tableWidget.setRowCount(len(self.rows))
        self.tableWidget.setColumnCount(len(self.labels))
        self.tableWidget.setHorizontalHeaderLabels(self.labels)
        i = 0
        for elem in self.rows:
            j = 0
            for t in elem:
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(t).strip()))
                j += 1
            i += 1
        i = 0
        self.tableWidget.resizeColumnsToContents()

    def to_print_acc(self):
        query = 'SELECT login, departament FROM bank_worker ORDER BY id'
        self.labels = ['Логин', 'Номер банка']
        self.to_print_table(query)

    def to_print_bank(self):
        query = 'SELECT * FROM bank_view'
        self.labels = ['Название', 'Тип банка', 'Год открытия', 'Уставной фонд (млн.)', 'Телефон']
        self.to_print_table(query)

    def to_print_bamk_type(self):
        query = 'SELECT * FROM bank_type_view'
        self.labels = ['Тип банка']
        self.to_print_table(query)

    def to_print_client(self):
        query = 'SELECT * FROM client_view'
        self.labels = ['ФИО / Название', 'Город', 'Телефон', 'Номер счета']
        self.to_print_table(query)

    def to_print_city(self):
        query = 'SELECT * FROM city_view'
        self.labels = ['Город']
        self.to_print_table(query)

    def to_print_credit(self):
        query = 'SELECT * FROM credit_view'
        self.labels = ['Клиент', 'Банк', 'Тип кредита', 'Сумма', 'Годовой процент', 'Дата получения']
        self.to_print_table(query)

    def to_print_credit_type(self):
        query = 'SELECT * FROM credit_type_view'
        self.labels = ['Тип кредита']
        self.to_print_table(query)

    def to_print_return_credit(self):
        query = 'SELECT * FROM return_credit_view'
        self.labels = ['Клиент', 'Банк', 'Сумма', 'Дата возврата']
        self.to_print_table(query)


class MainMenu(PrintTable, main_window.Ui_MainWindow):
    def __init__(self, connection, cursor, current_user, role_group):
        super(MainMenu, self).__init__()
        self.setupUi(self)
        self.setFixedSize(1050, 720)
        self.bank.clicked.connect(self.to_print_bank)
        self.client.clicked.connect(self.to_print_client)
        self.credit.clicked.connect(self.to_print_credit)
        self.bamk_type.clicked.connect(self.to_print_bamk_type)
        self.city.clicked.connect(self.to_print_city)
        self.credit_type.clicked.connect(self.to_print_credit_type)
        self.return_credit.clicked.connect(self.to_print_return_credit)

        self.Change_button.clicked.connect(self.to_add)
        self.Delete_button.clicked.connect(self.to_delete)
        self.Workers_button.clicked.connect(self.to_add_worker)
        self.Queries_button.clicked.connect(self.queries)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.role_group = role_group

    def to_add(self):
        self.add = Add(self.connection, self.cursor, self.role_group)
        self.add.show()

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_worker(self):
        self.worker = AddWorker(self.connection, self.cursor, self.current_user, self.role_group)
        self.worker.show()

    def queries(self):
        self.q = Queries(self.connection, self.cursor)
        self.q.show()


class Add(QMainWindow, Add.Ui_Dialog):
    def __init__(self, connection, cursor, role_group):
        super(Add, self).__init__()
        self.setupUi(self)
        self.role_group = role_group
        self.connection = connection
        self.cursor = cursor
        if role_group == 'bank':
            self.table.addItem('Город')
            self.table.addItem('Тип банка')
            self.table.addItem('Тип кредита')
            self.table.addItem('Возврат кредита')
        self.OKbutton.clicked.connect(self.to_add)

    def to_add(self):
        if self.table.currentText() == 'Город':
            self.table_name = 'city'
        elif self.table.currentText() == 'Тип банка':
            self.table_name = 'bank_type'
        elif self.table.currentText() == 'Тип кредита':
            self.table_name = 'credit_type'
        try:
            self.name = self.id.text()
            query = f'SELECT id FROM {self.table_name} ORDER BY id DESC LIMIT 1'
            self.cursor.execute(query)
            self.name_id = self.cursor.fetchone()
            if not self.name_id:
                self.name_id = [0]
            query = f"INSERT INTO {self.table_name} VALUES({int(self.name_id[0]) + 1}, '{self.name}')"
            self.cursor.execute(query)
            self.connection.commit()
            self.error.setText('Успешно добавлено')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class DeleteMess(QMainWindow, DeleteMessage.Ui_Dialog):
    def __init__(self, connection, cursor, table, id):
        super(DeleteMess, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.table = table
        self.id = id
        query = f'SELECT * FROM {self.table} WHERE id = {self.id}'
        self.cursor.execute(query)
        self.text.setText(f'Вы действительно хотите удалить {self.cursor.fetchall()}')
        self.OKbutton.clicked.connect(self.delete)
        self.CancelButton.clicked.connect(self.cancel)

    def delete(self):
        try:
            query = f'DELETE FROM {self.table} WHERE id = {self.id}'
            self.cursor.execute(query)
            self.connection.commit()
            self.error.setText('Удалено!')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')

    def cancel(self):
        self.close()


class Delete(QMainWindow, delete.Ui_Dialog):
    def __init__(self, connection, cursor, role_group):
        super(Delete, self).__init__()
        self.setupUi(self)
        self.role_group = role_group
        self.connection = connection
        self.cursor = cursor
        if role_group == 'bank':
            self.table.addItem('Город')
            self.table.addItem('Тип банка')
            self.table.addItem('Тип кредита')
            self.table.addItem('Банкиры')
            self.table.addItem('Клиенты')
        elif role_group == 'bank_worker':
            self.table.addItem('Кредит')
        elif role_group == 'client_acc':
            self.table.addItem('Возврат кредитов')
        self.OKbutton.clicked.connect(self.to_delete)

    def to_delete(self):
        if self.table.currentText() == 'Город':
            self.table_name = 'city'
        elif self.table.currentText() == 'Тип банка':
            self.table_name = 'bank_type'
        elif self.table.currentText() == 'Тип кредита':
            self.table_name = 'credit_type'
        elif self.table.currentText() == 'Кредит':
            self.table_name = 'language'
        elif self.table.currentText() == 'Возврат кредита':
            self.table_name = 'return_credit'
        elif self.table.currentText() == 'Банкиры':
            self.table_name = 'bank_worker'
        elif self.table.currentText() == 'Клиенты':
            self.table_name = 'client_acc'
        id = self.id.text()
        self.message = DeleteMess(self.connection, self.cursor, self.table_name, id)
        self.message.show()


class AddWorker(PrintTable, worker.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, role_group):
        super(AddWorker, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.role_group = role_group
        self.update_reg.clicked.connect(self.to_print_reg)
        self.update_acc.clicked.connect(self.to_print_acc)
        self.add_acc.clicked.connect(self.to_add)
        self.add_reg.clicked.connect(self.to_add)
        self.delete_reg.clicked.connect(self.to_delete)
        self.delete_acc.clicked.connect(self.to_delete)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add(self):
        self.add = AddEmployees(self.connection, self.cursor)
        self.add.show()

    def to_print_reg(self):
        query = 'SELECT login, departament FROM client_acc ORDER BY id'
        self.labels = ['Логин', 'Номер клиента']
        self.cursor.execute(query)
        self.rows = self.cursor.fetchall()
        self.tableWidget_2.setRowCount(len(self.rows))
        self.tableWidget_2.setColumnCount(len(self.labels))
        self.tableWidget_2.setHorizontalHeaderLabels(self.labels)
        i = 0
        for elem in self.rows:
            j = 0
            for t in elem:
                self.tableWidget_2.setItem(i, j, QTableWidgetItem(str(t).strip()))
                j += 1
            i += 1
        i = 0
        self.tableWidget_2.resizeColumnsToContents()


class AddEmployees(QMainWindow, add_worker.Ui_Dialog):
    def __init__(self, connection, cursor):
        super(AddEmployees, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.table.addItem('Банкиры')
        self.table.addItem('Клиенты')
        self.table_name = 'bank_worker'
        self.table.currentTextChanged.connect(self.handle_table_change)  # Подключение сигнала
        self.add_button.clicked.connect(self.to_add)

    def handle_table_change(self):
        if self.table.currentText() == 'Банкиры':
            self.table_name = 'bank_worker'
            self.dep.show()
            self.label_6.show()
        if self.table.currentText() == 'Клиенты':
            self.table_name = 'client_acc'
            self.dep.show()
            self.label_6.show()

    def to_add(self):
        self.query = f'SELECT id FROM {self.table_name} ORDER BY id DESC'
        self.cursor.execute(self.query)
        self.id = self.cursor.fetchone()
        if not self.id:
            self.id = [0]
        self.query = f"INSERT INTO {self.table_name} VALUES ({int(self.id[0])+1}, '{self.log.text()}', {self.dep.text()})"
        try:
            self.cursor.execute(self.query)
            self.connection.commit()
            self.error.setText('Успешно добавлено')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class BankMenu(PrintTable, credit.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, departament, role_group):
        super(BankMenu, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.departament = departament
        self.role_group = role_group
        self.auth_as.setText(f'Вы вошли как: {self.current_user}, банк № {self.departament}')
        self.Update_btn.clicked.connect(self.to_print_help_as_accountant)
        self.Add_btn.clicked.connect(self.to_add_help)
        self.Delete_btn.clicked.connect(self.to_delete)

    def to_print_help_as_accountant(self):
        query = f' SELECT client.name AS client, bank.name AS bank, credit_type.name AS credit_type, credit.sum, credit.year_percent, credit.date FROM credit LEFT JOIN credit_type ON credit_type.id = credit.credit_type LEFT JOIN client ON client.id = credit.client_id LEFT JOIN bank ON bank.id = credit.bank_id WHERE bank.id = {self.departament}'
        self.labels = ['Клиент', 'Банк', 'Тип кредита', 'Сумма', 'Годовой процент', 'Дата']
        self.to_print_table(query)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_help(self):
        self.add = AddCredit(self.connection, self.cursor, self.departament)
        self.add.show()


class ClientMenu(PrintTable, client.Ui_Dialog):
    def __init__(self, connection, cursor, current_user, role_group, departament):
        super(ClientMenu, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.current_user = current_user
        self.dep = departament
        self.role_group = role_group
        query = f'SELECT name FROM client WHERE id = {self.dep}'
        self.cursor.execute(query)
        self.lastname = self.cursor.fetchone()
        self.author = self.lastname[0].replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        self.auth_as.setText(f'Вы вошли как: {current_user}, {self.author}')
        self.Update_btn.clicked.connect(self.to_print_book_as_author)
        self.Add_btn.clicked.connect(self.to_add_client)
        self.Delete_btn.clicked.connect(self.to_delete)

    def to_print_book_as_author(self):
        query = f'SELECT client.name AS client, bank.name AS bank, return_credit.sum, return_credit.return_date FROM return_credit LEFT JOIN client ON client.id = return_credit.client_id LEFT JOIN bank ON bank.id = return_credit.bank_id WHERE client.id = {self.dep}'
        self.labels = ['Клиент', 'Банк', 'Сумма возврата', 'Дата возврата']
        self.to_print_table(query)

    def to_delete(self):
        self.delete = Delete(self.connection, self.cursor, self.role_group)
        self.delete.show()

    def to_add_client(self):
        self.add = AddReturn(self.connection, self.cursor, self.dep)
        self.add.show()


class AddCredit(QMainWindow, bank.Ui_Dialog):
    def __init__(self, connection, cursor, departament):
        super(AddCredit, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.departament = departament
        query = 'SELECT id, name FROM client'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.client.addItem(str(t))
        self.Add.clicked.connect(self.correct_data)

    def correct_data(self):
        sum = self.sum.text()
        client = self.client.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        client_id = str(client[0])
        percent = self.percent.text()
        if int(sum) > 0:
            try:
                query = f"INSERT INTO credit VALUES({client_id}, {self.departament}, 1, {sum}, {percent}, '{datetime.date.today()}')"
                self.cursor.execute(query)
                self.connection.commit()
                self.error.setText('Успешно добавлено')
            except Exception as err:
                print(err)
                self.error.setText('Что-то пошло не так :(')
        else:
            self.error.setText('Проверьте корректность заполнения полей!')


class AddReturn(QMainWindow, return_credit.Ui_Dialog):
    def __init__(self, connection, cursor, departament):
        super(AddReturn, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.dep = departament
        query = f'SELECT id, bank.name FROM credit LEFT JOIN bank ON bank.id = credit.bank_id WHERE credit.client_id = {self.dep}'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.credit.addItem(str(t))
        self.Add.clicked.connect(self.correct_data)

    def correct_data(self):
        sum = self.sum.text()
        if int(sum) > 0:
            exemption = self.credit.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            exemption_id = str(exemption[0])
            if exemption_id:
                try:
                    query = f'SELECT id FROM return_credit ORDER BY id DESC LIMIT 1'
                    self.cursor.execute(query)
                    self.name_id = self.cursor.fetchone()
                    if not self.name_id:
                        self.name_id = [0]
                    query = f"INSERT INTO return_credit VALUES({int(self.name_id[0])+1}, {self.dep}, {exemption_id}, '{sum}', \'{datetime.date.today()}\')"
                    self.cursor.execute(query)
                    self.connection.commit()
                    self.error.setText('Успешно добавлено')
                except Exception as err:
                    print(err)
                    self.error.setText('Что-то пошло не так :(')
            else:
                self.error.setText('Проверьте корректность заполнения полей!')


class Queries(QMainWindow, queries.Ui_Dialog):
    def __init__(self, connection, cursor):
        super(Queries, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.queries.currentTextChanged.connect(self.handle_queries_change)  # Подключение сигнала
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по внешнему ключу')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по внешнему ключу (2)')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по датам')
        self.queries.addItem('Симметричное внутреннее соединение с условием отбора по датам (2)')
        self.queries.addItem('Симметричное внутреннее соединение без условия')
        self.queries.addItem('Симметричное внутреннее соединение без условия (2)')
        self.queries.addItem('Симметричное внутреннее соединение без условия (3)')
        self.queries.addItem('Левое внешнее соединение')
        self.queries.addItem('Правое внешнее соединение')
        self.queries.addItem('Запрос на запросе по принципу левого соединения')
        self.queries.addItem('Итоговый запрос без условия')
        self.queries.addItem('Итоговый запрос с условием на данные')
        self.queries.addItem('Итоговый запрос с условием на группы')
        self.queries.addItem('Итоговый запрос с условием на данные и на группы')
        self.queries.addItem('Запрос с подзапросом')

    def handle_queries_change(self):
        if self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по внешнему ключу':
            self.hide_all()
            self.label_combo.show()
            self.label_combo.setText('Выберите тип банка')
            self.comboBox.show()
            query = 'SELECT id, name FROM bank_type'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            district = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            district_id = str(district[0])
            self.labels = ['Банк', 'Телефон', 'Тип банка']
            self.query = f'SELECT * FROM q1({district_id})'
            self.comboBox.currentTextChanged.connect(self.q1)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по внешнему ключу (2)':
            self.hide_all()
            self.hide_all()
            self.label_combo.show()
            self.comboBox.show()
            self.label_combo.setText('Выберите город')
            self.comboBox.show()
            query = 'SELECT id, name FROM city'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            exemption = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            exemption_id = str(exemption[0])
            self.labels = ['Фамилия / Название', 'Город']
            self.query = f'SELECT * FROM q2({exemption_id})'
            self.comboBox.currentTextChanged.connect(self.q2)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по датам':
            self.hide_all()
            self.dateEdit.show()
            self.label_date.show()
            self.label_date.setText('Введите дату')
            self.dateEdit.dateChanged.connect(self.q3)  # Подключение сигнала
        elif self.queries.currentText() == 'Симметричное внутреннее соединение с условием отбора по датам (2)':
            self.hide_all()
            self.dateEdit.show()
            self.label_date.show()
            self.label_date.setText('Введите дату')
            self.textEdit.textChanged.connect(self.q4)
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия':
            self.hide_all()
            self.labels = ['Фамилия / Название', 'Банк']
            self.query = 'SELECT * FROM q5()'
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия (2)':
            self.hide_all()
            self.labels = ['Фамилия / Название', 'Город']
            self.query = 'SELECT * FROM q6()'
        elif self.queries.currentText() == 'Симметричное внутреннее соединение без условия (3)':
            self.hide_all()
            self.labels = ['Банк', 'Тип банка']
            self.query = f'SELECT * FROM q7()'
        elif self.queries.currentText() == 'Левое внешнее соединение':
            self.hide_all()
            self.labels = ['Фамилия / Название', 'Сумма кредита']
            self.query = f'SELECT * FROM q8()'
        elif self.queries.currentText() == 'Правое внешнее соединение':
            self.hide_all()
            self.labels = ['Фамилия / Название', 'Сумма кредита']
            self.query = f'SELECT * FROM q9()'
        elif self.queries.currentText() == 'Запрос на запросе по принципу левого соединения':
            self.hide_all()
            self.textEdit.setText('')
            self.label_text.show()
            self.textEdit.show()
            self.label_text.setText('Выберите банк')
            self.textEdit.textChanged.connect(self.q10)
        elif self.queries.currentText() == 'Итоговый запрос без условия':
            self.hide_all()
            self.labels = ['Клиент', 'Количество кредитов']
            self.query = f'SELECT * FROM q11()'
        elif self.queries.currentText() == 'Итоговый запрос с условием на данные':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text_2.show()
            self.textEdit_2.show()
            self.textEdit.setText('')
            self.textEdit_2.setText('')
            self.label_text.setText('Выберите начальную сумму кредита')
            self.label_text_2.setText('Выберите конечную сумму кредита')
            self.textEdit.textChanged.connect(self.q12)
            self.textEdit_2.textChanged.connect(self.q12)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Итоговый запрос с условием на группы':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text.setText('Выберите количество кредитов')
            self.textEdit.textChanged.connect(self.q13)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Итоговый запрос с условием на данные и на группы':
            self.hide_all()
            self.label_text.show()
            self.textEdit.show()
            self.label_text_2.show()
            self.textEdit_2.show()
            self.label_text_3.show()
            self.textEdit_3.show()
            self.textEdit.setText('')
            self.textEdit_2.setText('')
            self.label_text.setText('Выберите начальную сумму кредита')
            self.label_text_2.setText('Выберите конечную сумму кредита')
            self.label_text_3.setText('Выберите количество кредитов')
            self.textEdit.textChanged.connect(self.q14)
            self.textEdit_2.textChanged.connect(self.q14)
            self.textEdit_3.textChanged.connect(self.q14)
            self.excel_btn.show()
            self.graph_btn.show()
        elif self.queries.currentText() == 'Запрос с подзапросом':
            self.hide_all()
            self.label_combo.show()
            self.comboBox.show()
            self.label_combo.setText('Выберите город')
            self.comboBox.show()
            query = 'SELECT id, name FROM city'
            self.cursor.execute(query)
            for t in self.cursor.fetchall():
                self.comboBox.addItem(str(t))
            city = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
            city_id = str(city[1])
            self.labels = ['Клиент']
            self.query = f'SELECT * FROM q16({city_id})'
            self.comboBox.currentTextChanged.connect(self.q16)
        self.print.clicked.connect(self.to_print)
        self.graph_btn.clicked.connect(self.create_chart)
        self.excel_btn.clicked.connect(self.export_to_excel)

    def hide_all(self):
        self.label_text.hide()
        self.textEdit.hide()
        self.label_combo.hide()
        self.comboBox.hide()
        self.label_text_2.hide()
        self.comboBox.clear()
        self.textEdit_2.hide()
        self.textEdit.clear()
        self.textEdit_2.clear()
        self.textEdit_3.clear()
        self.label_text_3.hide()
        self.textEdit_3.hide()
        self.dateEdit.hide()
        self.label_date.hide()
        self.graph_btn.hide()
        self.excel_btn.hide()

    def q1(self):
        district = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        district_id = str(district[0])
        self.labels = ['Банк', 'Телефон', 'Тип банка']
        self.query = f'SELECT * FROM q1({district_id})'

    def q2(self):
        exemption = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        exemption_id = str(exemption[0])
        self.labels = ['Фамилия / Название', 'Город']
        self.query = f'SELECT * FROM q2({exemption_id})'

    def q3(self):
        date = self.dateEdit.text()
        self.labels = ['Фамилия / Название', 'Банк']
        self.query = f"SELECT * FROM q3('{date}')"

    def q4(self):
        year = self.textEdit.text()
        self.labels = ['Фамилия / Название', 'Банк']
        self.query = f'SELECT * FROM q4({year})'

    def q10(self):
        name = self.textEdit.text()
        self.labels = ['Банк', 'Клиент']
        self.query = f"SELECT * FROM q10('{name}')"

    def q12(self):
        organ1 = self.textEdit.text()
        organ2 = self.textEdit_2.text()
        self.labels = ['Клиент', 'Количество кредитов']
        self.query = f'SELECT * FROM q12({organ1}, {organ2})'

    def q13(self):
        book_count = self.textEdit.text()
        self.labels = ['Банк', 'Количество выданных кредитов']
        self.query = f'SELECT * FROM q13({book_count})'

    def q14(self):
        organ1 = self.textEdit.text()
        organ2 = self.textEdit_2.text()
        helps = self.textEdit_3.text()
        self.labels = ['Клиент', 'Количество кредитов']
        self.query = f'SELECT * FROM q14({organ1}, {organ2}, {helps})'

    def q16(self):
        query = 'SELECT id, name FROM city'
        self.cursor.execute(query)
        for t in self.cursor.fetchall():
            self.comboBox.addItem(str(t))
        dist = self.comboBox.currentText().replace('(', '').replace(')', '').replace(' \'', '\'').split(',')
        dist_id = str(dist[1])
        self.labels = ['Клиент']
        self.query = f'SELECT * FROM q16({dist_id})'

    def create_chart(self):
        self.label = self.queries.currentText()
        self.chart = Chart(self.connection, self.cursor, self.query, self.label)
        self.chart.show()

    def to_print(self):
        try:
            self.cursor.execute(self.query)
            self.rows = self.cursor.fetchall()
            self.tableWidget.setRowCount(len(self.rows))
            self.tableWidget.setColumnCount(len(self.labels))
            self.tableWidget.setHorizontalHeaderLabels(self.labels)
            i = 0
            for elem in self.rows:
                j = 0
                for t in elem:
                    self.tableWidget.setItem(i, j, QTableWidgetItem(str(t).strip()))
                    j += 1
                i += 1
            i = 0
            self.tableWidget.resizeColumnsToContents()
        except psycopg2.Error as err:
            print(err)
            self.error.setText('Проверьте ввод!')

    def export_to_excel(self):
        self.label = self.queries.currentText()
        self.cursor = self.connection.cursor()
        book = openpyxl.Workbook()
        sheet = book.active
        self.cursor.execute(self.query)
        results = self.cursor.fetchall()
        i = 0
        for row in results:
            i += 1
            j = 1
            for col in row:
                cell = sheet.cell(row=i, column=j)
                cell.value = col
                j += 1
        try:
            book.save(f"{self.label}.xlsx")
            self.error.setText('Успешно!')
        except Exception as err:
            print(err)
            self.error.setText('Ошибка!')


class Chart(QMainWindow, graphics.Ui_Dialog):
    def __init__(self, connection, cursor, query, label):
        super(Chart, self).__init__()
        self.setupUi(self)
        self.connection = connection
        self.cursor = cursor
        self.query = query
        self.label = label.split('. ')
        self.cursor.execute(self.query)
        self.graphics_name.setText(self.label[0])
        data = self.cursor.fetchall()
        categories = [str(row[0]) for row in data]
        values = [row[1] for row in data]
        series = QBarSeries()
        bar_set = QBarSet("Количество кредитов")
        for value in values:
            bar_set.append(value)
        bar_set.setColor(QColor('black'))
        series.append(bar_set)
        chart = QChart()
        chart.addSeries(series)
        axis_x = QBarCategoryAxis()
        axis_x.append(categories)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        scene = QGraphicsScene()
        scene.addItem(chart)
        chart.setMinimumSize(500, 500)
        scene.setSceneRect(chart.rect())
        self.graphicsView.setScene(scene)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AuthWindow()

    window.show()
    sys.exit(app.exec_())
