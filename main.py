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

DISABLED_BUTTON_BKGRND = 'DarkGray'
ENABLED_BUTTON_BKGRND = 'LightGreen'


class Maintenance(tk.Toplevel):

    def __init__(self, db, master=None, data=None):
        tk.Toplevel.__init__(self)

        # Properties:
        self.db = db
        self.master = master
        self.date = data[0]
        self.intensity = data[1]
        self.migraine = data[2]
        self.medicine = data[3]
        self.comment = data[4]
        self.title('Maintenance for {date}'.format(date=self.date))
        self.resizable(True, True)

        # data
        self.list_values_headache = ('0 - none', '1 - weak', '2 - medium', '3 - strong')
        self.list_value_headache = tk.StringVar()
        self.list_value_headache.set(str(self.list_values_headache[self.intensity]))
        self.check_migraine_value = tk.IntVar()
        self.check_migraine_value.set(self.migraine)
        self.check_medicine_value = tk.IntVar()
        self.check_medicine_value.set(self.medicine)

        # widget creation
        self.label_date = tk.Label(self, text='Date under maintenance:')
        self.label_date_value = tk.Label(self, text=self.date)
        self.label_intensity = tk.Label(self, text='Headache intensity:')
        self.combo_headache = tk.OptionMenu(self, self.list_value_headache, *self.list_values_headache)
        self.label_migraine = tk.Label(self, text='Migraine:')
        self.check_migraine = tk.Checkbutton(self, variable=self.check_migraine_value)
        self.label_medicine = tk.Label(self, text='Medicine:')
        self.check_medicine = tk.Checkbutton(self, variable=self.check_medicine_value)
        self.label_comment = tk.Label(self, text='Comment:')
        self.text_comment = tk.Text(self, wrap=tk.WORD, height=3, width=1)
        self.button_save = tk.Button(self, text='Save', command=self.save_data)
        self.button_cancel = tk.Button(self, text='Cancel', command=self.cancel)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='Maintenance ready.')

        self.balloon = tix.Balloon(self.master)

        self.balloon.bind_widget(self.combo_headache,
                                 balloonmsg='Click to select the intensity of your headache.')
        self.balloon.bind_widget(self.check_migraine,
                                 balloonmsg='Mark this box if you feel like the headache is connected to migraine.')
        self.balloon.bind_widget(self.check_medicine,
                                 balloonmsg='Mark this box if you took some medicine to alleviate the headache.')
        self.balloon.bind_widget(self.text_comment,
                                 balloonmsg='Add any comment you think is relevant for the selected date.')
        self.balloon.bind_widget(self.button_cancel,
                                 balloonmsg='Dismiss this window without changing any value.')
        self.balloon.bind_widget(self.button_save,
                                 balloonmsg='Update all the input information for the current selected date.')

        # widgets manipulation on window startup
        self.text_comment.delete(tk.INSERT, tk.END)
        if self.comment is not None:
            self.text_comment.insert(tk.INSERT, self.comment)
        self.button_save.configure(background=ENABLED_BUTTON_BKGRND)

        # row and column configuration
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=1)
        self.rowconfigure(6, weight=0)
        self.rowconfigure(7, weight=0)
        self.rowconfigure(8, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # widget deployment
        self.label_date.grid(row=0, column=0, sticky=tk.W)
        self.label_date_value.grid(row=0, column=1, sticky=tk.E)
        self.label_intensity.grid(row=1, column=0, sticky=tk.W)
        self.combo_headache.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5)
        self.label_migraine.grid(row=2, column=0, sticky=tk.W)
        self.check_migraine.grid(row=2, column=1, sticky=tk.E)
        self.label_medicine.grid(row=3, column=0, sticky=tk.W)
        self.check_medicine.grid(row=3, column=1, sticky=tk.E)
        self.label_comment.grid(row=4, column=0, sticky=tk.W)
        self.text_comment.grid(row=5, column=0, stick=tk.W + tk.E + tk.N + tk.S, columnspan=2)
        self.button_save.grid(row=6, column=1, sticky=tk.E, pady=5, padx=5)
        self.button_cancel.grid(row=6, column=0, stick=tk.W, pady=5, padx=5)
        self.separator.grid(row=7, column=0, stick=tk.W + tk.E, columnspan=2)
        self.label_status.grid(row=8, column=0, stick=tk.W, columnspan=2)

    def save_data(self):
        self.intensity = int(self.list_value_headache.get()[0])
        self.migraine = self.check_migraine_value.get()
        self.medicine = self.check_medicine_value.get()
        self.comment = self.text_comment.get('1.0', tk.END)
        if self.comment == '\n':
            self.comment = None
        if self.comment is not None and self.comment[-1] == '\n':
            self.comment = self.comment[0:-1]
        self.db.execute(
            'update headache set intensity = ?, migraine = ?, medicine = ?, comment = ? where date = ?',
            (self.intensity, self.migraine, self.medicine, self.comment, self.date))
        self.db.commit()
        self.destroy()

    def cancel(self):
        self.destroy()


