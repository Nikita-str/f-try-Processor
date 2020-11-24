#from opcodes import *;
from registers import reg_init
from  cmd_parse import cmd_handler
from  cmd_parse import get_cmd_prefix

from values import is_num, is_fnum, is_reg, f_value_to_byte, value_to_byte, valid_name, check_value, NOT_REG
from variable_types import get_variable_type, ALL_VAR_TYPES, SCALAR_VAR_TYPES, TypeofName, TypeofNameAction

from class__asm_name import asm_name

from global_variable import check_name, name_substitute, exist_expected_names, print_all_expected_names, get_pcode_size

import config

import sys

# + + + CONSTS + + + ###################
VAR__ONE = -1#one may be only local var
VAR__LOC = 0
VAR__GLOB = 1
# - - - CONSTS - - - ###################

class LineType:#lt
    PASS = -5
    CODE_OR_VAR = -3
    ERROR = -2
    END = -1   # if label in end it's ok, i.e. after it will stay HLT and it can use as 'goto END'

    CODE = 0
    SECTION = 1
    LABEL = 2
    FUNC = 3
    VAR = 4
    ONE_LINE_VAR = 5
    back_line_type = PASS

    @staticmethod
    def upd_line_type(now_line_type):
        #return None #TODO:MOVE line_type check here
        if(LineType.back_line_type == now_line_type): return None
        if(LineType.back_line_type == LineType.PASS): pass
        elif(LineType.back_line_type == LineType.CODE): pass #TODO:add jump if need
        elif(LineType.back_line_type == LineType.LABEL):
            if(now_line_type == LineType.SECTION):
                print('error: after label cant stay section')
                return LineType.ERROR
        elif(LineType.back_line_type == LineType.FUNC):
            if(now_line_type == LineType.SECTION):
                print('error: after function cant stay section (in future it will warning with JUMP CMD add)') #TODO:WARING with adding jump cmd
                return LineType.ERROR
        elif(LineType.back_line_type == LineType.VAR):
            if(now_line_type not in [LineType.SECTION, LineType.END]):
                print('error: after var section may stay only other section')
                if(now_line_type == LineType.FUNC):print('but there function defenition')
                if(now_line_type == LineType.LABEL):print('but there label defenition')
                return LineType.ERROR
            pass

        LineType.back_line_type = now_line_type
        return None

# order of []_parse function in this file:
#    1: section_parse
#    2: var_parse
#    3: code_parse
#    4: func_parse
#    5: label_parse

def del_comment(line):
    r = line.strip()
    r = r.split(';')[0]
    r = r.split('//')[0]
    return r

def create_header(path):#TODO:we need to create header for .#pcode# executable file.
    #it need for compiler/os but not for processor so out it in other file .#pocde# -> .#PARSE_HEADER#
    #first 4byte is - version(for test -5 it is 0(i.e. there is no one section))
    header_file = open(path, "wb")
    
    #version 1:
        #VERSION [4 bytes]
        #BYTE ENTRY POINT [4 bytes]
        #SIZE OF PROGRAM [4 bytes]
        #SIZE OF LEN OF NAME ENTRY POINT[4 bytes] = x_1
        #ENTRY POINT NAME[x_1 bytes]
    header_file.write(create_header.version.to_bytes(4, 'little'))#VERSION

    name_entry_point = config.parse_info['entry_point']
    entry_point_in = 0
    if name_entry_point:
        aname = check_name(name_entry_point)
        entry_point_in = aname.get_value_ptr()

    header_file.write(entry_point_in.to_bytes(4, 'little'))#BYTE ENTRY POINT

    header_file.write(get_pcode_size().to_bytes(4, 'little'))#SIZE OF PROGRAM

    if name_entry_point:
        len_of_entry_name = len(name_entry_point)
        header_file.write(len_of_entry_name.to_bytes(4, 'little'))
        name_byte = bytearray(); name_byte.extend(map(ord, name_entry_point))
        header_file.write(name_byte)
    else:
        zero = 0
        header_file.write(zero.to_bytes(4, 'little'))
    #end: version 1

    header_file.close()
    return
create_header.version = 1

def type_of_line(line):
    c = line[0]
    if(c == '.'):return LineType.LABEL
    if(c == '='):return LineType.SECTION
    if(c=='+' or c=='-' or c=='!'):return LineType.FUNC
    return LineType.CODE_OR_VAR

def add_hlt(pcode_file):
    pcode_file.write(bytearray(  cmd_handler['HLT']([]).v_bytes ))

