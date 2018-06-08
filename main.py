#!/usr/bin/env python3
# coding: utf-8

"""
Headache Diary - Keep track of the dates and intensity of your headaches
Copyright (C) 2018 Gidalti Lourenço Junior

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""

import tkinter as tk  # GUI toolkit
from tkinter import ttk  # widget for the separator
from tkinter import filedialog  # file dialog for the report export
from tkinter import messagebox  # messagebox for displaying error messages
import sqlite3 as sql  # database operations
from datetime import date  # most of the date strings are get from it
from datetime import timedelta  # some date calculations
from datetime import datetime  # for report footer
import __init__  # to get the application version


class Report(tk.Toplevel):

    def __init__(self, db, master=None):
        tk.Toplevel.__init__(self)

        # Properties:
        self.db = db
        self.master = master
        self.title('Report')
        self.resizable(True, True)
        self.report_data = list()

        # data
        self.filter_values = ('1 - last 31 days', '2 - this month', '3 - everything')
        self.filter_value = tk.StringVar()
        self.filter_value.set(self.filter_values[0])
        self.list_value = tk.StringVar()

        # row and column configuration
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)

        # widget creation
        self.label_filter = tk.Label(self, text='Choose a filter:')
        self.combo_filter = tk.OptionMenu(self, self.filter_value, *self.filter_values)
        self.button_filter = tk.Button(self, text='Filter', command=self.search_data)
        self.scroll_list = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = tk.Listbox(self, listvariable=self.list_value, exportselection=0,
                                  width=50, height=20, activestyle='dotbox', yscrollcommand=self.scroll_list.set)
        self.scroll_list.configure(command=self.listbox.yview)
        self.button_export_txt = tk.Button(self, text='Export to txt', command=self.export_to_txt)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='')

        # widgets manipulation on window startup
        self.button_export_txt.configure(state=tk.DISABLED)

        # widget deployment
        self.label_filter.grid(row=0, column=0, sticky=tk.W)
        self.combo_filter.grid(row=0, column=1, sticky=tk.W + tk.E)
        self.button_filter.grid(row=0, column=2, sticky=tk.W + tk.E)
        self.listbox.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S, columnspan=3)
        self.scroll_list.grid(row=1, column=3, stick=tk.N + tk.S)
        self.button_export_txt.grid(row=2, column=0, stick=tk.W, padx=5, pady=5)
        self.separator.grid(row=3, column=0, stick=tk.W + tk.E, columnspan=4)
        self.label_status.grid(row=4, column=0, stick=tk.W, columnspan=4)

    def search_data(self):
        list_width = self.listbox.cget('width')-10
        results = list()
        self.report_data.clear()
        cursor = None
        if self.filter_value.get()[0] == '1':  # last 31 days
            ago31days = (date.today() + timedelta(days=-31)).isoformat()
            quantity = self.db.execute('select count(*) from headache where date >= ?',
                                       (ago31days,))
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache where date >= ? order by date ASC',
                                     (ago31days,))
            self.label_status.configure(text='Report generated for last 31 days. Returned items: ' + quantity)
        elif self.filter_value.get()[0] == '2':  # this month
            thismonth = date.today().isoformat()[:7]
            quantity = self.db.execute('select count(*) from headache where date >= ?',
                                       (thismonth,))
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache where date >= ? order by date ASC', (thismonth,))
            self.label_status.configure(text='Report generated for this month. Returned items: ' + quantity)
        elif self.filter_value.get()[0] == '3':  # everything
            quantity = self.db.execute('select count(*) from headache')
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache order by date ASC')
            self.label_status.configure(text='Report generated for all available data. Returned items: ' + quantity)
        results.append('{a:.<{width}}{b:.>{width}}'.format(a='Date:', b='Intensity:', width=list_width))
        for i in cursor:
            self.report_data.append((i[1], i[2]))
            results.append('{a:.<{width}}{b:.>{width}}'.format(a=i[1], b=i[2], width=list_width))
        self.list_value.set(results)
        self.button_export_txt.configure(state=tk.NORMAL)

    def export_to_txt(self):
        header = ('*'*120) + '\n' + '{:*^120}'.format(' HEADACHE DIARY v' + __init__.version +
                                                      ' - By Gidalti Lourenço Junior - GPLv3.0 ')
        header += '\n' + ('*'*120) + '\n\n'
        table_header = '{:<60}'.format('Date:') + '{:>60}'.format('Intensity:') + '\n'
        footer = '\n{:*>120}'.format(' Generated in ' + str(str(datetime.now()).split('.')[0]) + ' ***')
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('TXT', '.txt')],
                                            initialfile='my_headache_diary_report', parent=self)
        if not path == '':
            with open(path, 'w') as file:
                file.write(header)
                file.write(table_header)
                for i in self.report_data:
                    file.write('{:.<60}'.format(i[0]) + '{:.>60}'.format(i[1]) + '\n')
                file.write(footer)
            self.label_status.configure(text='Report exported to "' + path + '".')
        else:
            self.label_status.configure(text='Export to txt cancelled by the user.')


class MainForm(tk.Frame):

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.master.title('Headache Diary - v' + __init__.version)
        self.master.resizable(False, False)

        self.connection = self.load_database()
        self.initialize_database()

        self.grid(sticky=tk.W + tk.E + tk.N + tk.S)

        self.spin_value_day = tk.StringVar()
        self.spin_value_day.set(str(date.today().day))

        self.spin_value_month = tk.StringVar()
        self.spin_value_month.set(str(date.today().month))

        self.spin_value_year = tk.StringVar()
        self.spin_value_year.set(str(date.today().year))

        self.list_values_headache = ('0 - none', '1 - weak', '2 - medium', '3 - strong')
        self.list_value_headache = tk.StringVar()
        self.list_value_headache.set(str(self.list_values_headache[0]))

        self.label_top = tk.Label(self, text='Choose the date and headache intensity, then click on Save:')
        self.label_date = tk.Label(self, text='Date:')
        self.spin_digits_day = tk.Spinbox(self, from_=0, to=32, increment=1, textvariable=self.spin_value_day,
                                          wrap=True, state='readonly', command=self.validate_date)
        self.spin_digits_month = tk.Spinbox(self, from_=0, to=13, increment=1, textvariable=self.spin_value_month,
                                            wrap=True, state='readonly', command=self.validate_date)
        self.spin_digits_year = tk.Spinbox(self, from_=2018, to=3000, increment=1, textvariable=self.spin_value_year,
                                           state='readonly', command=self.validate_date)
        self.label_intensity = tk.Label(self, text='Headache intensity:')
        self.combo_headache = tk.OptionMenu(self, self.list_value_headache, *self.list_values_headache)
        self.button_save = tk.Button(self, text='Save', command=self.save_value)
        self.button_report = tk.Button(self, text='Report', command=self.create_report)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='')

        self.validate_date()
        self.create_widgets()

        self.update_idletasks()
        x = (self.master.winfo_screenwidth() - self.master.winfo_reqwidth()) / 2
        y = (self.master.winfo_screenheight() - self.master.winfo_reqheight()) / 2
        self.master.geometry("+%d+%d" % (x, y))

    def create_widgets(self):
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        self.label_top.grid(row=0, column=0, sticky=tk.W + tk.E, columnspan=3)
        self.label_date.grid(row=1, column=0, sticky=tk.W)
        self.spin_digits_day.grid(row=1, column=1, sticky=tk.W + tk.E)
        self.spin_digits_month.grid(row=1, column=2, sticky=tk.W + tk.E)
        self.spin_digits_year.grid(row=1, column=3, sticky=tk.W + tk.E)

        self.label_intensity.grid(row=2, column=0, sticky=tk.W, columnspan=2)
        self.combo_headache.grid(row=2, column=2, sticky=tk.E + tk.W, columnspan=2)

        self.button_save.grid(row=3, column=3, sticky=tk.E + tk.W, pady=5, padx=5)
        self.button_report.grid(row=3, column=0, sticky=tk.E + tk.W, pady=5, padx=5)
        self.separator.grid(row=4, column=0, sticky=tk.E + tk.W, columnspan=4)
        self.label_status.grid(row=5, column=0, sticky=tk.W, columnspan=4)

    def increment_month(self):
        if int(self.spin_value_month.get()) in [4, 6, 8, 9, 11]:
            if self.spin_value_day.get() == '0':
                self.spin_value_month.set(int(self.spin_value_month.get()) - 1)
                self.spin_value_day.set(31)
            elif self.spin_value_day.get() == '31':
                self.spin_value_month.set(int(self.spin_value_month.get()) + 1)
                self.spin_value_day.set(1)
        elif int(self.spin_value_month.get()) in [1, 5, 7, 10, 12]:
            if self.spin_value_day.get() == '0':
                self.spin_value_month.set(int(self.spin_value_month.get()) - 1)
                self.spin_value_day.set(30)
            elif self.spin_value_day.get() == '32':
                self.spin_value_month.set(int(self.spin_value_month.get()) + 1)
                self.spin_value_day.set(1)
        elif int(self.spin_value_month.get()) == 3: # march is special because of february
            if self.spin_value_day.get() == '0':
                self.spin_value_month.set(int(self.spin_value_month.get()) - 1)
                self.spin_value_day.set(29)
            elif self.spin_value_day.get() == '32':
                self.spin_value_month.set(int(self.spin_value_month.get()) + 1)
                self.spin_value_day.set(1)
        else:  # february
            if self.spin_value_day.get() == '0':
                self.spin_value_month.set(int(self.spin_value_month.get()) - 1)
                self.spin_value_day.set(31)
            elif self.spin_value_day.get() == '30':
                self.spin_value_month.set(int(self.spin_value_month.get()) + 1)
                self.spin_value_day.set(1)

    def increment_year(self):
        if self.spin_value_month.get() == '0':
            self.spin_value_year.set(int(self.spin_digits_year.get()) - 1)
            self.spin_value_month.set(12)
        elif self.spin_value_month.get() == '13':
            self.spin_value_year.set(int(self.spin_digits_year.get()) + 1)
            self.spin_value_month.set(1)

    def save_value(self):
        full_date = self.get_full_date()
        intensity = int(self.list_value_headache.get()[0])
        self.connection.execute('insert into headache (date, intensity) values (?, ?)', (full_date, intensity))
        self.connection.commit()
        self.button_save.configure(state=tk.DISABLED)
        self.label_status.configure(text='( ! ) Date and intensity saved successfully!')

    @staticmethod
    def load_database():
        database = sql.Connection('headache_diary.db')
        return database

    def initialize_database(self):
        try:
            self.connection.execute('CREATE TABLE "headache" ('
                                    '"_id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, '
                                    '"date"	TEXT NOT NULL UNIQUE, '
                                    '"intensity"	INTEGER NOT NULL DEFAULT 1 CHECK(intensity >= 0 and intensity <= 3)'
                                    ');')
            self.connection.commit()
        except sql.OperationalError as e:
            if str(e) == 'table "headache" already exists':
                pass
            else:
                messagebox.showerror('Unexpected Error', e)

    def create_report(self):
        report = Report(db=self.connection, master=self)
        report.transient(self)
        report.update_idletasks()
        x = (report.winfo_screenwidth() - report.winfo_reqwidth()) / 2
        y = (report.winfo_screenheight() - report.winfo_reqheight()) / 2
        report.geometry("+%d+%d" % (x, y))
        report.mainloop()

    def validate_date(self):

        self.increment_month()
        self.increment_year()

        full_date = self.get_full_date()
        quantity = self.connection.execute('select count(*) from headache where date = ?', (full_date,))
        value = quantity.fetchall()
        quantity = int(value[0][0])

        if quantity > 0:
            self.button_save.configure(state=tk.DISABLED)
            self.label_status.configure(text='( X ) This date was already created.')
        elif self.verify_date() is False:
            self.button_save.configure(state=tk.DISABLED)
            self.label_status.configure(text='( X ) This date is invalid.')
        else:
            self.button_save.configure(state=tk.NORMAL)
            self.label_status.configure(text='')

    def get_full_date(self):
        day = '{:0>2}'.format(self.spin_value_day.get())
        month = '{:0>2}'.format(self.spin_digits_month.get())
        year = self.spin_digits_year.get()
        full_date = year + '-' + month + '-' + day
        return full_date

    def verify_date(self):
        day = int(self.spin_value_day.get())
        month = int(self.spin_digits_month.get())
        year = int(self.spin_digits_year.get())
        try:
            date.isoformat(date(year, month, day))
        except ValueError:
            return False
        else:
            return True


if __name__ == '__main__':
    app = MainForm()
    app.mainloop()