class Report(tk.Toplevel):

    # TODO: EPIC: add a button to generate graphs of the filtered result with mathPlotLib

    def __init__(self, db, master=None):
        tk.Toplevel.__init__(self)

        # Properties:
        self.db = db
        self.master = master
        self.title('Report')
        self.resizable(True, True)
        self.report_data = list()
        self.column_size = 120

        # data
        self.filter_values = ('1 - last 31 days', '2 - this month', '3 - everything')
        self.filter_value = tk.StringVar()
        self.filter_value.set(self.filter_values[0])
        self.list_value = tk.StringVar()
        self.check_reverse_dates = tk.IntVar()
        self.check_reverse_dates.set(0)
        self.ord = 'ASC'

        # widget creation
        self.label_filter = tk.Label(self, text='Choose a filter:')
        self.label_reverse = tk.Label(self, text='Most recent on top:')
        self.check_reverse = tk.Checkbutton(self, variable=self.check_reverse_dates)
        self.combo_filter = tk.OptionMenu(self, self.filter_value, *self.filter_values)  # official
        # self.combo_filter = ttk.Combobox(self, textvariable=self.filter_value, values=self.filter_values) # experiment
        self.button_filter = tk.Button(self, text='Filter', command=self.search_data)
        self.vscroll_list = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.hscroll_list = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        self.hlist = tix.HList(self, yscrollcommand=self.vscroll_list.set, xscrollcommand=self.hscroll_list.set,
                               columns=5, header=True, height=25, width=100, indicator=True, selectmode='browse',
                               command=self.double_click)
        self.vscroll_list.configure(command=self.hlist.yview)
        self.hscroll_list.configure(command=self.hlist.xview)
        self.button_export_txt = tk.Button(self, text='Export to txt', command=self.export_to_txt)
        self.separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        self.label_status = tk.Label(self, text='')
        self.balloon = tix.Balloon(self.master)

        self.balloon.bind_widget(self.check_reverse,
                                 balloonmsg='Mark this option to display the most recent dates on top of the list.')
        self.balloon.bind_widget(self.combo_filter,
                                 balloonmsg='Select the range of your search.')
        self.balloon.bind_widget(self.button_filter,
                                 balloonmsg='Apply the filter based on your search.')
        self.balloon.bind_widget(self.hlist,
                                 balloonmsg='Double click to edit an entry.')
        self.balloon.bind_widget(self.button_export_txt,
                                 balloonmsg='Export the table values to a text file.')

        # widgets manipulation on window startup
        self.button_export_txt.configure(state=tk.DISABLED)
        self.button_export_txt.configure(background=DISABLED_BUTTON_BKGRND)
        # self.combo_filter.state(statespec=('!disabled', 'readonly'))  # experimental
        self.hlist.header_create(0, text='Date                          ')
        self.hlist.header_create(1, text='Intensity')
        self.hlist.header_create(2, text='Migraine')
        self.hlist.header_create(3, text='Medicine')
        self.hlist.header_create(4, text='Comment')

        # row and column configuration
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)
        self.rowconfigure(5, weight=0)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.columnconfigure(3, weight=0)
        self.columnconfigure(4, weight=0)
        self.columnconfigure(5, weight=0)

        # widget deployment
        self.label_filter.grid(row=0, column=0, sticky=tk.W)
        self.label_reverse.grid(row=0, column=1, sticky=tk.W)
        self.check_reverse.grid(row=0, column=2, sticky=tk.W)
        self.combo_filter.grid(row=0, column=3, sticky=tk.W + tk.E, padx=5)
        self.button_filter.grid(row=0, column=4, sticky=tk.W + tk.E)
        self.hlist.grid(row=1, column=0, sticky=tk.W + tk.E + tk.N + tk.S, columnspan=5)
        self.vscroll_list.grid(row=1, column=5, sticky=tk.N + tk.S)
        self.hscroll_list.grid(row=2, column=0, sticky=tk.W + tk.E, columnspan=6)
        self.button_export_txt.grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.separator.grid(row=4, column=0, stick=tk.W + tk.E, columnspan=6)
        self.label_status.grid(row=5, column=0, stick=tk.W, columnspan=6)

    def double_click(self, entry):
        entry_number = int(entry)
        maintenance_data = self.report_data[entry_number]
        maintenance = Maintenance(db=self.db, master=self, data=maintenance_data)
        maintenance.transient(self)
        maintenance.geometry('600x300')

        if os.name == 'nt':
            maintenance.update_idletasks()
            x = (maintenance.winfo_screenwidth() - maintenance.winfo_reqwidth()) / 2
            y = (maintenance.winfo_screenheight() - maintenance.winfo_reqheight()) / 2
            maintenance.geometry('+%d+%d' % (x, y))

        self.wait_window(maintenance)
        self.search_data()

    def search_data(self):
        self.report_data.clear()
        self.hlist.delete_all()

        if self.check_reverse_dates.get() == 1:
            self.ord = 'DESC'
        else:
            self.ord = 'ASC'

        cursor = None
        if self.filter_value.get()[0] == '1':  # last 31 days
            ago31days = (date.today() + timedelta(days=-31)).isoformat()
            quantity = self.db.execute('select count(*) from headache where date >= ?',
                                       (ago31days,))
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache where date >= ? order by date {ord}'.format(ord=self.ord),
                                     (ago31days,))
            self.label_status.configure(text='Report generated for last 31 days. Returned items: ' + quantity)
        elif self.filter_value.get()[0] == '2':  # this month
            thismonth = date.today().isoformat()[:7]
            quantity = self.db.execute('select count(*) from headache where date >= ?',
                                       (thismonth,))
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache where date >= ? order by date {ord}'.format(ord=self.ord),
                                     (thismonth,))
            self.label_status.configure(text='Report generated for this month. Returned items: ' + quantity)
        elif self.filter_value.get()[0] == '3':  # everything
            quantity = self.db.execute('select count(*) from headache')
            value = quantity.fetchall()
            quantity = str(value[0][0])
            cursor = self.db.execute('select * from headache order by date {ord}'.format(ord=self.ord))
            self.label_status.configure(text='Report generated for all available data. Returned items: ' + quantity)

        current_row = 0

        for i in cursor:

            self.hlist.add(current_row)

            self.report_data.append((i[1], i[2], i[3], i[4], i[5]))
            report_date = i[1]
            report_intensity = str(i[2])
            report_migraine = 'yes' if i[3] == 1 else 'no'
            report_medicine = 'yes' if i[4] == 1 else 'no'

            if i[5] is not None:
                report_comment = i[5][:-1]
            else:
                report_comment = ''

            self.hlist.item_create(current_row, 0, text=report_date)
            self.hlist.item_create(current_row, 1, text=report_intensity)
            self.hlist.item_create(current_row, 2, text=report_migraine)
            self.hlist.item_create(current_row, 3, text=report_medicine)
            self.hlist.item_create(current_row, 4, text=report_comment)

            current_row += 1

        self.button_export_txt.configure(state=tk.NORMAL)
        self.button_export_txt.configure(background=ENABLED_BUTTON_BKGRND)
        self.button_export_txt.flash()

    def export_to_txt(self):
        header = ('*'*self.column_size) + '\n' + '{:*^{}}'.format(' HEADACHE DIARY v' + __init__.version + ' ',
                                                                  self.column_size)
        header += '\n' + ('*'*self.column_size) + '\n\n'
        table_header = '{a:<{width}}{b:>{width}}{c:>{width}}{d:>{width}}\n'.\
            format(a='Date:', b='Intensity:', c='Migraine:', d='Medicine:', width=int(self.column_size/4))
        footer = '{:*>{}}'.format(' Generated in ' + str(str(datetime.now()).split('.')[0]) + ' ***',
                                  self.column_size)
        footer += '\n{:*>{}}'.format(' Copyright (C) 2018 Gidalti Lourenço Junior ***', self.column_size)
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('TXT', '.txt')],
                                            initialfile='my_headache_diary_report', parent=self)

        if path == () or path == '':
            self.label_status.configure(text='Export to txt cancelled by the user.')
        else:
            with open(path, 'w') as file:
                file.write(header)
                file.write(table_header)
                for i in self.report_data:
                    # i[0] = date; i[1] = intensity; i[2] = migraine; i[3] = medicine; i[4] = comments
                    file.write('{a:.<{width}}{b:.>{width}}{c:.>{width}}{d:.>{width}}\n'.
                               format(a=i[0], b=i[1], c=i[2], d=i[3], width=30))
                    if i[4] is not None:
                        report_comment = self.breaklines(i[4], self.column_size)
                        file.write('Comments:\n{e}'.format(e=report_comment))
                        file.writelines('\n')
                file.write(footer)
                self.label_status.configure(text='Report exported to "' + path + '".')

    @staticmethod
    def breaklines(message, column_size):
        if len(message) > column_size:
            array = message.split()
            lenght = -1
            count = -1
            for word in array:
                count += 1
                lenght += len(word) + 1
                if lenght > column_size:
                    array[count - 1] += '\n'
                    lenght = 0
                    lenght += len(array[count]) + 1
            postmessage = ''
            for word in array:
                if str(word).find('\n') < 0:  # if the word has no '\n' then a ' '(empty space) will be added at the end
                    postmessage += word + ' '
                else:  # otherwise, if the word has '\n', then nothing is added
                    postmessage += word
            return postmessage + '\n'  # return the whole message, with all '\n' and ' '(empty spaces) between the words
        else:
            return message


