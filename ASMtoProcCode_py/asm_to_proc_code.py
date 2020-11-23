#from opcodes import *;
from registers import reg_init
from  cmd_parse import cmd_handler
from  cmd_parse import get_cmd_prefix

from values import is_num, is_fnum, is_reg, f_value_to_byte, value_to_byte, valid_name, check_value, NOT_REG
from variable_types import get_variable_type, ALL_VAR_TYPES, SCALAR_VAR_TYPES, NAME_TYPE__VAR, NAME_TYPE__FUNC, NAME_TYPE__LABEL

from class__asm_name import asm_name

from global_variable import check_name, name_substitute

import config

import sys

# + + + CONSTS + + + ###################
LINE_TYPE__CODE_OR_VAR = -3
LINE_TYPE__ERROR = -2
LINE_TYPE__END = -1
LINE_TYPE__CODE = 0
LINE_TYPE__SECTION = 1
LINE_TYPE__LABEL = 2
LINE_TYPE__FUNC = 3
LINE_TYPE__VAR = 4

VAR__ONE = -1#one may be only local var
VAR__LOC = 0
VAR__GLOB = 1
# - - - CONSTS - - - ###################

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

def create_header(name_parse_info):#TODO:we need to create header for .#pcode# executable file.
    #it need for compiler/os but not for processor so out it in other file .#pocde# -> .#PARSE_HEADER#
    #first 4byte is - version(for test -5 it is 0(i.e. there is no one section))
    pass
    return

def type_of_line(line):
    c = line[0]
    if(c == '.'):return LINE_TYPE__LABEL
    if(c == '='):return LINE_TYPE__SECTION
    if(c=='+' or c=='-' or c=='!'):return LINE_TYPE__FUNC
    return LINE_TYPE__CODE_OR_VAR

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
            section_name = config.line[1:]
            i = section_name.find(':')
            if(i == -1):print('after section name should be ":"  (line: '+str(config.ind_line)+')'); return LINE_TYPE__ERROR
            section_name=section_name[0:i]
            config.line = config.line[i+2:]

            #one-line section(s):
            if(section_name == 'var'): return (LINE_TYPE__VAR, VAR__ONE)

            #many-line sections:
            if(len(config.line)!=0):print("error: if section is not 'var' then after ':' may be only comment"); return LINE_TYPE__ERROR
            pre_continue()
            if(section_name in ['vars','-vars']): return (LINE_TYPE__VAR, VAR__LOC)
            if(section_name == '+vars'): return (LINE_TYPE__VAR, VAR__GLOB)
            if(section_name == 'code'): return LINE_TYPE__CODE

            #error such section not exist!:
            print('such section: "'+section_name+'" not exist    (line:'+str(config.ind_line)+')')
            return LINE_TYPE__ERROR
        else: return LINE_TYPE__CODE #section of code
                
        pre_continue()

    #no:asm_file.seek(0)#go to start of file
    return LINE_TYPE__END

#######################################
##
#        VAR PARSE
#
def var_parse(var_section_type):
    #global parse_info, asm_file, pcode_file, line, ind_line

    if(var_section_type == VAR__GLOB): name_type = 'glob_vars'
    else: name_type = 'loc_vars'

    if(len(config.line) == 0 and var_section_type == VAR__ONE):
        print('var section must be not empty one-line section!')
        print('=var: var_name VAR_TYPE value[, ..., value]')
        return LINE_TYPE__ERROR        
    
    while config.line:
        #var_name var_type value[, ..., value]
        line = del_comment(config.line)
        if(len(line) == 0):
            if(var_section_type == VAR__ONE):
                print('var section must be not empty one-line section!  (line: '+str(config.ind_line)+')')
                return LINE_TYPE__ERROR
            pre_continue()
            continue
        line_type = type_of_line(line)
        if(line_type != LINE_TYPE__CODE_OR_VAR):
            if(line_type != LINE_TYPE__SECTION):
                print('error: after var section may stay only other section')
                if(line_type == LINE_TYPE__FUNC):print('but there function defenition')
                if(line_type == LINE_TYPE__LABEL):print('but there label defenition')
                return LINE_TYPE__ERROR 
            if(var_section_type != VAR__ONE):return line_type
            print('error: in (one-line)var section must be only one variable definition.')
            print('       line:'+ str(config.ind_line)+'   content: '+line)
            return LINE_TYPE__ERROR

        #line separate on ?tokens?:
        cstr_in_line = line.split('"')
        if(len(cstr_in_line)%2 == 0):
            print('error " in the  line: '+str(config.ind_line)+'  with content: '+line)
            return LINE_TYPE__ERROR
        
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
            return LINE_TYPE__ERROR 

        var_name = words[0]
        check = valid_name(var_name)
        if(check[0] == False):
            print('error: name is not valid   name:'+var_name+'   line:'+str(config.ind_line))
            print(check[1])
            return LINE_TYPE__ERROR     
        if(check_name(var_name) != None):
            print('error: name '+var_name+' already used   line:'+str(config.ind_line))
            return LINE_TYPE__ERROR

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
            return LINE_TYPE__ERROR

        if(var_type in SCALAR_VAR_TYPES):
            if(len(var_values) != 1):
                print ('error: too many values('+str(len(var_values))+') for '+var_type+' var')
                print('need one value.   values: '+str(var_values))
                return LINE_TYPE__ERROR
        
        if(var_type[0:3] == 'INT'):#INT
            int_sz = int(var_type[3:])
            if(not vp_int_get(var_values[0], int_sz)):return LINE_TYPE__ERROR
        elif(var_type[0:4] == 'IARR'):#INT ARRAY
            arr_len = len(var_values)
            int_sz = int(var_type[4:])
            for x in var_values:
                if(not vp_int_get(x, int_sz)):return LINE_TYPE__ERROR
        elif(var_type == 'DOUB'):#DOUBLE
            if(not vp_double_get(var_values[0])):return LINE_TYPE__ERROR
        elif(var_type == 'DARR'):#DOUBLE ARRAY
            arr_len = len(var_values)
            for x in var_values:
                if(not vp_double_get(x)):return LINE_TYPE__ERROR
        elif(var_type == 'CSTR'):#C STRING
            if(not vp_cstr_get(var_values[0])):return LINE_TYPE__ERROR
        else:#._.
            print('kawo? .-. something weird happen  (did not implement type'+var_type+')')
            return LINE_TYPE__ERROR

        name_for_subst = asm_name(var_name, config.pcode_file.tell(), NAME_TYPE__VAR, var_type, arr_len)#TODO:CHECK:file.tell()
        if(len(v_bytes)==0):# or name_for_subst==None):
            print('error (or maybe not ... im not sure actually,  heh)    line:'+str(config.ind_line))
            return LINE_TYPE__ERROR
        config.pcode_file.write(bytearray(v_bytes))#TODO:CHECK
        name_substitute(name_for_subst)
        config.parse_info[name_type] += [name_for_subst]
        pre_continue()
        if(var_section_type == VAR__ONE):return LINE_TYPE__SECTION #TODO:OR:MAYBE:LINE_TYPE__CODE

    return LINE_TYPE__END

