import threading
import time
import serial
import serial.tools.list_ports
import PySimpleGUI as sg
import psycopg2
import requests as req
import config as konfiguracja
import pickle

konfiguracja.ConfigLoadFile("settings.ini")
MainSettings = konfiguracja.UnpackSection('main')
Powitanie = MainSettings["welcome_msg"]
THREAD_EVENT = '-THREAD-'

try:
    ser = serial.Serial(
        MainSettings["serial_dev_add"], MainSettings["serial_dev_br"], timeout=1)
    s_on = True
except:
    s_on = False


def SaveToDisk(self, filename):
    try:
        results = _BuildResults(self, False, self)
        with open(filename, 'wb') as sf:
            pickle.dump(results[1], sf)
    except:
        print('*** Error saving form to disk ***')


def the_thread(window):

    if s_on:
        sg.cprint(time.asctime(), end=' (System) - ')
        sg.cprint((MainSettings["serial_dev_add"] + " (Połączono)"))
        window.TKroot.title(MainSettings["serial_dev_add"] + " (Połączono)")
    else:
        sg.cprint(time.asctime(), end=' (System) - ')
        sg.cprint(("Nie mozna polaczyc z -"+MainSettings["serial_dev_add"]))
        window.TKroot.title(
            MainSettings["serial_dev_add"] + " (Brak połączenia)")
    while s_on:
        # time.sleep(0.1)
        serBarCode = ser.readline()

        if len(serBarCode) > 0:
            Odczytana = serBarCode.decode("utf-8")
            window.write_event_value('-THREAD-', (Odczytana.rstrip()))

    if s_on:
        ser.close()


def new_thread(window):
    T = threading.Thread(target=the_thread, args=(window,), daemon=True)
    T.start()
    return T


def main():
    sg.theme('Dark brown')

###################################################### LISTA ULUBIONYCH ######################################################

    fav_list = konfiguracja.LoadList("fav.txt")

    tabfav_layout = [
        [sg.Listbox(fav_list, size=(15, 20), enable_events=True, key='-LISTFAV-')
         ], [sg.B('+', size=(4, 1)), sg.B('-', size=(4, 1))]
    ]

###################################################### LISTA HISTORIA ######################################################
#

    list_his = konfiguracja.LoadList("his.txt")

    tabhis_layout = [
        [sg.Listbox(list_his, size=(15, 20), enable_events=True,
                    key='-LISTHIS-')], [sg.B('Skasuj', size=(13, 1))]
    ]

################################################# ZAKŁADKI ULUBIONE / HISTORIA ######################################################

    tab_his_layout = [[sg.Tab('Ulubione', tabfav_layout, font='Courier 15', key='-TABFAV1-'),
                       sg.Tab('Historia', tabhis_layout, key='-TABHIS2-'),

                       ]]

################################################# GŁOWNE ZAKŁADKI ######################################################
    tab1_layout = [
        [sg.Text('SERek Commander v0.11b', font='Verdana 20')],
        [sg.Multiline(size=(100, 25), key='-ML-', font=('Verdana', 9), enable_events=True, disabled=True, autoscroll=True, reroute_stdout=True, write_only=True, reroute_cprint=True),
         sg.TabGroup(tab_his_layout, enable_events=True, key='-TABGROUP2-')],
        [sg.Input(key='-IN-', size=(120, 1)),
         sg.B('>>', bind_return_key=True)],
        [sg.Button('Koniec'), sg.Button('Połącz')],

    ]

    porty_full = serial.tools.list_ports.comports()
    porty = [row[0] for row in porty_full]

    tab2_layout = [[sg.Text('Dane konfiguracyjne - settings.ini')],
                   [sg.Text('Urządzenie:', size=(15, 1), text_color="orange"), sg.InputCombo(
                       porty, default_value=MainSettings["serial_dev_add"], key='-DA-', size=(50, 1))],
                   [sg.Text('Baud-rate:', size=(15, 1), text_color="orange"), sg.Input(
                       default_text=MainSettings["serial_dev_br"], key='-PA-', size=(50, 1))],
                   [sg.Button('Zapis')]

                   ]

    tab3_layout = [[sg.Text('Tab 3')]]
    tab4_layout = [[sg.Text('Tab 3')]]
    

    tab_group_layout = [[sg.Tab('Konsola', tab1_layout, font='Courier 15', key='-TAB1-'),
                         sg.Tab('Ustawienia', tab2_layout,
                                visible=True, key='-TAB2-'),
                         sg.Tab('Tab 3', tab3_layout, key='-TAB3-'),
                         sg.Tab('Tab 4', tab4_layout,
                                visible=False, key='-TAB4-'),
                         ]]

    layout = [[sg.TabGroup(tab_group_layout,
                           enable_events=True,
                           key='-TABGROUP-')]]

    window = sg.Window(MainSettings["serial_dev_add"], layout).Finalize()

################################################# KONIEC SEKCJI WYGLĄDU ######################################################

    T = new_thread(window)
    sg.cprint(time.asctime(), end=' (System) - ')
    sg.cprint(Powitanie)

    while True:
        event, values = window.read()

        if event == sg.WIN_CLOSED or event == 'Koniec':
            konfiguracja.SaveList(fav_list, "fav.txt")
            konfiguracja.SaveList(list_his, "his.txt")
         #   with open("logi.txt", 'w') as f:
              #  f.write(values['-ML-'][0])
            # T.join()
           # ser.close()
            break

        if event == THREAD_EVENT:
            sg.cprint(time.asctime(), end=' (RX) - ')
            sg.cprint(values[THREAD_EVENT])

        if event.startswith('Zapis'):
            konfiguracja.ConfigItem('main', 'serial_dev_add', values['-DA-'])
            konfiguracja.ConfigItem('main', 'serial_dev_br', values['-PA-'])
            konfiguracja.ConfigSave()

        if event.startswith('Ulubione'):
            window['-LISTFAV-'].update(enable_events=True)

        if values['-LISTFAV-']:
            window['-IN-'].update(values['-LISTFAV-'][0])

        if values['-LISTHIS-']:
            window['-IN-'].update(values['-LISTHIS-'][0])

        if event == '+':
            if (not values['-IN-'] in fav_list) and (values['-IN-'] != ""):
                fav_list.append(values['-IN-'])
                window['-LISTFAV-'].update(fav_list)

        if event == 'Skasuj':

            list_his.clear()
            window['-LISTHIS-'].update(list_his)

        if event == '-':
            if values['-IN-'] in fav_list:
                if not fav_list.count == 0:
                    try:
                        fav_list.remove(values['-LISTFAV-'][0])
                        window['-LISTFAV-'].update(fav_list)
                    except:
                        pass

        if event.startswith('>>'):
            if s_on:
                if not values['-IN-'] == "":
                    IN = '-IN-'
                    sg.cprint(time.asctime(), end=' (TX) - ')
                    sg.cprint(f' {values[IN]} ', colors='lime on black')
                    ser.write(values[IN].encode())
                    list_his.append(values['-IN-'])
                    window['-LISTHIS-'].update(list_his)
                    window['-IN-'].update("")
            else:
                sg.cprint(time.asctime(), end=' (System) - ')
                sg.cprint("Jesteś offline.")

    window.close()


if __name__ == '__main__':
    main()