class MainForm(tk.Frame):

    # TODO: create a new database table to keep preferences:
    # - Date format
    # - ASC or DESC Report display
    # - MainForm starts today or yesterday
    # - etc...

    def __init__(self, master=None):
        tk.Frame.__init__(self, master, bg='white')
        self.option_readfile('configuration.tk')

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
        self.previousday = tk.Button(self, text='- 1', command=self.previous_day)
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
        self.button_report = tk.Button(self, name='reportButton', text='Report', command=self.create_report)

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
            self.master.geometry('+%d+%d' % (x, y))

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
        self.rowconfigure(11, weight=0)

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
        self.text_comment.grid(row=8, column=0, sticky=tk.W + tk.E, columnspan=4, padx=5)

        self.button_save.grid(row=9, column=3, sticky=tk.E + tk.W, pady=5, padx=5)
        self.button_report.grid(row=9, column=0, sticky=tk.E + tk.W, pady=5, padx=5)

        self.separator2.grid(row=10, column=0, sticky=tk.E + tk.W, columnspan=4)

        self.label_status.grid(row=11, column=0, sticky=tk.W, columnspan=4)

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
        self.button_save.configure(background=DISABLED_BUTTON_BKGRND)
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
            report.geometry('+%d+%d' % (x, y))

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
            self.button_save.configure(background=DISABLED_BUTTON_BKGRND)
            self.label_status.configure(text='( X ) This date is already fulfilled.')
        elif self.verify_date() is False:
            self.button_save.configure(state=tk.DISABLED)
            self.button_save.configure(background=DISABLED_BUTTON_BKGRND)
            self.label_status.configure(text='( X ) This date is invalid.')
        else:
            self.button_save.configure(state=tk.NORMAL)
            self.button_save.configure(background=ENABLED_BUTTON_BKGRND)

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
        if event is None:
            self.spin_value_day.set(str(int(self.spin_value_day.get())+1))
            self.validate_date()

    def previous_day(self, event=None):
        if event is None:
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
    load_tix = tix.Tk(None, None, 'Headache Diary v' + __init__.version)
    app = MainForm()
    app.mainloop()
