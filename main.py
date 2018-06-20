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
from tkinter import tix
import sqlite3 as sql  # database operations
from datetime import date  # most of the date strings are get from it
from datetime import timedelta  # some date calculations
from datetime import datetime  # for report footer
import os
import __init__  # to get the application version


class Report(tk.Toplevel):

    # TODO: add a check box 'reverse' for displaying the dates on the list and TXT file in reverse order
    # TODO: Include results for 'migraine', 'medicine' and 'comment' to the list and generated TXT file
    # TODO: EPIC: add a button to generate graphs of the filtered result with mathPlotLib

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

        # widget creation
        self.label_filter = tk.Label(self, text='Choose a filter:')
        self.combo_filter = tk.OptionMenu(self, self.filter_value, *self.filter_values)  # official
        # self.combo_filter = ttk.Combobox(self, textvariable=self.filter_value, values=self.filter_values) # experiment
        self.button_filter = tk.Button(self, text='Filter', command=self.search_data)
        self.scroll_list = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.listbox = ttk.Treeview(self, columns=('Attribute', 'Value'), displaycolumns='#all', height=20,
                                    yscrollcommand=self.scroll_list.set)
        self.scroll_list.configure(command=self.listbox.yview)
        self.button_export_txt = tk.Button(self, text='Export to txt', command=self.export_to_txt)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='')

        # widgets manipulation on window startup
        self.button_export_txt.configure(state=tk.DISABLED)
        # self.combo_filter.state(statespec=('!disabled', 'readonly'))  # experimental

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
        for i in cursor:
            self.report_data.append((i[1], i[2], i[3], i[4], i[5]))
            report_date = i[1]
            report_intensity = str(i[2])
            report_migraine = 'yes' if i[3] == 1 else 'no'
            report_medicine = 'yes' if i[4] == 1 else 'no'
            iid = self.listbox.insert(parent='', index=0, open=True, text=report_date)
            self.listbox.insert(parent=iid, index=0, values=('Intensity', report_intensity))
            self.listbox.insert(parent=iid, index=1, values=('Migraine', report_migraine))
            self.listbox.insert(parent=iid, index=2, values=('Medicine', report_medicine))
            if i[5] is not None:
                self.listbox.insert(parent=iid, index=3, values=('Comment', i[5]))

        self.button_export_txt.configure(state=tk.NORMAL)

    def export_to_txt(self):
        # for later use:
        # results.append('{a:_<{width}.{width}}{b:_>{width}.{width}}{c:_>{width}.{width}}{d:_>{width}.{width}}'.
        # format(a=report_date, b=report_intensity, c=report_migraine, d=report_medicine,
        # width=int((list_width+2)/4)))
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

    # TODO: EPIC: create a new window for maintenance of the records, to allow changing of the values

    def __init__(self, master=None):
        tk.Frame.__init__(self, master)

        self.master.title('Headache Diary - v' + __init__.version)
        self.master.resizable(False, False)

        self.master.focus_force()

        self.connection = self.load_database()
        self.initialize_database()

        self.grid(sticky=tk.W + tk.E + tk.N + tk.S)

        yesterday = date.today() + timedelta(days=-1)

        self.spin_value_day = tk.StringVar()
        self.spin_value_day.set(str(yesterday.day))

        self.spin_value_month = tk.StringVar()
        self.spin_value_month.set(str(yesterday.month))

        self.spin_value_year = tk.StringVar()
        self.spin_value_year.set(str(yesterday.year))

        self.list_values_headache = ('0 - none', '1 - weak', '2 - medium', '3 - strong')
        self.list_value_headache = tk.StringVar()
        self.list_value_headache.set(str(self.list_values_headache[0]))

        self.check_migraine_value = tk.IntVar()
        self.check_migraine_value.set(0)

        self.check_medicine_value = tk.IntVar()
        self.check_medicine_value.set(0)

        self.label_top = tk.Label(self, text='Choose the date and headache intensity, then click on Save:')
        self.label_date = tk.Label(self, text='Selected date:', width=20, justify=tk.LEFT)
        self.spin_digits_day = tk.Spinbox(self, from_=0, to=32, increment=1, textvariable=self.spin_value_day,
                                          wrap=True, state='readonly', command=self.validate_date, width=20)
        self.spin_digits_month = tk.Spinbox(self, from_=0, to=13, increment=1, textvariable=self.spin_value_month,
                                            wrap=True, state='readonly', command=self.validate_date, width=20)
        self.spin_digits_year = tk.Spinbox(self, from_=2018, to=3000, increment=1, textvariable=self.spin_value_year,
                                           state='readonly', command=self.validate_date, width=20)

        self.nextday = tk.Button(self, text='+1', command=self.next_day)
        self.previousday = tk.Button(self, text='-1', command=self.previous_day)
        self.yesterday = tk.Button(self, text='yesterday', command=self.set_yesterday)
        self.today = tk.Button(self, text='today', command=self.set_today)

        self.label_intensity = tk.Label(self, text='Headache intensity:')
        self.combo_headache = tk.OptionMenu(self, self.list_value_headache, *self.list_values_headache)
        self.label_migraine = tk.Label(self, text='Migraine:')
        self.check_migraine = tk.Checkbutton(self, variable=self.check_migraine_value)
        self.label_medicine = tk.Label(self, text='Medicine:')
        self.check_medicine = tk.Checkbutton(self, variable=self.check_medicine_value)
        self.label_comment = tk.Label(self, text='Comment:')
        self.text_comment = tk.Text(self, wrap=tk.WORD, height=3, width=1)

        self.button_save = tk.Button(self, text='Save', command=self.save_value)
        self.button_report = tk.Button(self, text='Report', command=self.create_report)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.separator2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='')

        self.balloon = tix.Balloon(self.master)

        self.balloon.bind_widget(self.spin_digits_day,
                                 balloonmsg='Current selected day.')
        self.balloon.bind_widget(self.spin_digits_month,
                                 balloonmsg='Current selected month.')
        self.balloon.bind_widget(self.spin_digits_year,
                                 balloonmsg='Current selected year.')
        self.balloon.bind_widget(self.nextday,
                                 balloonmsg='Select next day.')
        self.balloon.bind_widget(self.previousday,
                                 balloonmsg='Select previous day.')
        self.balloon.bind_widget(self.yesterday,
                                 balloonmsg='Select yesterday.')
        self.balloon.bind_widget(self.today,
                                 balloonmsg='Select today.')
        self.balloon.bind_widget(self.combo_headache,
                                 balloonmsg='Click to select the intensity of your headache.')
        self.balloon.bind_widget(self.check_migraine,
                                 balloonmsg='Mark this box if you feel like the headache is connected to migraine.')
        self.balloon.bind_widget(self.check_medicine,
                                 balloonmsg='Mark this box if you took some medicine to alleviate the headache.')
        self.balloon.bind_widget(self.text_comment,
                                 balloonmsg='Add any comment you think is relevant for the selected date.')
        self.balloon.bind_widget(self.button_report,
                                 balloonmsg='Click here to open the report window, where you will\n'
                                            ' be able to check all previous dates and information.')
        self.balloon.bind_widget(self.button_save,
                                 balloonmsg='Save all the input information for the current selected date.')

        self.bind_all('<Alt-Right>', self.next_day)
        self.bind_all('<Alt-Left>', self.previous_day)

        self.validate_date()
        self.create_widgets()

        if os.name == 'nt':
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
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.rowconfigure(8, weight=0)
        self.rowconfigure(9, weight=0)
        self.rowconfigure(10, weight=0)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)

        self.label_top.grid(row=0, column=0, sticky=tk.W, columnspan=4)

        self.label_date.grid(row=1, column=0, sticky=tk.W)
        self.spin_digits_day.grid(row=1, column=1, sticky=tk.W + tk.E)
        self.spin_digits_month.grid(row=1, column=2, sticky=tk.W + tk.E)
        self.spin_digits_year.grid(row=1, column=3, sticky=tk.W + tk.E)

        self.previousday.grid(row=2, column=0, sticky=tk.W, pady=5, padx=5)
        self.yesterday.grid(row=2, column=1, sticky=tk.W + tk.E, pady=5, padx=2)
        self.today.grid(row=2, column=2, sticky=tk.W + tk.E, pady=5, padx=2)
        self.nextday.grid(row=2, column=3, sticky=tk.E, pady=5, padx=5)

        self.separator.grid(row=3, column=0, sticky=tk.E + tk.W, columnspan=4)
        
        self.label_intensity.grid(row=4, column=0, sticky=tk.W, columnspan=2, padx=5)
        self.combo_headache.grid(row=4, column=2, sticky=tk.E + tk.W, columnspan=2)

        self.label_migraine.grid(row=5, column=0, sticky=tk.W, columnspan=2, padx=5)
        self.check_migraine.grid(row=5, column=3, sticky=tk.E)

        self.label_medicine.grid(row=6, column=0, sticky=tk.W, columnspan=2, padx=5)
        self.check_medicine.grid(row=6, column=3, sticky=tk.E)

        self.label_comment.grid(row=7, column=0, sticky=tk.W + tk.N, padx=5)
        self.text_comment.grid(row=7, column=1, sticky=tk.W + tk.E, columnspan=3, padx=5)

        self.button_save.grid(row=8, column=3, sticky=tk.E + tk.W, pady=5, padx=5)
        self.button_report.grid(row=8, column=0, sticky=tk.E + tk.W, pady=5, padx=5)

        self.separator2.grid(row=9, column=0, sticky=tk.E + tk.W, columnspan=4)

        self.label_status.grid(row=10, column=0, sticky=tk.W, columnspan=4)

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
        elif int(self.spin_value_month.get()) == 3:  # march is special because of february
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
        migraine = self.check_migraine_value.get()
        medicine = self.check_medicine_value.get()
        comment = self.text_comment.get('1.0', tk.END)
        if comment == '\n':
            comment = None
        self.connection.execute(
            'insert into headache (date, intensity, migraine, medicine, comment) values (?, ?, ?, ?, ?)',
            (full_date, intensity, migraine, medicine, comment))
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
                                    '"intensity" INTEGER NOT NULL DEFAULT 1 CHECK(intensity >= 0 and intensity <= 3),'
                                    '"migraine" INTEGER NOT NULL DEFAULT 0,'
                                    '"medicine" INTEGER NOT NULL DEFAULT 0,'
                                    '"comment" TEXT DEFAULT NULL'
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

        if os.name == 'nt':
            report.update_idletasks()
            x = (report.winfo_screenwidth() - report.winfo_reqwidth()) / 2
            y = (report.winfo_screenheight() - report.winfo_reqheight()) / 2
            report.geometry("+%d+%d" % (x, y))

        report.mainloop()

    def validate_date(self):

        self.label_status.configure(text='')

        yesterday = date.today() + timedelta(days=-1)
        tomorrow = date.today() + timedelta(days=+1)
        full_date = self.get_full_date()

        self.increment_month()
        self.increment_year()

        quantity = self.connection.execute('select count(*) from headache where date = ?', (full_date,))
        value = quantity.fetchall()
        quantity = int(value[0][0])

        if quantity > 0:
            self.button_save.configure(state=tk.DISABLED)
            self.label_status.configure(text='( X ) This date is already fulfilled.')
        elif self.verify_date() is False:
            self.button_save.configure(state=tk.DISABLED)
            self.label_status.configure(text='( X ) This date is invalid.')
        else:
            self.button_save.configure(state=tk.NORMAL)
            if full_date == yesterday.isoformat():
                self.label_status.configure(text='Current selected date: yesterday.')
            elif full_date == tomorrow.isoformat():
                self.label_status.configure(text='Current selected date: tomorrow.')
            elif full_date == date.today().isoformat():
                self.label_status.configure(text='Current selected date: today.')
            else:
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

    def next_day(self, event=None):
        del event
        self.spin_value_day.set(str(int(self.spin_value_day.get())+1))
        self.validate_date()

    def previous_day(self, event=None):
        del event
        self.spin_value_day.set(str(int(self.spin_value_day.get()) - 1))
        self.validate_date()

    def set_yesterday(self):
        yesterday = date.today() + timedelta(days=-1)
        self.spin_value_day.set(str(yesterday.day))
        self.spin_value_month.set(str(yesterday.month))
        self.spin_value_year.set(str(yesterday.year))
        self.validate_date()

    def set_today(self):
        self.spin_value_day.set(str(date.today().day))
        self.spin_value_month.set(str(date.today().month))
        self.spin_value_year.set(str(date.today().year))
        self.validate_date()


if __name__ == '__main__':
    load_tix = tix.Tk()
    app = MainForm()
    app.mainloop()
