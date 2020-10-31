opcodes = { #not prefix of cmd, but distinct cmd
    #CBC = CAN BE CMD
    #PUSH:
    'PUSHD'    : 4, #CBC
    'PUSH_4'   : 4, #CBC
    'PUSHQ'    : 5, #CBC
    'PUSH_8'   : 5, #CBC
    'PUSH_EAX' : 6, 
    'PUSH_F'   : 7, #CBC
    #'FLD'      : 7, #TODO:DEL
    'PUSH_REG' : 1,
    'PUSH_FREG': 2,

    'PUSH_FAX' : 9,

    #POP:
    'POPD'     : 8, #CBC
    'POP_4'    : 8, #CBC
    'POP_EAX'  : 0x0A,
    'POP_F'    : 0x0B,#CBC
    'POP_FAX'  : 0x0C,
    'POP_REG'  : 0x0D,
    'POP_FREG' : 0x0E,

    #ADD:
    'ADD_PPP'  : 0x10, #PPP : POP POP PUSH
    'ADD_F'    : 0x11, #CBC
    'ADD_RV'   : 0x12,
    'ADD_RR'   : 0x13,
    'ADD_FRV'  : 0x14,
    'ADD_FRFR' : 0x15,

    #SUB:
    'SUB_PPP'  : 0x18, #PPP : POP POP PUSH
    'SUB_F'    : 0x19, #CBC
    'SUB_RV'   : 0x1A,
    'SUB_RR'   : 0x1B,
    'SUB_FRV'  : 0x1C,
    'SUB_FRFR' : 0x1D,

    #MUL:
    'MUL_PPP'  : 0x20, #PPP : POP POP (PUSHx2)
    'MUL_F'    : 0x21, #CBC
    'MUL_RV'   : 0x22,
    'MUL_RR'   : 0x23,
    'MUL_FRV'  : 0x24,
    'MUL_FRFR' : 0x25,

    #DIV:
    'DIV_PPP'  : 0x28, #PPP : POP POP (PUSHx2)
    'DIV_F'    : 0x29, #CBC
    'DIV_RV'   : 0x2A,
    'DIV_RR'   : 0x2B,
    'DIV_FRV'  : 0x2C,
    'DIV_FRFR' : 0x2D,

    #MOV:
    'MOV_RV'   : 0x30,
    'MOV_FRV'  : 0x31,
    'MOV_RR'   : 0x32,
    'MOV_FRFR' : 0x33,
    'MOV_RFR'  : 0x34,
    'MOV_FRR'  : 0x35,

    #JUMP:
    'JUMP_D'   : 0x38,
    'JUMP_A'   : 0x39, 
    'JUMP_IF_D': 0x3A,  
    'JUMP_IF_A': 0x3B,

    #INC/DEC:
    'INC_R'    : 0x3C,
    'DEC_R'    : 0x3D,

    #OUT:
    'OUT_R'    : 0x3E,
    'OUT_FR'   : 0x3F,
    'OUT_C_STR': 0x40,

    #IN:
    'IN_R'     : 0x41,
    'IN_FR'    : 0x42,

    'HLT'      : 0x43,
    }
