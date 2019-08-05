import os
from subprocess import Popen
import json 
from os import listdir
import ctypes
from ctypes import c_char_p
import sys

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
    

def main():
    # check arguments
    # for arg in sys.argv[1:]:
    if(len(sys.argv) != 2):
        print("Wrong number of arguments .. entered (",len(sys.argv),")")
        # print(sys.argv, file=sys.stderr)
        print("Usage (",sys.argv[0],"): <data file name>")
        sys.exit(1)

    table_name = os.path.abspath(sys.argv[1]);
    
    # print(table_name)
    executeFahes(table_name)
    



if __name__ == "__main__":
    main()
