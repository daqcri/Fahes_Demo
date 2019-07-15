import os
from subprocess import Popen
import json 
from os import listdir
import ctypes
from ctypes import c_char_p

global tool_loc
tool_loc = "./fahes_service/"



def executeFahes(input_table): 
    out_dir = 'Fahes_Results/'
    
    output_dir = ""
    # print("Out directory (", out_dir, ")")
    if out_dir:
        output_dir = os.path.join(os.getcwd(), out_dir)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    tName = os.path.join(os.getcwd(), input_table)
    callFahes(input_table, output_dir)
    tab_name = input_table[input_table.rindex('/')+1: len(input_table)]
    tab_name = tab_name.replace('.csv', '.json')
    dmvs_table_name = os.path.join(output_dir, 'DMV_' + tab_name)
    return dmvs_table_name
                    
        
        

def callFahes(tab_full_name, output_dir):
    global tool_loc
    g_path = os.path.abspath(tool_loc)
    path = ""
    if not g_path.endswith('/'):
        path = g_path + "/libFahes.so"
    else:
        path = g_path + "libFahes.so"

    tab_name = c_char_p(tab_full_name.encode('utf-8'))
    out_dir = c_char_p(output_dir.encode('utf-8'))
    Fahes=ctypes.cdll.LoadLibrary(path)
    Fahes.execute(tab_name, out_dir)
    