#######################################
##
#        CODE PARSE
#
def code_parse():
    #global asm_file, pcode_file, line, ind_line
    
    while config.line:
        line = del_comment(config.line)
        if(len(line) == 0):pre_continue(); continue

        #check: it's code line?
        line_type = type_of_line(line)
        if(line_type != LINE_TYPE__CODE_OR_VAR): return line_type
        
        
        br_count = line.count('[')  
        if br_count == 0: pass
        elif br_count  == 1:
            if line.count(']') != 1:
                print("amount of ']' more than '['")  
                return LINE_TYPE__ERROR  
            if line.find('[') > line.find(']'):
                print("wrong order of '[' and ']'")
                return LINE_TYPE__ERROR
        elif br_count  > 1:
            print("too many '[' in one line (in current cmds in one line may be only one pointer)")
            return LINE_TYPE__ERROR

        str_param = line.split('"')
        len_str_param = len(str_param)
        line = str_param[0]
        if(len_str_param != 3 and len_str_param != 1):
            print("string error: "+ line+"  line: " + str(config.ind_line))
            print('in one line may stay only 0 or 2 char ["] ')
            return LINE_TYPE__ERROR
        if(len_str_param == 3 and len(str_param[2].replace(' ','')) != 0):
            print("string error: "+ line+"  line: " + str(config.ind_line))
            print('after string may stay only comment')
            return LINE_TYPE__ERROR
        if(len_str_param == 3 and br_count != 0):
            print("now it error when str and ptr in one line")
            return LINE_TYPE__ERROR
        
        
        if br_count == 0:
            line = line.split(' ')
        else:
            start = line.split('[')
            end = start[1].split(']')
            line = start[0].split(' ') +['['+end[0]+']']+ end[1].split(' ')
        if(len_str_param == 3): line += ['"' + str_param[1] + '"']
        cmd = []
        #pass empty str and make upper that need make upper:
        line[0] = line[0].upper()
        for x in line:
            if(len(x) == 0): continue
            if is_reg(x.upper())[0] != NOT_REG: x = x.upper()
            cmd += [x]

        cmd_name = cmd[0]
        operands = cmd[1:]
        
        for i in range(0,len(operands)-1):#delete ',' after operands except last
            if(operands[i][len(operands[i])-1]==','):operands[i]=operands[i][0:len(operands[i])-1]
            
        func = cmd_handler.get(cmd_name)
        if(not func):
            cmd_prefix = get_cmd_prefix(cmd_name)
            if(not cmd_prefix[0]):
                print("not such command: " + str(cmd_name)+"  line: " + str(config.ind_line))
                return LINE_TYPE__ERROR
            cmd_prefix = cmd_prefix[1]
            func = cmd_handler.get(cmd_prefix)
            line_res = func(operands, cmd_name)
        else:
            line_res = func(operands, "")
        if(line_res.valid == False):
            print("error:    cmd: "+str(cmd_name) + "   line: "+str(config.ind_line))
            print(line_res.why_invalid)
            return LINE_TYPE__ERROR

        
        config.pcode_file.write(bytearray(line_res.v_bytes))    
        pre_continue()
        
    add_hlt(config.pcode_file)#ADD HLT IN END    
    return LINE_TYPE__END


