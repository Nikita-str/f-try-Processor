from opcodes import *;
from registers import *;
from  cmd_parse import cmd_handler;
from  cmd_parse import get_cmd_prefix;

import sys

def ASM_to_PCode(path_from, path_to = "p.#code#"):
    try:
        asm_file = open(path_from, "r");
    except:
        print("path to asm file is bad");
        return 1
    try:
        pcode_file = open(path_to, "wb");
    except:
        print("path to pcode file is bad  -______-")
        print("[mentioned in path folders must exist]");
        return 1;
    
    reg_init()
    global regs_index;
    
    line = asm_file.readline();
    ind_line = 1;
    while line:
        line = line.strip()
        line = line.split(';')[0]
        line = line.split('//')[0]
        if(len(line) == 0):
            line = asm_file.readline();
            ind_line+=1;
            continue;

        str_param = line.split('"')
        len_str_param = len(str_param)
        line = str_param[0]
        if(len_str_param != 3 and len_str_param != 1):
            print("string error: "+ line+"  line: " + str(ind_line))
            print('in one line may stay only 0 or 2 char ["] ')
            return 1;
        if(len_str_param == 3 and len(str_param[2].replace(' ','')) != 0):
            print("string error: "+ line+"  line: " + str(ind_line))
            print('after string may stay only comment')
            return 1;
        
        line = line.split(' ');
        if(len_str_param == 3): line += ['"' + str_param[1] + '"']
        cmd = []
        #pass empty str and make upper that need make upper:
        for x in line:
            if(len(x) == 0): continue;
            if(x[0] != '"'): x = x.upper()
            cmd += [x]

        cmd_name = cmd[0]
        operands = cmd[1:]
        func = cmd_handler.get(cmd_name)
        if(not func):
            cmd_prefix = get_cmd_prefix(cmd_name)
            if(not cmd_prefix[0]):
                print("not such command: " + str(cmd_name)+"  line: " + str(ind_line))
                return 1;
            cmd_prefix = cmd_prefix[1]
            func = cmd_handler.get(cmd_prefix)
            line_res = func(operands, cmd_name)
        else:
            line_res = func(operands, "");
        if(line_res.valid == False):
            print("error:    cmd: "+str(cmd_name) + "   line: "+str(ind_line))
            print(line_res.why_invalid)
            return 1;
        pcode_file.write(bytearray(line_res.v_bytes))
            
        line = asm_file.readline();
        ind_line+=1;

    pcode_file.write(bytearray(  cmd_handler['HLT']([]).v_bytes ))#ADD HLT IN END
    pcode_file.close()
    asm_file.close()
    return 0;

len_arg = len(sys.argv)
ret_val = 0
if(len_arg == 1): ret_val = ASM_to_PCode('')
if(len_arg == 2): ret_val = ASM_to_PCode(sys.argv[1])
if(len_arg > 2): ret_val = ASM_to_PCode(sys.argv[1], sys.argv[2])
if(ret_val != 0):
    print('some error occurred during assembling to pcode')
else:
    print('\nassembling DONE')