def pre_continue():
    config.line = config.asm_file.readline(); config.ind_line+=1
        
#######################################
##
#        SECTION PARSE
#
def section_parse(): #TODO:VRODE VSE OK

    while config.line:
        config.line = del_comment(config.line)
        if(len(config.line) == 0): pre_continue(); continue
        is_section = (config.line[0] == '=')
        if(is_section):
            if LineType.upd_line_type(LineType.SECTION): return LineType.ERROR

            section_name = config.line[1:]
            i = section_name.find(':')
            if(i == -1):print('after section name should be ":"  (line: '+str(config.ind_line)+')'); return LineType.ERROR
            section_name=section_name[0:i]
            config.line = config.line[i+2:]

            #one-line section(s):
            if(section_name == 'var'): return (LineType.VAR, VAR__ONE)

            #many-line sections:
            if(len(config.line)!=0):print("error: if section is not 'var' then after ':' may be only comment"); return LineType.ERROR
            pre_continue()
            if(section_name in ['vars','-vars']): return (LineType.VAR, VAR__LOC)
            if(section_name == '+vars'): return (LineType.VAR, VAR__GLOB)
            if(section_name == 'code'): return LineType.CODE

            #error such section not exist!:
            print('such section: "'+section_name+'" not exist    (line:'+str(config.ind_line)+')')
            return LineType.ERROR
        else: return LineType.CODE #section of code
                
        pre_continue()

    #no:asm_file.seek(0)#go to start of file
    return LineType.END

