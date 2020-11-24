from opcodes import opcodes, jump_cmds, OPCODE_PASS
from variable_types import TypeofName, TypeofNameAction 
from values import is_num, is_fnum, value_to_byte, f_value_to_byte, check_value, iGP_REG, fGP_REG, is_reg, NOT_PTR_REG, NOT_REG, valid_name, PTR_BYTE, is_ptr_reg
from is_ptr import is_cptr, is_ncptr, is_str_ptr, IS_PTR_RET__OK

from global_variable import check_name, get_pcode_pos, add_expected_name, add_expected_ptr_expression

from class__expected_name import expected_name, std_diff_func, std_diff_with_shift_func

class ret_cmd:
    def __init__(self, valid, v_bytes, why_invalid = ""):
        self.valid = valid
        self.v_bytes = v_bytes
        if(not valid): self.why_invalid = why_invalid

    def __str__(self):
        return str(self.valid)+" "+str(self.v_bytes)


TOO_MANY_PARAMS = ret_cmd(False, [0], "Too many params") 
TOO_FEW_PARAMS = ret_cmd(False, [0], "Too few params")
ERR_OP_1 = ret_cmd(False, [0], "Error operand[1]")
ERR_OP_2 = ret_cmd(False, [0], "Error operand[2]")
TOO_BIG_OP_1_NUM = ret_cmd(False, [0], "Too big operand[1]") 
TOO_BIG_OP_2_NUM = ret_cmd(False, [0], "Too big operand[2]") 
ERR_CMD = ret_cmd(False, [0], "Error command")
ERR_REG_COMP = ret_cmd(False, [0], "registers is not compatibility in this cmd (try use MOV if you want comp)")


ERR_TOO_BIG_STR = ret_cmd(False, [0], "Length of string is too big (max is 255)")
ERR_STR_CHAR = ret_cmd(False, [0], "error char in string (you should use only c : 0 <= ord(c) <= 255)")

ERR_NOT_PTR_REG = ret_cmd(False, [0], "registers is not ptr reg")
def err_not_ptr_reg(reg): return ret_cmd(False, [0], "registers "+reg+" is not ptr reg")

ERR_PLEASE_NOT_JUMP_BY_NUM = ret_cmd(False, [0], "jump by number is ... bad idea; you can.. although no, there is error i.e. it's not safe. Write a label and jump on it")
#####################################################################################
#########
####            CMD ARE BELLOW
#
#

# TODO:DEL:COPY-PAST (from one func to other)

def PUSH_cmd(ops, cmd = ""):
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS

    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == iGP_REG):
        if(is_reg_1[3] and cmd == ""):
            return ret_cmd(True, [opcodes["PUSH_EAX"]])
        if(cmd == ""):
            return ret_cmd(True, [opcodes["PUSH_REG"], is_reg_1[1]])
        return ERR_OP_1
    if(is_reg_1[0] == fGP_REG):
        if(is_reg_1[3] and cmd == ""):
            return ret_cmd(True, [opcodes["PUSH_FAX"]])
        if(cmd == ""):
            return ret_cmd(True, [opcodes["PUSH_FREG"], is_reg_1[1]])
        return ERR_OP_1
    
    is_num_1 = is_num(ops[0])
    if(is_num_1[0] and cmd != "PUSH_F"):
        value = is_num_1[1]
        if(cmd == "" or cmd == "PUSHD" or cmd == "PUSH_4"):
            if(check_value(value, 4)): return TOO_BIG_OP_1_NUM
            v_bytes = [opcodes["PUSH_4"]]
            value_to_byte(v_bytes, value, 4)
            return ret_cmd(True, v_bytes)
        if(cmd == "PUSHQ" or cmd == "PUSH_8"):
            if(check_value(value, 8)): return TOO_BIG_OP_1_NUM
            v_bytes = [opcodes["PUSH_8"]]
            value_to_byte(v_bytes, value, 8)
            return ret_cmd(True, v_bytes)
        #return ERR_OP_1

    is_fnum_1 = is_fnum(ops[0])
    if(is_fnum_1[0]):
        value = is_fnum_1[1]
        if(cmd == "" or cmd == "PUSH_F"):
            v_bytes = [opcodes["PUSH_F"]]
            f_value_to_byte(v_bytes, value)
            return ret_cmd(True, v_bytes)
    return ERR_OP_1

