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
    'POP_EAX'  : 10,
    'POP_F'    : 11,#CBC
    'POP_FAX'  : 12,
    'POP_REG'  : 13,
    'POP_FREG' : 14,

    #ADD:
    'ADD_PPP'  : 16, #PPP : POP POP PUSH
    'ADD_F'    : 17, #CBC
    'ADD_RV'   : 18,
    'ADD_RR'   : 19,
    'ADD_FRV'  : 20,
    'ADD_FRFR' : 21,

    #SUB:
    'SUB_PPP'  : 24, #PPP : POP POP PUSH
    'SUB_F'    : 25, #CBC
    'SUB_RV'   : 26,
    'SUB_RR'   : 27,
    'SUB_FRV'  : 28,
    'SUB_FRFR' : 29,

    #MUL:
    'MUL_PPP'  : 32, #PPP : POP POP (PUSHx2)
    'MUL_F'    : 33, #CBC
    'MUL_RV'   : 34,
    'MUL_RR'   : 35,
    'MUL_FRV'  : 36,
    'MUL_FRFR' : 37,

    #DIV:
    'DIV_PPP'  : 40, #PPP : POP POP (PUSHx2)
    'DIV_F'    : 41, #CBC
    'DIV_RV'   : 42,
    'DIV_RR'   : 43,
    'DIV_FRV'  : 44,
    'DIV_FRFR' : 45,

    #MOV:
    'MOV_RV'   : 48,
    'MOV_FRV'  : 49,
    'MOV_RR'   : 50,
    'MOV_FRFR' : 51,
    'MOV_RFR'  : 52,
    'MOV_FRR'  : 53,

    #JUMP:
    'JUMP_D'   : 56,
    'JUMP_A'   : 57, 
    'JUMP_IF_D': 58,  
    'JUMP_IF_A': 59,

    #INC/DEC:
    'INC_R'    : 60,
    'DEC_R'    : 61,

    #OUT:
    'OUT_R'    : 62,
    'OUT_FR'   : 63,
    'OUT_C_STR': 64,

    #IN:
    'IN_R'     : 65,
    'IN_FR'    : 66,
    }