#######################################
##
#        VAR PARSE
#
def var_parse(var_section_type):
    #global parse_info, asm_file, pcode_file, line, ind_line

    if(var_section_type == VAR__GLOB): name_type = 'glob_vars'; local = False
    else: name_type = 'loc_vars'; local = True

    if(len(config.line) == 0 and var_section_type == VAR__ONE):
        print('var section must be not empty one-line section!')
        print('=var: var_name VAR_TYPE value[, ..., value]')
        return LineType.ERROR        
    
    while config.line:
        #var_name var_type value[, ..., value]
        line = del_comment(config.line)
        if(len(line) == 0):
            if(var_section_type == VAR__ONE):
                print('var section must be not empty one-line section!  (line: '+str(config.ind_line)+')')
                return LineType.ERROR
            pre_continue()
            continue
        line_type = type_of_line(line)
        
        if var_section_type == VAR__ONE:
            if LineType.upd_line_type(LineType.ONE_LINE_VAR): return LineType.ERROR
        elif LineType.upd_line_type(LineType.VAR): return LineType.ERROR

        if(line_type != LineType.CODE_OR_VAR):
            if(var_section_type != VAR__ONE):return line_type
            print('error: in (one-line)var section must be only one variable definition.')
            print('       line:'+ str(config.ind_line)+'   content: '+line)
            return LineType.ERROR

        #line separate on ?tokens?:
        cstr_in_line = line.split('"')
        if(len(cstr_in_line)%2 == 0):
            print('error " in the  line: '+str(config.ind_line)+'  with content: '+line)
            return LineType.ERROR
        
        words = []
        for w in cstr_in_line[0].split(' '):#TODO:NOW:ONLY ONE LINE DEFINITION OF VAR(and ARRAY !!)
            if(len(w)==0):continue
            words+=[w]
            
        for i in range(1, len(cstr_in_line)):
            if(i%2 == 0):continue #TODO:CHECK:',' BETWEEN cstr  AND last ','
            words+=['"'+cstr_in_line[i]+'"']

        #delete ',' after var_values except last:
        for i in range(2,len(words)-1):
            if(words[i][len(words[i])-1]==','):words[i]=words[i][0:len(words[i])-1]
                
        if((len(words) < 3)):
            print('error: var difinition must has the form like: name TYPE value[, ..., value]')
            print('       line: '+str(config.ind_line)+'  content: '+line)
            return LineType.ERROR 

        var_name = words[0]
        check = valid_name(var_name)
        if check[0] == TypeofNameAction.ERROR:
            print('error: name is not valid   name:'+var_name+'   line:'+str(config.ind_line))
            print(check[1])
            return LineType.ERROR     
        if(check_name(var_name) != None):
            print('error: name '+var_name+' already used   line:'+str(config.ind_line))
            return LineType.ERROR

        var_type_initial, var_type = get_variable_type(words[1])
        var_values = words[2:]

        v_bytes = []
        name_for_subst = None #what name we will check and substitute if it used before  
        arr_len = None #or [0/1]? then LEN(scalar)=[0/1]... no, think error is better

        #+++help func+++ ###  ###  ###  ###
        def vp_int_get(x, int_sz):#vp mean var_parse;  x - str value
            nonlocal v_bytes, var_type_initial
            val = is_num(x)
            if(not val[0]):
                print('error: '+x+' is not a int.')
                return False
            val = val[1]
            if(check_value(val, int_sz)):
                print('error: too big int: '+x+' for '+var_type_initial+' type')
                return False
            v_bytes += value_to_byte([], val, int_sz)#TODO:CHECK
            return True
        
        def vp_double_get(x):#vp mean var_parse;  x - str value
            nonlocal v_bytes
            val = is_fnum(x)
            if(not val[0]):
                print('error: '+x+' is not a double.')
                return False
            val = val[1]
            v_bytes += f_value_to_byte([], val)#TODO:CHECK
            return True
        
        def vp_cstr_get(x):
            nonlocal v_bytes
            c_str = x.replace('\\n', '\n')
            len_str = len(c_str)
            if(c_str[0] != '"' or c_str[len_str - 1] != '"'):
                print('''error: value for CSTR variable must started and ended with " symbol''')
                return False
            c_str = c_str[1:(len_str - 1)]
            len_str -= 2
            if(len_str > 255):
                print('too big string(max 255 symbols): "'+c_str+'"')
                return False
            v_bytes+=[len_str]
            for c in c_str:
                ord_c = ord(c)
                if(ord_c > 255 or ord_c < 0):
                    print('error char: '+c+' code of char must be in [0,255]')
                    return False
                v_bytes += [ord_c]
            return True
        #---help func--- ###  ###  ###  ###

        if(var_type not in ALL_VAR_TYPES):
            print('error: not such type: '+var_type+'   line:'+str(config.ind_line))
            return LineType.ERROR

        if(var_type in SCALAR_VAR_TYPES):
            if(len(var_values) != 1):
                print ('error: too many values('+str(len(var_values))+') for '+var_type+' var')
                print('need one value.   values: '+str(var_values))
                return LineType.ERROR
        
        if(var_type[0:3] == 'INT'):#INT
            int_sz = int(var_type[3:])
            if(not vp_int_get(var_values[0], int_sz)):return LineType.ERROR
        elif(var_type[0:4] == 'IARR'):#INT ARRAY
            arr_len = len(var_values)
            int_sz = int(var_type[4:])
            for x in var_values:
                if(not vp_int_get(x, int_sz)):return LineType.ERROR
        elif(var_type == 'DOUB'):#DOUBLE
            if(not vp_double_get(var_values[0])):return LineType.ERROR
        elif(var_type == 'DARR'):#DOUBLE ARRAY
            arr_len = len(var_values)
            for x in var_values:
                if(not vp_double_get(x)):return LineType.ERROR
        elif(var_type == 'CSTR'):#C STRING
            if(not vp_cstr_get(var_values[0])):return LineType.ERROR
        else:#._.
            print('kawo? .-. something weird happen  (did not implement type'+var_type+')')
            return LineType.ERROR

        name_for_subst = asm_name(var_name, config.pcode_file.tell(), TypeofName.var, local, var_type, arr_len)#TODO:CHECK:file.tell()
        if(len(v_bytes)==0):# or name_for_subst==None):
            print('error (or maybe not ... im not sure actually,  heh)    line:'+str(config.ind_line))
            return LineType.ERROR
        config.pcode_file.write(bytearray(v_bytes))#TODO:CHECK
        name_substitute(name_for_subst)
        config.parse_info[name_type] += [name_for_subst]
        pre_continue()
        if(var_section_type == VAR__ONE):return LineType.SECTION #TODO:OR:MAYBE:LINE_TYPE__CODE

    return LineType.END

