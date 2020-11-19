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
        s = s[1:]
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
MAX_VALUE = {
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

NOT_REG = 0
iGP_REG = 1
fGP_REG = 2
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
