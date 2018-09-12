import os
import sys
from re import sub
import time
from threading import Thread
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from pygtail import Pygtail
from pywinauto import clipboard
from pywinauto.keyboard import SendKeys
from pywinauto.application import Application

from UI.mainwindow import Ui_MainWindow as MainWindow
from UI.piratestats import Ui_Form as PirateStatsWindow
from UI.battlestats import Ui_Form as BattleStatsWindow
from UI.overridecounts import Ui_Form as OverrideCountsWindow
from UI.about import Ui_Form as AboutWindow

greedy_strings = [
    'executes a masterful strike',
    'swings a devious blow',
    'performs a powerful attack',
    'delivers an overwhelming barrage'
]
battle_ended_string = 'as your initial cut of the booty!'
battle_began_string = 'intercepted'
fight_began_string = 'A melee breaks out between the crews!'

pirate_stats_table_headers = [["Pirate", "LL Total", "LL Avg", "TLB", "TTB"]]
battle_stats_table_headers = [["Battle #", "Ship Name", "Total Greedies"]]
version = '3.0'


class GreedyBashCounter(QMainWindow, MainWindow):
    active = False
    total_lls, average_lls, last_battle_lls, this_battle_lls, battle_count = 0, 0, 0, 0, 0
    battle_started, battle_ended, fight_started = False, False, False
    current_battle_ship_name, last_battle_ship_name = "None", "None"
    pirates, battles = {}, {}

    def __init__(self, *args, **kwargs):
        super(GreedyBashCounter, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.settings = QSettings('settings.ini', QSettings.IniFormat)
        self.log_folder = self.settings.value('pp_log_folder')
        if self.log_folder:
            self.load_pirates_menu()
        else:
            self.statusbar.showMessage('Log folder not set')

        if self.settings.value('last_pirate_action_used'):
            last_pirate_used = self.settings.value('last_pirate_action_used')
            self.set_pirate(last_pirate_used)

        # Create sub windows
        self.psw = PirateStats()
        self.bsw = BattleStats()
        self.aw = About()
        self.ow = OverrideCounts()

        # Menu Button Actions
        self.menuOptions.triggered[QAction].connect(self.menu_button_action)
        self.menuLogging.triggered[QAction].connect(self.menu_button_action)
        self.actionLoad_Pirates.triggered.connect(self.load_pirates_menu)


        self.menuPirates.triggered[QAction].connect(self.set_pirate)

        # Regular Button Actions
        self.piratestatsButton.clicked.connect(self.regular_button_action)
        self.battlestatsButton.clicked.connect(self.regular_button_action)
        self.ow.overridefixButton.clicked.connect(self.fix_loss)

        self.show()

    # Actions
    def menu_button_action(self, action):
        menu_action = action.text()

        if menu_action == "About":
            state = self.aw.isVisible()
            if state:
                self.aw.hide()
            else:
                self.aw.show()

        elif menu_action == "Reset":
            self.reset_stats()

        elif menu_action == "Clear This Battle":
            self.clear_this_battle_lls()

        elif menu_action == "Start" and not self.active:
            self.active = True
            self.log_reader_thread = Thread(target=self.read_log)
            print('Starting Logging thread')
            self.actionStart.setEnabled(False)
            self.actionStop.setEnabled(True)
            self.log_reader_thread.start()

        elif menu_action == "Stop" and self.active:
            self.active = False
            print('Stopping Logging Thread')
            self.actionStart.setEnabled(True)
            self.actionStop.setEnabled(False)

        elif menu_action == "Override":
            state = self.ow.isVisible()
            if state:
                self.ow.hide()
            else:
                self.ow.show()

        elif menu_action == "Set Log Folder":
            temp_thread = Thread(target=self.set_log_folder)
            temp_thread.start()

    def regular_button_action(self):
        btn = self.sender().objectName()

        if btn == "piratestatsButton":
            state = self.psw.isVisible()
            if state:
                self.psw.hide()
            else:
                self.psw.show()
        elif btn == "battlestatsButton":
            state = self.bsw.isVisible()
            if state:
                self.bsw.hide()
            else:
                self.bsw.show()

    def menu_about_window_action(self):
        state = self.aw.isVisible()
        if state:
            self.aw.hide()
        else:
            self.aw.show()

    def pirate_stats_window_action(self):
        state = self.psw.isVisible()
        if state:
            self.psw.hide()
        else:
            self.psw.show()

    def load_pirates_menu_thread(self):
        if not self.log_folder:
            self.statusbar.showMessage('Log folder not set')
        else:
            temp_thread = Thread(target=self.load_pirates_menu)
            temp_thread.start()

    def load_pirates_menu(self):
        self.menuPirates.clear()
        log_list = self.get_log_list()
        pirates_and_oceans = [(log.split('_')[0], log.split('_')[1].capitalize()) for log in log_list]

        group = QActionGroup(self.menuPirates)
        for pirate, ocean in pirates_and_oceans:
            action_name = 'action{}_{}'.format(pirate, ocean)
            text = '{} - {}'.format(pirate, ocean)
            action = QAction(text, self.menuPirates, checkable=True)
            action.setObjectName(action_name)
            self.menuPirates.addAction(action)
            group.addAction(action)
        group.setExclusive(True)
        self.menuPirates.addSeparator()
        self.actionLoad_Pirates = QAction(self)
        self.actionLoad_Pirates.setObjectName("actionLoad_Pirates")
        self.menuPirates.addAction(self.actionLoad_Pirates)
        self.actionLoad_Pirates.setText(QCoreApplication.translate("MainWindow", "Load Pirates"))

    def set_log_folder(self):
        print('Getting Log Folder')
        selected_folder = QFileDialog.getExistingDirectory(self, "Select Directory")
        if selected_folder:
            print('Setting Log Folder')
            self.settings.setValue('pp_log_folder', selected_folder)
            self.log_folder = selected_folder
            self.actionLoad_Pirates.triggered.connect(self.load_pirates_menu_thread)

    # Core Functions
    def get_log_list(self):
        file_list = [file for file in os.listdir(self.log_folder)
                     if os.path.isfile(os.path.join(self.log_folder, file))]
        only_log_pirate_files = [file for file in file_list if file.endswith('.log')]

        return only_log_pirate_files

    def set_pirate(self, action):
        try:
            menu_action = action.text()
        except AttributeError:
            menu_action = action

        if menu_action != 'Load Pirates':
            pirate, ocean = menu_action.split(' ')[0], menu_action.split(' ')[2]
            print('Using {} on {}'.format(pirate, ocean))
            self.active = False
            self.actionStart.setEnabled(True)
            self.actionStop.setEnabled(False)
            self.piratenameLabel.setText(pirate)
            self.pirateoceanLabel.setText(ocean)
            self.settings.setValue('last_pirate_action_used', menu_action)
            all_actions = self.menuPirates.actions()
            for a in all_actions:
                if a.isChecked() and a.text() != menu_action:
                    a.setChecked(False)

    def individual_pirate_stat(self, pirate):
        print('Updating Individual Pirate Stat for {}'.format(pirate))
        if not self.pirates.get(pirate):
            print('Creating Pirate Dictionary')
            self.pirates[pirate] = {
                'll_this_battle': 0,
                'll_total': 0,
                'll_average': 0,
                'll_last_battle': 0
            }
        self.pirates[pirate]['ll_this_battle'] = self.pirates[pirate]['ll_this_battle'] + 1
        print('New LL count for {} is {}'.format(pirate, self.pirates[pirate]['ll_this_battle']))
        refresh_pirate = Thread(target=self.refresh_pirate_stats_table)
        refresh_pirate.start()

    def log_parser(self, lines):
        if lines:
            line_list = lines.split('\n')
            try:
                line_list.remove('')
            except ValueError:
                pass
            sanitized_lines = [sub('^\[..:..:..\] ', '', line) for line in line_list]

            for line in sanitized_lines:
                if battle_began_string in line:
                    self.battle_started = True
                    self.battle_ended = False
                    self.current_battle_ship_name = ' '.join(line.split(' ')[-2:]).replace('!', '')
                    print(self.current_battle_ship_name)
                    self.thisshipdisplayLabel.setText(self.current_battle_ship_name)
                    print('Battle Started')
                elif fight_began_string in line:
                    self.fight_started = True
                    print('Fight Started')
                elif battle_ended_string in line:
                    self.battle_ended = True
                    self.battle_started = False
                    self.fight_started = False
                    print('Battle Ended')

            greedy_sanitized_lines = [line for line in sanitized_lines if any(s for s in greedy_strings if s in line)]
            return greedy_sanitized_lines

    def read_log(self):
        log_list = self.get_log_list()
        active_pirate, ocean = self.piratenameLabel.text(), self.pirateoceanLabel.text().lower()
        active_pirate_log = [pirate for pirate in log_list if pirate.startswith('{}_{}'.format(active_pirate, ocean))]
        log_file = os.path.join(self.log_folder, active_pirate_log[0])
        print('Reading log from: {}'.format(log_file))
        pygtail = Pygtail(log_file, read_from_end=True)
        while self.active:
            raw_lines = pygtail.read()
            time.sleep(.5)
            if raw_lines:
                lines = self.log_parser(raw_lines)
                if lines:
                    for line in lines:
                        pirate = line.split(' ')[0]
                        self.this_battle_lls = self.this_battle_lls + 1
                        self.thisbattlelavishlockersLCD.display(self.this_battle_lls)
                        self.individual_pirate_stat(pirate)


                if self.battle_ended:
                    update_stats = Thread(target=self.update_major_stats)
                    update_stats.start()


    def reset_stats(self):
        print('Resetting Stats')
        self.total_lls = 0
        self.average_lls = 0
        self.last_battle_lls = 0
        self.this_battle_lls = 0
        self.battle_count = 0
        self.current_battle_ship_name = "None"
        self.last_battle_ship_name = "None"

        self.totallavishlockersLCD.display(self.total_lls)
        self.lastbattlelavishlockersLCD.display(self.last_battle_lls)
        self.averagelavishlockersLCD.display(self.average_lls)
        self.battlesLCD.display(self.battle_count)
        self.thisbattlelavishlockersLCD.display(self.this_battle_lls)
        self.lastshipdisplayLabel.setText(self.last_battle_ship_name)
        self.thisshipdisplayLabel.setText(self.current_battle_ship_name)


        self.pirates, self.battles = {}, {}
        refresh_pirate = Thread(target=self.refresh_pirate_stats_table)
        refresh_pirate.start()
        refresh_battle = Thread(target=self.refresh_battle_stats_table)
        refresh_battle.start()
        print('Stats Reset')

    def update_major_stats(self):
        self.battle_count = self.battle_count + 1
        self.last_battle_lls = self.this_battle_lls
        self.total_lls = self.total_lls + self.this_battle_lls
        self.average_lls = round(self.total_lls / self.battle_count, 1)
        self.this_battle_lls = 0
        self.last_battle_ship_name = self.current_battle_ship_name
        self.current_battle_ship_name = "None"
        self.totallavishlockersLCD.display(self.total_lls)
        self.lastbattlelavishlockersLCD.display(self.last_battle_lls)
        self.averagelavishlockersLCD.display(self.average_lls)
        self.battlesLCD.display(self.battle_count)
        self.thisbattlelavishlockersLCD.display(self.this_battle_lls)
        self.lastshipdisplayLabel.setText(self.last_battle_ship_name)
        self.thisshipdisplayLabel.setText(self.current_battle_ship_name)
        self.battle_ended = False

        for pirate in self.pirates:
            self.pirates[pirate]['ll_total'] = self.pirates[pirate]['ll_total'] + \
                                               self.pirates[pirate]['ll_this_battle']
            self.pirates[pirate]['ll_last_battle'] = self.pirates[pirate]['ll_this_battle']
            self.pirates[pirate]['ll_this_battle'] = 0
            self.pirates[pirate]['ll_average'] = round(self.pirates[pirate]['ll_total'] / self.battle_count, 1)

        self.battles[self.battle_count] = {
            'ship': self.last_battle_ship_name,
            'greedies': self.last_battle_lls
        }
        refresh_pirate = Thread(target=self.refresh_pirate_stats_table)
        refresh_pirate.start()
        refresh_battle = Thread(target=self.refresh_battle_stats_table)
        refresh_battle.start()

    # SubWindow Functions
    def clear_this_battle_lls(self):
        self.this_battle_lls = 0
        self.thisbattlelavishlockersLCD.display(self.this_battle_lls)

    def fix_loss(self):
        self.total_lls = self.ow.lavishlockeroverrideSpinBox.value()
        self.battle_count = self.ow.battleoverrideSpinBox.value()
        self.totallavishlockersLCD.display(self.total_lls)
        self.battlesLCD.display(self.battle_count)
        self.ow.hide()

    def refresh_pirate_stats_table(self):
        table = self.psw.tableWidget
        table.setRowCount(0)
        print('Refreshing pirate stats table')
        for row_id, pirate in enumerate(self.pirates.keys()):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QTableWidgetItem(str(pirate)))
            table.setItem(row_id, 1, QTableWidgetItem(str(self.pirates[pirate]['ll_total'])))
            table.setItem(row_id, 2, QTableWidgetItem(str(self.pirates[pirate]['ll_average'])))
            table.setItem(row_id, 3, QTableWidgetItem(str(self.pirates[pirate]['ll_last_battle'])))
            table.setItem(row_id, 4, QTableWidgetItem(str(self.pirates[pirate]['ll_this_battle'])))

    def refresh_battle_stats_table(self):
        table = self.bsw.battlestatsTable
        table.setRowCount(0)
        print('Refreshing battle stats table')
        for row_id, battle_num in enumerate(self.battles.keys()):
            table.insertRow(row_id)
            table.setItem(row_id, 0, QTableWidgetItem(str(battle_num)))
            table.setItem(row_id, 1, QTableWidgetItem(str(self.battles[battle_num]['ship'])))
            table.setItem(row_id, 2, QTableWidgetItem(str(self.battles[battle_num]['greedies'])))

    # Send To Puzzle Pirates Functions
    def send_pirate_stats(self, row_id):
        row_data = self.app.getTableRow('PirateStats', row_id)
        active_pirate_info = str(self.app.getLabel('PirateNameDisplay')).split(' ')
        title_re = 'Puzzle Pirates - {} on the {} ocean'.format(active_pirate_info[0], active_pirate_info[2])
        formatted_data = 'Pirate: {}, Total LLs: {}, Average LLs: {},' \
                         ' Total Last Battle: {}'.format(row_data[0], row_data[1], row_data[2], row_data[3])
        self.app.info(formatted_data)
        pp_frame = Application().connect(title_re=title_re)
        window = pp_frame.window()
        window.set_focus()
        clipboard.EmptyClipboard()
        clipboard.win32clipboard.OpenClipboard()
        clipboard.win32clipboard.SetClipboardText(formatted_data)
        clipboard.win32clipboard.CloseClipboard()
        SendKeys('+{INS}')
        SendKeys('{ENTER}')

    def send_totals(self):
        formatted_data = 'Total LLs: {}, Average LLs: {}, ' \
                         'LLs Last Battle: {}, Battles: {}'.format(self.total_lls, self.average_lls,
                                                                   self.last_battle_lls, self.battle_count)
        self.app.info(formatted_data)
        active_pirate_info = str(self.app.getLabel('PirateNameDisplay')).split(' ')
        title_re = 'Puzzle Pirates - {} on the {} ocean'.format(active_pirate_info[0], active_pirate_info[2])
        pp_frame = Application().connect(title_re=title_re)
        window = pp_frame.window()
        window.set_focus()
        clipboard.EmptyClipboard()
        clipboard.win32clipboard.OpenClipboard()
        clipboard.win32clipboard.SetClipboardText(formatted_data)
        clipboard.win32clipboard.CloseClipboard()
        SendKeys('+{INS}')
        SendKeys('{ENTER}')


class PirateStats(QWidget, PirateStatsWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class BattleStats(QWidget, BattleStatsWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class About(QWidget, AboutWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


class OverrideCounts(QWidget, OverrideCountsWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gbc = GreedyBashCounter()
    app.exec()