#######################################
##
#        CODE PARSE
#
def cmd_line_normalization(line, to_upper = [0]):
    now_cmd = ''
    back_space = True
    string_in = False
    open_ptr = 0
    open_act = 0
    comma = 0
    ret = []
    ind = 0
    n_cmd = 0
    ptr_in_row = 0
    def __help_ret_add():
        nonlocal n_cmd, ret, now_cmd, to_upper
        if not back_space: 
            nc_upper = now_cmd.upper()
            if n_cmd in to_upper: now_cmd = nc_upper
            elif is_reg(nc_upper)[0] != NOT_REG: now_cmd = nc_upper
            ret += [now_cmd]
            now_cmd = ''
            n_cmd += 1

    def __help_set_zero():
        nonlocal comma, ptr_in_row, back_space
        comma = 0; ptr_in_row = 0; back_space = False 

    for c in line:
        if c=='"': 
            __help_set_zero() 
            string_in = not string_in; now_cmd += c; continue
        if string_in: now_cmd += c; continue


        if open_ptr == 0 and c in [' ', ',']:
            if not back_space: 
                __help_ret_add()
                ind += 1
                back_space = True
            if c == ' ':continue
            comma += 1
            if n_cmd == 0:
                print("error: line cant start with ','") 
                return LineType.ERROR 
            if n_cmd == 1:
                print("error: after command not may ','") 
                return LineType.ERROR 
            if comma > 1:
                print("error: twice in a row stay ','")  
                return LineType.ERROR 
            continue 
        else: __help_set_zero()

        if c == '[':
            open_ptr += 1
            ptr_in_row += 1
            if open_ptr > 1:
                print("error: nested ptr('[')")  
                return LineType.ERROR  
            if ptr_in_row > 1:
                print("error: between pointers is needed a separator{',', ' '}    it wrong:'[...][...]'")  
                return LineType.ERROR  
            now_cmd += c
            ind += 1
        elif c ==']':
            open_ptr -= 1
            if open_ptr < 0:
                print("error: too many closing square brackets ']'")  
                return LineType.ERROR 
            now_cmd += c
            ind += 1
        elif c == '(':
            if now_cmd.upper() in ['LEN', 'SZ']: now_cmd = now_cmd.upper()
            open_act += 1
            if open_act > 1:
                print("error: nested action with name '('")  
                return LineType.ERROR  
            now_cmd += c
            ind += 1
        elif c ==')':
            open_act -= 1
            if open_act < 0:
                print("error: too many closing brackets ')'")  
                return LineType.ERROR 
            now_cmd += c
            ind += 1
        else:
            now_cmd += c
            ind+=1

    __help_ret_add()
    return ret


def code_parse():
    #global asm_file, pcode_file, line, ind_line
    
    while config.line:
        line = del_comment(config.line)
        if(len(line) == 0):pre_continue(); continue

        #check: it's code line?
        line_type = type_of_line(line)
        if(line_type != LineType.CODE_OR_VAR): return line_type

        if LineType.upd_line_type(LineType.CODE): return LineType.ERROR
        
        cmd = cmd_line_normalization(line)
        if cmd == LineType.ERROR: return cmd

        cmd_name = cmd[0]
        operands = cmd[1:]
            
        func = cmd_handler.get(cmd_name)
        if(not func):
            cmd_prefix = get_cmd_prefix(cmd_name)
            if(not cmd_prefix[0]):
                print("not such command: " + str(cmd_name)+"  line: " + str(config.ind_line))
                return LineType.ERROR
            cmd_prefix = cmd_prefix[1]
            func = cmd_handler.get(cmd_prefix)
            line_res = func(operands, cmd_name)
        else:
            line_res = func(operands, "")
        if(line_res.valid == False):
            print("error:    cmd: "+str(cmd_name) + "   line: "+str(config.ind_line))
            print(line_res.why_invalid)
            return LineType.ERROR

        
        config.pcode_file.write(bytearray(line_res.v_bytes))    
        pre_continue()
        
    add_hlt(config.pcode_file)#ADD HLT IN END    
    return LineType.END


#######################################
##
#        FUNC PARSE
#
def func_parse():
    #global parse_info, line, ind_line
    
    line = del_comment(config.line)
    if(len(line) < 1):print('[dev] error: call func_parse when it is not func -___-'); raise Exception('[ERROR:DEV]')
    
    LineType.upd_line_type(LineType.FUNC)

    first_char = line[0]
    line = line[1:]
    i2 = line.find(':') 
    if(i2 == -1):print("error: after name of function must stay ':'"); return LineType.ERROR
    if(len(line) != i2+1):print("error: after 'name_of _function:' may only stay comment or next line"); return LineType.ERROR
    
    
    if(first_char == '!'):
        func_type = 'glob_funcs'
        if(line[0] == '+'):line = line[1:]; i2 -= 1
        if(line[0] == '-'):print("error: entry point(!) can be only global func(+) not local(-)"); return LineType.ERROR
        if(config.parse_info['entry_point'] != None):
            print('error: entry point is already exist '+config.parse_info['entry_point'])
            return LineType.ERROR
        local = False
    elif(first_char == '+'):func_type = 'glob_funcs'; local = False
    elif(first_char == '-'):func_type = 'loc_funcs'; local = True
    else: print('error: weird error ... it must be func'); return LineType.ERROR

    func_name = line[0:i2]
    check = valid_name(func_name)
    if check[0] == TypeofNameAction.ERROR:
        print('error: name is not valid   name: "'+func_name+'"   line:'+str(config.ind_line))
        print(check[1])
        return LineType.ERROR     
    if(check_name(func_name) != None):
        print('error: name '+func_name+' already used   line:'+str(config.ind_line))
        return LineType.ERROR

    if(first_char == '!'):config.parse_info['entry_point'] = func_name

    name_for_subst = asm_name(func_name, config.pcode_file.tell(), TypeofName.func, local)#TODO:CHECK:file.tell()
    name_substitute(name_for_subst)
    config.parse_info[func_type] += [name_for_subst]
    
    pre_continue()
    return LineType.CODE