def POP_cmd(ops, cmd=""):
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        if(cmd == "" or cmd == "POPD" or cmd == "POP_4"):
            return ret_cmd(True, [opcodes['POPD']])
        if(cmd == 'POP_F'):
            return ret_cmd(True, [opcodes['POP_F']])
        return ERR_OP_1

    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == iGP_REG):
        if(is_reg_1[3] and cmd == ""):
            return ret_cmd(True, [opcodes["POP_EAX"]])
        if(cmd == ""):
            return ret_cmd(True, [opcodes["POP_REG"], is_reg_1[1]])
        return ERR_OP_1
    if(is_reg_1[0] == fGP_REG):
        if(is_reg_1[3] and cmd == ""):
            return ret_cmd(True, [opcodes["POP_FAX"]])
        if(cmd == ""):
            return ret_cmd(True, [opcodes["POP_FREG"], is_reg_1[1]])
        return ERR_OP_1
    return ERR_OP_1

#ADD SUM MUL DIV COMAND:
def ASMD_cmd_help(ops, cmd, prefix):
    op_len = len(ops)
    if(op_len > 2):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        if(cmd == ''):
            return ret_cmd(True, [opcodes[prefix+"_PPP"]])
        if(cmd == prefix + '_F'):
            return ret_cmd(True, [opcodes[prefix+"_F"]])
        return ERR_OP_1
    if(op_len == 1):
        return TOO_FEW_PARAMS

    if(cmd != ""):return ERR_CMD
    
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == NOT_REG): return ERR_OP_1
    
    is_reg_2 = is_reg(ops[1])
    if(is_reg_2[0]):
        if(is_reg_1[0] != is_reg_2[0]): return ERR_REG_COMP
        if(is_reg_1[0] == iGP_REG):
            return ret_cmd(True, [opcodes[prefix+"_RR"], is_reg_1[1], is_reg_2[1]])
        if(is_reg_1[0] == fGP_REG):
            return ret_cmd(True, [opcodes[prefix+"_FRFR"], is_reg_1[1], is_reg_2[1]])

    v_bytes = []
    op_2 = ops[1]
    if is_str_ptr(op_2):

        op_shift = 2 #CMD[0] {op1:reg} !here!
        const_ptr = is_cptr(op_2, op_shift)
        if(const_ptr[0] == IS_PTR_RET__OK):
            const_ptr = const_ptr[1]
            if(is_reg_1[0] == iGP_REG): v_bytes += [opcodes[prefix+"_REG_CPTR"]]
            elif(is_reg_1[0] == fGP_REG): v_bytes += [opcodes[prefix+"_FREG_CPTR"]]
            else: return ERR_OP_2
            v_bytes += [is_reg_1[1]]
            if const_ptr.need_variable_define():
                add_expected_ptr_expression(const_ptr)
            v_bytes += const_ptr.to_bytes()
            return ret_cmd(True, v_bytes)
        
        cmd_shift = 1
        op_shift = 3 #CMD[0] CMD[1] {op1:reg} !here!
        not_const_ptr = is_ncptr(op_2, cmd_shift, op_shift)
        if(not_const_ptr[0] == IS_PTR_RET__OK):
            not_const_ptr = not_const_ptr[1]
            if(is_reg_1[0] == iGP_REG): v_bytes += [opcodes[prefix+"_REG_NCPTR"]]
            elif(is_reg_1[0] == fGP_REG): v_bytes += [opcodes[prefix+"_FREG_NCPTR"]]
            else: return ERR_OP_2
            v_bytes += not_const_ptr.get_cmd_to_bytes()
            v_bytes += [is_reg_1[1]]
            if not_const_ptr.need_variable_define():
                add_expected_ptr_expression(not_const_ptr)
            v_bytes += not_const_ptr.to_bytes()
            return ret_cmd(True, v_bytes)
        
        return ret_cmd(False, [0], const_ptr[1]+'\n'+not_const_ptr[1])

    if(is_reg_1[0] == iGP_REG):
        return num_help(ops[1], is_reg_1[2], [opcodes[prefix+"_RV"], is_reg_1[1]], [])
    elif(is_reg_1[0] == fGP_REG):
        is_fnum_2 = is_fnum(ops[1])
        if(not is_fnum_2[0]): return ERR_OP_2
        value = is_fnum_2[1]
        v_bytes = [opcodes[prefix + "_FRV"], is_reg_1[1]]
        f_value_to_byte(v_bytes, value)
        return ret_cmd(True, v_bytes)
        
    return ERR_OP_2
        
    
def ADD_cmd(ops, cmd=""): return ASMD_cmd_help(ops, cmd, 'ADD')
    
