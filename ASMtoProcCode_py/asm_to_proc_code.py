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
        print("path to pcode file is bad  -______-");
        return 1;
    
    reg_init()
    global regs_index;
    
    line = asm_file.readline();
    ind_line = 1;
    while line:
        line = line.strip()
        line = line.split(';')[0]
        if(len(line) == 0):
            line = asm_file.readline();
            ind_line+=1;
            continue;
        line = line.upper()
        line = line.split(' ');
        cmd = []
        #pass empty str:
        for x in line:
            if(len(x) == 0): continue;
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