#######################################
##
#        LABEL PARSE
#
def label_parse():
    #global parse_info, line, ind_line
    
    line = del_comment(config.line)
    if(len(line) < 1):print('[dev] error: call label_parse when it is empty line -___-'); raise Exception('[ERROR:DEV]')
    
    if LineType.upd_line_type(LineType.LABEL): return LineType.ERROR

    first_char = line[0]
    line = line[1:]
    i2 = line.find(':') 
    if(i2 == -1):print("error: after name of label must stay ':'"); return LineType.ERROR
    if(len(line) != i2+1):print("error: after 'name_of _label:' may only stay comment or next line"); return LineType.ERROR
    
    if(first_char != '.'):print("weird error: there must be '.'"); return LineType.ERROR
    
    label_name = line[0:i2]
    
    check = valid_name(label_name)
    if check[0] == TypeofNameAction.ERROR:
        print('error: name is not valid   name: "'+label_name+'"   line:'+str(config.ind_line))
        print(check[1])
        return LineType.ERROR     
    if(check_name(label_name) != None):
        print('error: name '+label_name+' already used   line:'+str(config.ind_line))
        return LineType.ERROR

    name_for_subst = asm_name(label_name, config.pcode_file.tell(), TypeofName.label, True)
    name_substitute(name_for_subst)
    config.parse_info['labels'] += [name_for_subst]
    
    pre_continue()
    return LineType.CODE

##################################################
####
##               ASM TO PCODE
#
def ASM_to_PCode(path_from, path_to = "p.#code#"):
    #global asm_file, pcode_file, line, config.ind_line
    try:
        config.asm_file = open(path_from, "r")
    except:
        print("path to asm file is bad")
        return 1
    try:
        config.pcode_file = open(path_to, "wb")
    except:
        print("path to pcode file is bad  -______-")
        print("[mentioned in path folders must exist]")
        return 1

    reg_init()
    
    config.line = config.asm_file.readline()
    config.ind_line = 1

    line_type = section_parse()
    if(line_type == LineType.END): add_hlt(config.pcode_file)#EMPTY FILE == HLT
    while(line_type != LineType.END):#TODO
        if(type(line_type) != int and len(line_type) == 2 and line_type[0] == LineType.VAR):
            line_type = var_parse(line_type[1])
        elif(line_type == LineType.CODE): line_type = code_parse()
        elif(line_type == LineType.LABEL): line_type = label_parse()
        elif(line_type == LineType.FUNC): line_type = func_parse()
        elif(line_type == LineType.SECTION): line_type = section_parse()
        elif(line_type == LineType.ERROR): print(config.line+'  (line: '+str(config.ind_line)+')'); return 1
        else: print('omg... there is not such type of line:  (line: '+str(config.ind_line)+')'); return 1

    if LineType.upd_line_type(LineType.END): return LineType.ERROR

    if exist_expected_names():
        print("parsing ended but expected names still exist:")
        print_all_expected_names()
        return 1
    
    create_header(path_to[:path_to.rfind('.')]+'.#OS_exe_header#')
        
    config.pcode_file.close()
    config.asm_file.close()
    return 0

len_arg = len(sys.argv)
ret_val = 0
if(len_arg == 1): ret_val = ASM_to_PCode('')
if(len_arg == 2): ret_val = ASM_to_PCode(sys.argv[1])
if(len_arg > 2): ret_val = ASM_to_PCode(sys.argv[1], sys.argv[2])
if(ret_val != 0):
    #print(config.parse_info)#TODO:DEL
    print('some error occurred during assembling to pcode')
else:
    print('\nassembling DONE')