def SUB_cmd(ops, cmd=""): return ASMD_cmd_help(ops, cmd, 'SUB')

def MUL_cmd(ops, cmd=""): return ASMD_cmd_help(ops, cmd, 'MUL')

def DIV_cmd(ops, cmd=""): return ASMD_cmd_help(ops, cmd, 'DIV')

def num_help(num_op, reg_bytes, opcodes_prev, opcodes_past, byte_shift = None):
    temp = valid_name(num_op, False)
    typeof_act = temp[0]
    if typeof_act != TypeofNameAction.ERROR:
        value = temp[1]
        temp = check_name(value)
        v_bytes = opcodes_prev#[opcodes["MOV_RV"], is_reg_1[1]]
        if(temp != None): 
            value = temp.get_value_by_typeof_act(typeof_act)
            value_to_byte(v_bytes, value, reg_bytes)
            v_bytes += opcodes_past
            return ret_cmd(True, v_bytes)
        else: 
            if byte_shift == None: byte_shift = len(v_bytes)
            exp_name = expected_name(get_pcode_pos()+byte_shift, value, typeof_act)
            if not exp_name.is_valid(): return ret_cmd(False, [0], 'such action with "'+value+'" is invalid')
            add_expected_name(exp_name)
            v_bytes += exp_name.to_bytes()
            v_bytes += opcodes_past
            return ret_cmd(True, v_bytes)

    is_num_op = is_num(num_op)
    if(not is_num_op[0]): return ERR_OP_2
    value = is_num_op[1]
    if(check_value(value, reg_bytes)): return TOO_BIG_OP_2_NUM
    v_bytes = opcodes_prev
    value_to_byte(v_bytes, value, reg_bytes)
    v_bytes += opcodes_past
    return ret_cmd(True, v_bytes)


