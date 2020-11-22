from opcodes import *;
from registers import *;
from values import *;

from is_ptr import is_cptr, is_ncptr;

class ret_cmd:
    def __init__(self, valid, v_bytes, why_invalid = ""):
        self.valid = valid;
        self.v_bytes = v_bytes;
        if(not valid): self.why_invalid = why_invalid;

    def __str__(self):
        return str(self.valid)+" "+str(self.v_bytes)


TOO_MANY_PARAMS = ret_cmd(False, [0], "Too many params") 
TOO_FEW_PARAMS = ret_cmd(False, [0], "Too few params")
ERR_OP_1 = ret_cmd(False, [0], "Error operand[1]");
ERR_OP_2 = ret_cmd(False, [0], "Error operand[2]");
TOO_BIG_OP_1_NUM = ret_cmd(False, [0], "Too big operand[1]") 
TOO_BIG_OP_2_NUM = ret_cmd(False, [0], "Too big operand[2]") 
ERR_CMD = ret_cmd(False, [0], "Error command");
ERR_REG_COMP = ret_cmd(False, [0], "registers is not compatibility in this cmd (try use MOV if you want comp)");


ERR_TOO_BIG_STR = ret_cmd(False, [0], "Length of string is too big (max is 255)");
ERR_STR_CHAR = ret_cmd(False, [0], "error char in string (you should use only c : 0 <= ord(c) <= 255)");
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

    if(is_reg_1[0] == iGP_REG):
        is_num_2 = is_num(ops[1])
        if(not is_num_2[0]): return ERR_OP_2
        value = is_num_2[1]
        reg_bytes = is_reg_1[2]
        if(check_value(value, reg_bytes)): return TOO_BIG_OP_2_NUM
        v_bytes = [opcodes[prefix + "_RV"], is_reg_1[1]]
        value_to_byte(v_bytes, value, reg_bytes)
        return ret_cmd(True, v_bytes)
    if(is_reg_1[0] == fGP_REG):
        is_fnum_2 = is_fnum(ops[1])
        if(not is_fnum_2[0]): return ERR_OP_2
        value = is_fnum_2[1]
        v_bytes = [opcodes[prefix + "_FRV"], is_reg_1[1]]
        f_value_to_byte(v_bytes, value)
        return ret_cmd(True, v_bytes)
        
    return ERR_OP_2
        
    
def ADD_cmd(ops, cmd=""):
    return ASMD_cmd_help(ops, cmd, 'ADD');
    
def SUB_cmd(ops, cmd=""):
    return ASMD_cmd_help(ops, cmd, 'SUB');

def MUL_cmd(ops, cmd=""):
    return ASMD_cmd_help(ops, cmd, 'MUL');

def DIV_cmd(ops, cmd=""):
    return ASMD_cmd_help(ops, cmd, 'DIV');

def MOV_cmd(ops, cmd=""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 2):
        return TOO_MANY_PARAMS
    if(op_len < 2):
        return TOO_FEW_PARAMS
    
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

    if(is_reg_1[0] == iGP_REG):
        is_num_2 = is_num(ops[1])
        if(not is_num_2[0]): return ERR_OP_2
        value = is_num_2[1]
        reg_bytes = is_reg_1[2]
        if(check_value(value, reg_bytes)): return TOO_BIG_OP_2_NUM
        v_bytes = [opcodes["MOV_RV"], is_reg_1[1]]
        value_to_byte(v_bytes, value, reg_bytes)
        return ret_cmd(True, v_bytes)
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
    pass


def INC_DEC_cmd_help(ops, cmd, prefix):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] != iGP_REG): return ERR_OP_1
    return ret_cmd(True, [opcodes[prefix+"_R"], is_reg_1[1]]);
        

def INC_cmd(ops, cmd = ""):
    return INC_DEC_cmd_help(ops, cmd, 'INC');

def DEC_cmd(ops, cmd = ""):
    return INC_DEC_cmd_help(ops, cmd, 'DEC');
    
def OUT_cmd(ops, cmd = ""):
    if(cmd != ""): return ERR_CMD
    op_len = len(ops)
    if(op_len > 1):
        return TOO_MANY_PARAMS
    if(op_len == 0):
        return TOO_FEW_PARAMS
    is_reg_1 = is_reg(ops[0])
    if(is_reg_1[0] == iGP_REG): 
        return ret_cmd(True, [opcodes["OUT_R"], is_reg_1[1]]);
    if(is_reg_1[0] == fGP_REG): 
        return ret_cmd(True, [opcodes["OUT_FR"], is_reg_1[1]]);

    c_str = ops[0].replace('\\n','\n')
    len_str = len(c_str)
    if(c_str[0] == '"' and c_str[len_str - 1] == '"'):
        c_str = c_str[1:(len_str - 1)]
        len_str -= 2;
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
        return ret_cmd(True, [opcodes["IN_R"], is_reg_1[1]]);
    if(is_reg_1[0] == fGP_REG): 
        return ret_cmd(True, [opcodes["IN_FR"], is_reg_1[1]]);
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
        is_num_2 = is_num(ops[1])
        if(not is_num_2[0]): return ERR_OP_2
        value = is_num_2[1]
        reg_bytes = is_reg_1[2]
        if(check_value(value, reg_bytes)): return TOO_BIG_OP_2_NUM
        v_bytes = [opcodes["CMP_REG_VAL"], is_reg_1[1]]
        value_to_byte(v_bytes, value, reg_bytes)
        return ret_cmd(True, v_bytes)
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

    return [False]
