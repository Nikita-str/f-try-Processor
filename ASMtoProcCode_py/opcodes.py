ONE_MORE_CMD_BYTE = 0x80

OPCODE_PASS = 0x50

opcodes = { #not prefix of cmd, but distinct cmd
    #CBC = CAN BE CMD
    #CPTR - CONST_PTR
    #NCPTR - NOT_CONST_PTR
    #PUSH:
    'PUSHD'    : 4, #CBC
    'PUSH_4'   : 4, #CBC
    'PUSHQ'    : 5, #CBC
    'PUSH_8'   : 5, #CBC
    'PUSH_EAX' : 6, 
    'PUSH_F'   : 7, #CBC
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
    'ADD_REG_CPTR'   : 0x16, #TODO:NEW
    'ADD_REG_NCPTR'  : 0x16 | ONE_MORE_CMD_BYTE, #TODO:NEW
    'ADD_FREG_CPTR'  : 0x17, #TODO:NEW
    'ADD_FREG_NCPTR' : 0x17 | ONE_MORE_CMD_BYTE, #TODO:NEW


    #SUB:
    'SUB_PPP'  : 0x18, #PPP : POP POP PUSH
    'SUB_F'    : 0x19, #CBC
    'SUB_RV'   : 0x1A,
    'SUB_RR'   : 0x1B,
    'SUB_FRV'  : 0x1C,
    'SUB_FRFR' : 0x1D,
    'SUB_REG_CPTR'   : 0x1E, #TODO:NEW
    'SUB_REG_NCPTR'  : 0x1E | ONE_MORE_CMD_BYTE, #TODO:NEW
    'SUB_FREG_CPTR'  : 0x1F, #TODO:NEW
    'SUB_FREG_NCPTR' : 0x1F | ONE_MORE_CMD_BYTE, #TODO:NEW

    #MUL:
    'MUL_PPP'  : 0x20, #PPP : POP POP (PUSHx2)
    'MUL_F'    : 0x21, #CBC
    'MUL_RV'   : 0x22,
    'MUL_RR'   : 0x23,
    'MUL_FRV'  : 0x24,
    'MUL_FRFR' : 0x25,
    'MUL_REG_CPTR'   : 0x26, #TODO:NEW
    'MUL_REG_NCPTR'  : 0x26 | ONE_MORE_CMD_BYTE, #TODO:NEW
    'MUL_FREG_CPTR'  : 0x27, #TODO:NEW
    'MUL_FREG_NCPTR' : 0x27 | ONE_MORE_CMD_BYTE, #TODO:NEW

    #DIV:
    'DIV_PPP'  : 0x28, #PPP : POP POP (PUSHx2)
    'DIV_F'    : 0x29, #CBC
    'DIV_RV'   : 0x2A,
    'DIV_RR'   : 0x2B,
    'DIV_FRV'  : 0x2C,
    'DIV_FRFR' : 0x2D,
    'DIV_REG_CPTR'   : 0x2E, #TODO:NEW
    'DIV_REG_NCPTR'  : 0x2E | ONE_MORE_CMD_BYTE, #TODO:NEW
    'DIV_FREG_CPTR'  : 0x2F, #TODO:NEW
    'DIV_FREG_NCPTR' : 0x2F | ONE_MORE_CMD_BYTE, #TODO:NEW


    #MOV:
    'MOV_RV'   : 0x30,
    'MOV_FRV'  : 0x31,
    'MOV_RR'   : 0x32,
    'MOV_FRFR' : 0x33,
    'MOV_RFR'  : 0x34,
    'MOV_FRR'  : 0x35,
    'MOV_REG_CPTR'   : 0x36, #TODO:NEW
    'MOV_REG_NCPTR'  : 0x36 | ONE_MORE_CMD_BYTE, #TODO:NEW
    'MOV_FREG_CPTR'  : 0x37, #TODO:NEW
    'MOV_FREG_NCPTR' : 0x37 | ONE_MORE_CMD_BYTE, #TODO:NEW
    'MOV_CPTR_REG'   : 0x4E, #TODO:NEW
    'MOV_NCPTR_REG'  : 0x4E | ONE_MORE_CMD_BYTE, #TODO:NEW
    'MOV_CPTR_FREG'  : 0x4F, #TODO:NEW
    'MOV_NCPTR_FREG' : 0x4F | ONE_MORE_CMD_BYTE, #TODO:NEW


    #JUMP:
    #TODO:+NEW
    'JUMP_D'   : 0x38,
    'JUMP_A'   : 0x39, 
    'JUMP_IF_D': 0x3A,  
    'JUMP_IF_A': 0x3B,
    'JUMP_ADDR_REG'    : 0x4C, 
    'JUMP_IF_ADDR_REG' : 0x4D,

    #INC/DEC:
    'INC_R'    : 0x3C,
    'DEC_R'    : 0x3D,

    #OUT:
    'OUT_R'    : 0x3E,
    'OUT_FR'   : 0x3F,
    'OUT_C_STR': 0x40,
    'OUT_CPTR_C_STR' : 0x51,

    #IN:
    'IN_R'     : 0x41,
    'IN_FR'    : 0x42,

    'HLT'      : 0x43,
    
    'CMP_REG_VAL'   : 0x44, #TODO:+NEW
    'CMP_REG_REG'   : 0x45, #TODO:+NEW
    'CMP_FREG_VAL'  : 0x46, #TODO:+NEW
    'CMP_FREG_FREG' : 0x47, #TODO:+NEW
    
    #NOT REALISED:
    #CALL_ADDR = 0x48,
    #CALL_REG  = 0x49,
    #RET       = 0x4A,

    'PASS' : OPCODE_PASS, #TODO:+NEW

    #0x51:OUT_CPTR_C_STR
    }

jump_cmds = {
    'JZ' : 1,  #JUMP IF ZERO
    'JE' : 1, #JUMP IF EQUAL
    'JNZ' : 2, #JUMP IF NOT ZERO
    'JNE' : 2, #JUMP IF NOT EQUAL
    'JOF' : 3, #JUMP IF OVERFLOW
    'JAZ' : 4, #JUMP IF ABOVE ZERO
    'JAZZ' : 4,
    'JAEZ' : 5,#J IF ABOVE OR EQUAL ZERO
    'JLZ' : 6, #J IF LESS ZERO
    'JLEZ' : 7,#J IF LESS OR EQUAL ZERO
    }