#######################################
##
#        FUNC PARSE
#
def func_parse():
    #global parse_info, line, ind_line
    
    line = del_comment(config.line)
    if(len(line) < 1):print('[dev] error: call func_parse when it is not func -___-'); raise Exception('[ERROR:DEV]')
    
    first_char = line[0]
    line = line[1:]
    i2 = line.find(':') 
    if(i2 == -1):print("error: after name of function must stay ':'"); return LINE_TYPE__ERROR
    if(len(line) != i2+1):print("error: after 'name_of _function:' may only stay comment or next line"); return LINE_TYPE__ERROR
    
    
    if(first_char == '!'):
        func_type = 'glob_funcs'
        if(line[0] == '+'):line = line[1:]; i2 -= 1
        if(line[0] == '-'):print("error: entry point(!) can be only global func(+) not local(-)"); return LINE_TYPE__ERROR
        if(config.parse_info['entry_point'] != None):
            print('error: entry point is already exist '+config.parse_info['entry_point'])
            return LINE_TYPE__ERROR
    elif(first_char == '+'):func_type = 'glob_funcs'
    elif(first_char == '-'):func_type = 'loc_funcs'
    else: print('error: weird error ... it must be func'); return LINE_TYPE__ERROR

    func_name = line[0:i2]
    check = valid_name(func_name)
    if(check[0] == False):
        print('error: name is not valid   name: "'+func_name+'"   line:'+str(config.ind_line))
        print(check[1])
        return LINE_TYPE__ERROR     
    if(check_name(func_name) != None):
        print('error: name '+func_name+' already used   line:'+str(config.ind_line))
        return LINE_TYPE__ERROR

    if(first_char == '!'):config.parse_info['entry_point'] = func_name

    name_for_subst = asm_name(func_name, config.pcode_file.tell(), name_type = NAME_TYPE__FUNC)#TODO:CHECK:file.tell()
    name_substitute(name_for_subst)
    config.parse_info[func_type] += [name_for_subst]
    
    pre_continue()
    return LINE_TYPE__CODE


#######################################
##
#        LABEL PARSE
#
def label_parse():
    #global parse_info, line, ind_line
    
    line = del_comment(config.line)
    if(len(line) < 1):print('[dev] error: call label_parse when it is empty line -___-'); raise Exception('[ERROR:DEV]')
    
    first_char = line[0]
    line = line[1:]
    i2 = line.find(':') 
    if(i2 == -1):print("error: after name of label must stay ':'"); return LINE_TYPE__ERROR
    if(len(line) != i2+1):print("error: after 'name_of _label:' may only stay comment or next line"); return LINE_TYPE__ERROR
    
    if(first_char != '.'):print("weird error: there must be '.'"); return LINE_TYPE__ERROR
    
    label_name = line[0:i2]
    
    check = valid_name(label_name)
    if(check[0] == False):
        print('error: name is not valid   name: "'+label_name+'"   line:'+str(config.ind_line))
        print(check[1])
        return LINE_TYPE__ERROR     
    if(check_name(label_name) != None):
        print('error: name '+label_name+' already used   line:'+str(config.ind_line))
        return LINE_TYPE__ERROR

    name_for_subst = asm_name(label_name, config.pcode_file.tell(), name_type = NAME_TYPE__LABEL)#TODO:CHECK:file.tell()
    name_substitute(name_for_subst)
    config.parse_info['labels'] += [name_for_subst]
    
    pre_continue()
    return LINE_TYPE__CODE

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
    if(line_type == LINE_TYPE__END): add_hlt(config.pcode_file)#EMPTY FILE == HLT
    while(line_type != LINE_TYPE__END):#TODO
        if(type(line_type) != int and len(line_type) == 2 and line_type[0] == LINE_TYPE__VAR):
            line_type = var_parse(line_type[1])
        elif(line_type == LINE_TYPE__CODE): line_type = code_parse()
        elif(line_type == LINE_TYPE__LABEL): line_type = label_parse()
        elif(line_type == LINE_TYPE__FUNC): line_type = func_parse()
        elif(line_type == LINE_TYPE__SECTION): line_type = section_parse()
        elif(line_type == LINE_TYPE__ERROR): print('(line: '+str(config.ind_line)+')'); return 1
        else: print('omg... there is not such type of line:  (line: '+str(config.ind_line)+')'); return 1

    #TODO:create header
        
    config.pcode_file.close()
    config.asm_file.close()
    return 0

len_arg = len(sys.argv)
ret_val = 0
if(len_arg == 1): ret_val = ASM_to_PCode('')
if(len_arg == 2): ret_val = ASM_to_PCode(sys.argv[1])
if(len_arg > 2): ret_val = ASM_to_PCode(sys.argv[1], sys.argv[2])
if(ret_val != 0):
    print(config.parse_info)#TODO:DEL
    print('some error occurred during assembling to pcode')
else:
    print('\nassembling DONE')