def MOV_cmd(ops, cmd=""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 2):
        return TOO_MANY_PARAMS
    if(op_len < 2):
        return TOO_FEW_PARAMS
    
    op_1 = ops[0]
    if is_str_ptr(op_1):
        is_reg_2 = is_reg(ops[1])
        if(is_reg_2[0] == NOT_REG): return ERR_OP_2

        v_bytes = []
        op_shift = 1 #CMD[0] !here! {op2:reg} 
        const_ptr = is_cptr(op_1, op_shift)
        if(const_ptr[0] == IS_PTR_RET__OK):
            const_ptr = const_ptr[1]
            if(is_reg_2[0] == iGP_REG): v_bytes += [opcodes["MOV_CPTR_REG"]]
            elif(is_reg_2[0] == fGP_REG): v_bytes += [opcodes["MOV_CPTR_FREG"]]
            else: return ERR_OP_2
            if const_ptr.need_variable_define():
                add_expected_ptr_expression(const_ptr)
            v_bytes += const_ptr.to_bytes()
            v_bytes += [is_reg_2[1]]
            return ret_cmd(True, v_bytes)

        cmd_shift = 1
        op_shift = 2 #CMD[0] CMD[1] !here! {op2:reg} 
        not_const_ptr = is_ncptr(op_1, cmd_shift, op_shift)
        if(not_const_ptr[0] == IS_PTR_RET__OK):
            not_const_ptr = not_const_ptr[1]
            if(is_reg_2[0] == iGP_REG): v_bytes += [opcodes["MOV_NCPTR_REG"]]
            elif(is_reg_2[0] == fGP_REG): v_bytes += [opcodes["MOV_NCPTR_FREG"]]
            else: return ERR_OP_2
            v_bytes += not_const_ptr.get_cmd_to_bytes()
            if not_const_ptr.need_variable_define():
                add_expected_ptr_expression(not_const_ptr)
            v_bytes += not_const_ptr.to_bytes()
            v_bytes += [is_reg_2[1]]
            return ret_cmd(True, v_bytes)
        
        return ret_cmd(False, [0], const_ptr[1]+'\n'+not_const_ptr[1])

    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == NOT_REG): return ERR_OP_1
    
    is_reg_2 = is_reg(ops[1])
    if(is_reg_2[0]):
        if(is_reg_1[0] == iGP_REG):
            if(is_reg_2[0] == iGP_REG):
                return ret_cmd(True, [opcodes["MOV_RR"], is_reg_1[1], is_reg_2[1]])
            if(is_reg_2[0] == fGP_REG):
                return ret_cmd(True, [opcodes["MOV_RFR"], is_reg_1[1], is_reg_2[1]])
        if(is_reg_1[0] == fGP_REG):
            if(is_reg_2[0] == iGP_REG):
                return ret_cmd(True, [opcodes["MOV_FRR"], is_reg_1[1], is_reg_2[1]])
            if(is_reg_2[0] == fGP_REG):
                return ret_cmd(True, [opcodes["MOV_FRFR"], is_reg_1[1], is_reg_2[1]])

    v_bytes = []
    op_2 = ops[1]
    if is_str_ptr(op_2):

        op_shift = 2 #CMD[0] {op1:reg} !here!
        const_ptr = is_cptr(op_2, op_shift)
        if(const_ptr[0] == IS_PTR_RET__OK):
            const_ptr = const_ptr[1]
            if(is_reg_1[0] == iGP_REG): v_bytes += [opcodes["MOV_REG_CPTR"]]
            elif(is_reg_1[0] == fGP_REG): v_bytes += [opcodes["MOV_FREG_CPTR"]]
            else: return ERR_OP_2
            v_bytes += [is_reg_1[1]]
            if const_ptr.need_variable_define():
                add_expected_ptr_expression(const_ptr)
            v_bytes += const_ptr.to_bytes()
            return ret_cmd(True, v_bytes)
        
        cmd_shift = 1
        op_shift = 3 #CMD[0] CMD[1] {op1:reg} !here!
        not_const_ptr = is_ncptr(op_2, cmd_shift, op_shift)
        if(not_const_ptr[0] == IS_PTR_RET__OK):
            not_const_ptr = not_const_ptr[1]
            if(is_reg_1[0] == iGP_REG): v_bytes += [opcodes["MOV_REG_NCPTR"]]
            elif(is_reg_1[0] == fGP_REG): v_bytes += [opcodes["MOV_FREG_NCPTR"]]
            else: return ERR_OP_2
            v_bytes += not_const_ptr.get_cmd_to_bytes()
            v_bytes += [is_reg_1[1]]
            if not_const_ptr.need_variable_define():
                add_expected_ptr_expression(not_const_ptr)
            v_bytes += not_const_ptr.to_bytes()
            return ret_cmd(True, v_bytes)
        
        return ret_cmd(False, [0], const_ptr[1]+'\n'+not_const_ptr[1])


    if(is_reg_1[0] == iGP_REG):
        return num_help(ops[1], is_reg_1[2], [opcodes["MOV_RV"], is_reg_1[1]], [])
    if(is_reg_1[0] == fGP_REG):
        is_fnum_2 = is_fnum(ops[1])
        if(not is_fnum_2[0]): return ERR_OP_2
        value = is_fnum_2[1]
        v_bytes = [opcodes["MOV_FRV"], is_reg_1[1]]
        f_value_to_byte(v_bytes, value)
        return ret_cmd(True, v_bytes)
        
    return ERR_OP_2

