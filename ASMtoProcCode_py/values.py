import struct
from registers import *;

def is_num(s):
    ord_0 = ord('0')
    ord_A = ord('A')
    ord__ = ord('_')
    value = 0
    _hex = False
    neg = False
    if(s[0] == '-'):
        neg = True
        s = s[1:].lstrip()
    if(s[0:2]== '0x' or s[0:2]== '0X'):
        _hex = True
        s = s[2:]
    last_num = False
    for c in s:
        c_i = ord(c)
        if(c_i == ord__): last_num = False; continue;
        c_i -= ord_0
        last_num = True;
        if(0 <= c_i and c_i <= 9):
            if(_hex): value = value*16 + c_i
            else : value = value*10 + c_i
            continue;
        c_i = c_i+ord_0-ord_A
        if(_hex and 0 <= c_i and c_i <= 5):
             value = value*16 + c_i+10;
             continue;
        return [False]
    if(not last_num): return [False]
    if(neg): return [True, -value]
    return [True, value]
MAX_VALUE = { #first F --> 7 ?
    1 : 0xFF,
    2 : 0xFFFF,
    4 : 0xFFFF_FFFF,
    8 : 0xFFFF_FFFF_FFFF_FFFF,
    }
ADD_NEG_VALUE = {
    1 : 0x80,
    2 : 0x8000,
    4 : 0x8000_0000,
    8 : 0x8000_0000_0000_0000,
    }
BYTE = 0xFF
PTR_BYTE = 4;

def value_to_byte(v_bytes, value, n_byte):
    global BYTE    
    for i in range(n_byte):
        v_bytes += [value & BYTE]
        value = value >> 8
    return v_bytes

def is_fnum(s):
    try:
        return [True, float(s)]
    except:
        return [False]

def f_value_to_byte(v_bytes, value):
    for b in bytearray(struct.pack("d", value)):
        v_bytes += [b]
    return v_bytes

def check_value(value, n_byte):
    global ADD_NEG_VALUE, MAX_VALUE   
    return (value < 0 and value + ADD_NEG_VALUE[n_byte] < 0) or (value > MAX_VALUE[n_byte]);  

def is_valid_value(value, n_byte): return not check_value(value, n_byte)

#for mul subable = False, for add/sub: True
#for mul zero_byte_value = 1; for add/sub = 0;
def need_bytes_for_ptr_value(ptr_value, zero_byte_value, subable = False):
    if(ptr_value == zero_byte_value): return 0
    need_bytes = 0
    if(subable and ptr_value < 0): ptr_value = -ptr_value;
    while ptr_value != 0:
        ptr_value = ptr_value // BYTE;
        need_bytes += 1
    if(need_bytes == 0): need_bytes = 1;
    return need_bytes
    

NOT_REG = 0
NOT_PTR_REG = 0
iGP_REG = 1
fGP_REG = 2
IS_PTR_REG = 3
def is_reg(s):
    reg_init();
    reg = regs_index.get(s)
    if(reg):
        reg_bytes = 0
        if((reg & 3) == 0): reg_bytes = 8
        else: reg_bytes = (1 << ((reg&3) - 1))
        return [iGP_REG, reg, reg_bytes, s == 'EAX'] 
    freg = fregs_index.get(s)
    if(freg): return [fGP_REG, freg, 8, s == 'FAX']
    return [NOT_REG];

def is_ptr_reg(s):
    temp = is_reg(s)
    if(len(z) == 1):return [NOT_PTR_REG];
    if(temp[0] != iGP_REG or temp[2] != PTR_BYTE):return [NOT_PTR_REG]
    return [IS_PTR_REG, temp[1]]


def valid_name(name):
    global regs_index;
    reg_init();
    if(len(name) == 0):return(False, 'empty name is unallowable')
    if(name.upper() in regs_index):return (False, 'that name used for register')
    if('0'<=name[0] and name[0]<='9'):return (False, "name can't start from number")
    for c in name:
        if(('a'<=c and c<='z') or (c=='_') or ('0'<=c and c<='9')): continue
        return (False, "in name may be only chars from [a..z | 0..9 | _]  error char: '"+c+"'")
    return (True, '')

     
