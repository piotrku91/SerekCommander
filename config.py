#!/usr/bin/python
from configparser import ConfigParser

parser = ConfigParser()
Collect = {}
is_Loaded= False

def ConfigLoadFile(filename='settings.ini'):
    parser.clear
    parser.read(filename)
    return 1

def UnpackSection(section=''):
    if parser.has_section(section):
        params = parser.items(section)
        Collect = {}
        for param in params:
            Collect[param[0]] = param[1]
        
    else:
        raise Exception('No section - {0} in the file'.format(section))
   
    return Collect

def ConfigItem(section='main',item='',value=''):
    parser[section][item] = value
    return 1

def ConfigSave(filename='settings.ini'):
    
    with open(filename, 'w') as configfile:
        parser.write(configfile)    
    return 1



def SaveList(Lista,ListFilename,EOL=""):
    try:
        my_file = open(ListFilename, "w")
        my_file.writelines("%s\n" % item.rstrip() for item in Lista)
        my_file.close()
    except:
        my_file.close()
        return 0

    return 1

def LoadList(ListFilename):
    try:
        my_file = open(ListFilename, "r")
        tmplist = my_file.readlines()
    except:
        tmplist=['default']
    my_file.close() 

    return tmplist