#TODO:
def JUMP_cmd(ops, cmd = ""):
    global jump_cmds
    op_len = len(ops)
    if(op_len > 1): return TOO_MANY_PARAMS
    if(op_len == 0): return TOO_FEW_PARAMS

    op = ops[0]

    is_op_reg = is_reg(op)
    if(is_op_reg[0] != NOT_REG):
        is_op_reg = is_ptr_reg(op)
        if(is_op_reg[0] == NOT_PTR_REG): return err_not_ptr_reg(op)
        if(cmd == ""):
            return ret_cmd(True, [opcodes['JUMP_ADDR_REG'], is_op_reg[1]])
        if(cmd not in jump_cmds): return ERR_CMD
        return ret_cmd(True, [opcodes['JUMP_IF_ADDR_REG'], jump_cmds[cmd], is_op_reg[1]])

    is_op_num = is_num(op)
    if(is_op_num[0]):
        #value = is_op_num[1]
        return ERR_PLEASE_NOT_JUMP_BY_NUM
    
    v_bytes = []

    only_labels = False
    if(op[0] == '.'): only_labels = True; op = op[1:]
    temp = valid_name(op, True)#i.e. jump on const is error
    if temp[0] != TypeofNameAction.ERROR:
        typeof_act = temp[0]
        op = temp[1]
        if check_name(op, with_vars = True, with_funcs=False, with_labels=False):
            return ret_cmd(False, [0], "Error operand[1]"+ "\njump on variable is error (in future will be added run-time gen code section)")
        if only_labels and check_name(op, with_vars = False, with_funcs=True, with_labels=False): 
            return ret_cmd(False, [0], "Error operand[1]\n"+'"'+op+'"is a function, but marked as label: ".name"')
        
        if typeof_act != TypeofNameAction.PTR:
            return ret_cmd(False, [0], "Error operand[1]\nwrong action with name. jump on const are restricted, LEN(name)/SZ(name) is a const")

        aname = check_name(op, with_vars = False, with_funcs=not only_labels, with_labels=True)
        local = check_name.last_name_is_local

        if(local and cmd == ""): v_bytes += [opcodes["JUMP_D"]]
        elif(not local and cmd == ""): v_bytes += [opcodes["JUMP_A"]]
        else:
            if(cmd not in jump_cmds): return ERR_CMD
            if local: v_bytes += [opcodes["JUMP_IF_D"], jump_cmds[cmd]]
            else: v_bytes += [opcodes["JUMP_IF_A"], jump_cmds[cmd]]

        if aname:
            ptr = aname.get_value_by_typeof_act(typeof_act)
            if local: value_to_byte(v_bytes, ptr - get_pcode_pos(), PTR_BYTE)
            else: value_to_byte(v_bytes, ptr, PTR_BYTE)
        else:
            typeof_name = TypeofName.not_var # i.e. jump on var is error
            if only_labels: typeof_name = TypeofName.label
            elif local: typeof_name = typeof_name & TypeofName.local
            ptr_func = False
            if local: ptr_func = std_diff_with_shift_func(len(v_bytes))#std_diff_func
            exp_name = expected_name(get_pcode_pos()+ len(v_bytes), op, typeof_act, typeof_name, ptr_func=ptr_func) #get_pcode_pos +  len(v_bytes)
            if not exp_name.is_valid(): return ERR_OP_1
            add_expected_name(exp_name)
            v_bytes+=[OPCODE_PASS] * PTR_BYTE

        return ret_cmd(True, v_bytes)

    #TODO:ADD CHECK VALID PTR(not big, and pointed in code section)
    
    return ret_cmd(False, [0], "Error operand[1]"+ '\n' + temp[1])


def INC_DEC_cmd_help(ops, cmd, prefix):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] != iGP_REG): return ERR_OP_1
    return ret_cmd(True, [opcodes[prefix+"_R"], is_reg_1[1]])
        

def INC_cmd(ops, cmd = ""):
    return INC_DEC_cmd_help(ops, cmd, 'INC')

def DEC_cmd(ops, cmd = ""):
    return INC_DEC_cmd_help(ops, cmd, 'DEC')
    
def OUT_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == iGP_REG): 
        return ret_cmd(True, [opcodes["OUT_R"], is_reg_1[1]])
    if(is_reg_1[0] == fGP_REG): 
        return ret_cmd(True, [opcodes["OUT_FR"], is_reg_1[1]])

    op = ops[0]
    if is_str_ptr(op):
        len_op = len(op)
        op = op[1:len_op-1]
        temp = valid_name(op)
        typeof_act = temp[0]
        if typeof_act != TypeofNameAction.PTR: return ret_cmd(False, [0], 'there may stay only CSTR var name\n'+temp[1])
        value = temp[1]
        temp = check_name(value)
        v_bytes = [opcodes["OUT_CPTR_C_STR"]]
        if(temp != None): 
            value = temp.get_value_by_typeof_act(typeof_act)
            value_to_byte(v_bytes, value, PTR_BYTE)
            return ret_cmd(True, v_bytes)
        else: 
            exp_name = expected_name(get_pcode_pos()+len(v_bytes), value, typeof_act, valid_var_types=['CSTR'])
            if not exp_name.is_valid(): return ret_cmd(False, [0], 'such action with "'+value+'" is invalid')
            add_expected_name(exp_name)
            v_bytes += exp_name.to_bytes()
            return ret_cmd(True, v_bytes)


    c_str = ops[0].replace('\\n','\n')
    len_str = len(c_str)
    if(c_str[0] == '"' and c_str[len_str - 1] == '"'):
        c_str = c_str[1:(len_str - 1)]
        len_str -= 2
        if(len_str > 255): return ERR_TOO_BIG_STR
        v_bytes = [opcodes["OUT_C_STR"], len_str]
        for c in c_str:
            ord_c = ord(c)
            if(ord_c > 255):return ERR_STR_CHAR
            if(ord_c < 0): return ERR_STR_CHAR
            v_bytes += [ord(c)]
        return ret_cmd(True, v_bytes)
    
    return ERR_OP_1

def IN_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == iGP_REG): 
        return ret_cmd(True, [opcodes["IN_R"], is_reg_1[1]])
    if(is_reg_1[0] == fGP_REG): 
        return ret_cmd(True, [opcodes["IN_FR"], is_reg_1[1]])
    return ERR_OP_1

def HLT_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    if(len(ops) > 0): return TOO_MANY_PARAMS
    return ret_cmd(True, [opcodes["HLT"]])

def PASS_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    if(len(ops) > 0): return TOO_MANY_PARAMS
    return ret_cmd(True, [opcodes["PASS"]])


def CMP_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 2): return TOO_MANY_PARAMS
    if(op_len < 2): return TOO_FEW_PARAMS
    
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == NOT_REG): return ERR_OP_1   

    is_reg_2 = is_reg(ops[1])
    if(is_reg_2[0]):
        if(is_reg_1[0] != is_reg_2[0]): return ERR_REG_COMP
        if(is_reg_1[0] == iGP_REG):
            return ret_cmd(True, [opcodes["CMP_REG_REG"], is_reg_1[1], is_reg_2[1]])
        if(is_reg_1[0] == fGP_REG):
            return ret_cmd(True, [opcodes["CMP_FREG_FREG"], is_reg_1[1], is_reg_2[1]])

    if(is_reg_1[0] == iGP_REG):
        return num_help(ops[1], is_reg_1[2], [opcodes["CMP_REG_VAL"], is_reg_1[1]], [])
    if(is_reg_1[0] == fGP_REG):
        is_fnum_2 = is_fnum(ops[1])
        if(not is_fnum_2[0]): return ERR_OP_2
        value = is_fnum_2[1]
        v_bytes = [opcodes["CMP_FREG_VAL"], is_reg_1[1]]
        f_value_to_byte(v_bytes, value)
        return ret_cmd(True, v_bytes)
        
    return ERR_OP_2
    
    
cmd_handler = {
    'PUSH' : PUSH_cmd,
    'POP' : POP_cmd,
    
    'ADD' : ADD_cmd,
    'SUB' : SUB_cmd,
    'MUL' : MUL_cmd,
    'DIV' : DIV_cmd,

    'MOV' : MOV_cmd,
    
    #TODO:JUMP
    'JUMP' : JUMP_cmd,
    'JMP' : JUMP_cmd,

    'INC' : INC_cmd,
    'DEC' : DEC_cmd,

    'OUT' : OUT_cmd,
    'IN'  : IN_cmd,

    'HLT' : HLT_cmd,

    'CMP' : CMP_cmd,
    
    'PASS' : PASS_cmd,
    }


############################################################
#   GET CMD PREFIX:

#TODO: it write not good(copy-past  copy-past):

def get_cmd_prefix(cmd_name):
    global jump_cmds
    len_cmd = len(cmd_name)
    if(len_cmd < 2): return [False]
    #NOW CANNOT = NC
    #4:
    if(cmd_name[0:4] == 'PUSH'): return [True, 'PUSH', cmd_name]
    if(cmd_name[0:4] == 'PASS'): return [True, 'PASS', cmd_name] #NC
    #3:
    if(cmd_name[0:3] == 'POP'): return [True, 'POP', cmd_name]

    #[ADD|SUB|MUL|DIV]_F:
    if(cmd_name[0:3] == 'ADD'): return [True, 'ADD', cmd_name] 
    if(cmd_name[0:3] == 'SUB'): return [True, 'SUB', cmd_name]
    if(cmd_name[0:3] == 'MUL'): return [True, 'MUL', cmd_name]
    if(cmd_name[0:3] == 'DIV'): return [True, 'DIV', cmd_name]

    if(cmd_name[0:3] == 'MOV'): return [True, 'MOV', cmd_name] #NC


    if(cmd_name[0:3] == 'OUT'): return [True, 'INC', cmd_name] #NC
    
    if(cmd_name[0:3] == 'DEC'): return [True, 'DEC', cmd_name] #NC
    if(cmd_name[0:3] == 'INC'): return [True, 'INC', cmd_name] #NC

    if(cmd_name[0:3] == 'HLT'): return [True, 'HLT', cmd_name] #NC
    
    if(cmd_name[0:3] == 'CMP'): return [True, 'CMP', cmd_name] #NC
    #2:
    if(cmd_name[0:2] == 'IN'): return [True, 'IN', cmd_name] #NC

    if(cmd_name[0] == 'J' and cmd_name in jump_cmds): return [True, 'JUMP', cmd_name]

    return [False]
