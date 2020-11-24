#pragma once
#ifndef PROCESSOR_OPCODES
#define PROCESSOR_OPCODES
#include <stdint.h>

enum {PROC_MAX_CMD_LEN = 2};

//if (opcode_byte & OpCodeOneMoreByte) => the next byte also belongs to the cmd
enum{OpCodeOneMoreByte = 0x80}; 

//opcode = opcode_byte & OpCodeByte
enum{OpCodeByte = 0x7F};

//postfix _F mean float point instr (double)
enum OpCode_1_byte
{
    PUSH = 0b100,
    PUSHD = PUSH, // 1 value-operand
    PUSH_4 = PUSH, // 1 value-operand
    PUSHQ = 0b101,
    PUSH_8 = PUSHQ, // 1 value-operand
    PUSH_EAX = 0b110, // 0 operand : EAX i.e. 32 byte more comfortable
    PUSH_F = 0b111, // 1 value-operand when we push double
    FLD = 0b111, // another name for PUSH_FAX instruction
    PUSH_REG_1B = 0b001,  // 1 reg-operand 
    PUSH_F_REG_1B = 0b010, // 1 reg-operand 

    PUSH_FAX = 0b1001, // 0 operand 

    POP = 0b1000, // 0 operand
    //RESERVED FOR:PUSH_FAX  0b1001
    POP_EAX = 0b1010, // 0 operand : EAX i.e. 32 byte more comfortable
    POP_F = 0b1011, // 0 operand 
    POP_FAX = 0b1100, // 0 operand
    POP_REG_1B = 0b1101,
    POP_F_REG_1B = 0b1110,

    ADD = 0x10, // 0 operand : x = POP, y = POP, PUSH x+y
    ADD_F, // 0 operand : x = POP_F, y = POP_F, PUSH_F x+y
    ADD_REG_VAL = 0x12,// 2 operand: ADD reg, x :=  reg = reg + x;  !ATTENTION : x has the same amount bytes as reg
    ADD_REG_REG = 0x13,// 2 operand: ADD reg1, reg2 := reg1 = reg1 + reg2 
    ADD_F_REG_VAL = 0x14,//2 operand: ADD f_reg, (double)x
    ADD_F_REG_REG = 0x15,//2 operand: ADD f_reg, f_reg
    #pragma region NOW N.T REALISED +++
    ADD_REG_CONST_PTR = 0x16, // ADD eax, [4*x + 3]
    ADD_REG_NOT_CONST_PTR = OpCodeOneMoreByte | ADD_REG_CONST_PTR, // ADD eax, [4*ecx + 3]
    ADD_FREG_CONST_PTR = 0x17,
    ADD_FREG_NOT_CONST_PTR = OpCodeOneMoreByte | ADD_FREG_CONST_PTR,
    #pragma endregion

    SUB = 0x18, // 0 operand : x = POP, y = POP, PUSH x-y
    SUB_F, // 0 operand : x = POP_F, y = POP_F, PUSH_F x-y
    SUB_REG_VAL = 0x1A,// 2 operand: SUB reg, x :=  reg = reg - x;  !ATTENTION : x has the same amount bytes as reg
    SUB_REG_REG = 0x1B,// 2 operand: SUB reg1, reg2 := reg1 = reg1 - reg2 
    SUB_F_REG_VAL = 0x1C,//2 operand: SUB f_reg, (double)x
    SUB_F_REG_REG = 0x1D,//2 operand: SUB f_reg, f_reg
    #pragma region NOW N.T REALISED +++
    SUB_REG_CONST_PTR = 0x1E, // SUB eax, [4*x + 3]
    SUB_REG_NOT_CONST_PTR = OpCodeOneMoreByte | SUB_REG_CONST_PTR, // SUB eax, [4*ecx + 3]
    SUB_FREG_CONST_PTR = 0x1F,
    SUB_FREG_NOT_CONST_PTR = OpCodeOneMoreByte | SUB_FREG_CONST_PTR,
    #pragma endregion

    MUL = 0x20, // 0 operand : x = POP, y = POP, PUSH (first 32)(x*y); PUSH (x*y) >> 32;
    MUL_F, // 0 operand : x = POP_F, y = POP_F, PUSH_F x*y
    MUL_REG_VAL = 0x22,// 2 operand: MUL reg, x :=  reg = reg * x;  !ATTENTION : x has the same amount bytes as reg
    MUL_REG_REG = 0x23,// 2 operand: MUL reg1, reg2 := reg1 = reg1 * reg2 
    MUL_F_REG_VAL = 0x24,//2 operand: MUL f_reg, (double)x
    MUL_F_REG_REG = 0x25,//2 operand: MUL f_reg, f_reg
    #pragma region NOW N.T REALISED +++
    MUL_REG_CONST_PTR = 0x26, // MUL eax, [4*x + 3]
    MUL_REG_NOT_CONST_PTR = OpCodeOneMoreByte | MUL_REG_CONST_PTR, // MUL eax, [4*ecx + 3]
    MUL_FREG_CONST_PTR = 0x27,
    MUL_FREG_NOT_CONST_PTR = OpCodeOneMoreByte | MUL_FREG_CONST_PTR,
    #pragma endregion

    DIV = 0x28, // 0 operand : x = POP, y = POP, PUSH x/y
    DIV_F, // 0 operand : x = POP_F, y = POP_F, PUSH_F x/y
    DIV_REG_VAL = 0x2A,// 2 operand: MUL reg, x :=  reg = reg / x;  !ATTENTION : x has the same amount bytes as reg
    DIV_REG_REG = 0x2B,// 2 operand: MUL reg1, reg2 := reg1 = reg1 / reg2 
    DIV_F_REG_VAL = 0x2C,//2 operand: MUL f_reg, (double)x
    DIV_F_REG_REG = 0x2D,//2 operand: MUL f_reg, f_reg
    #pragma region NOW N.T REALISED +++
    DIV_REG_CONST_PTR = 0x2E, // DIV eax, [4*x + 3]
    DIV_REG_NOT_CONST_PTR = OpCodeOneMoreByte | DIV_REG_CONST_PTR, // DIV eax, [4*ecx + 3]
    DIV_FREG_CONST_PTR = 0x2F,
    DIV_FREG_NOT_CONST_PTR = OpCodeOneMoreByte | DIV_FREG_CONST_PTR,
    #pragma endregion

    MOV_REG_VAL = 0x30,
    MOV_F_REG_VAL,
    MOV_REG_REG,
    MOV_FREG_FREG,
    MOV_REG_FREG,
    MOV_FREG_REG,
    #pragma region NOW N.T REALISED +++
    MOV_REG_CONST_PTR = 0x36, // MOV eax, [4*x + 3]
    MOV_REG_NOT_CONST_PTR = OpCodeOneMoreByte | MOV_REG_CONST_PTR, // MOV eax, [4*ecx + 3]
    MOV_FREG_CONST_PTR = 0x37,
    MOV_FREG_NOT_CONST_PTR = OpCodeOneMoreByte | MOV_FREG_CONST_PTR,
    
    MOV_CONST_PTR_REG = 0x4E, // MOV [x], eax
    MOV_CONST_PTR_FREG = 0x4F, 
    MOV_NOT_CONST_PTR_REG = OpCodeOneMoreByte | MOV_CONST_PTR_REG, // MOV [eax], ecx   ? MOV W[2*eax+3], ecx
    MOV_NOT_CONST_PTR_FREG = OpCodeOneMoreByte | MOV_CONST_PTR_FREG,//MOV [eax], edx
    #pragma endregion

    JUMP_DIFF = 0x38, // 1 [(ptrdiff_t) | int32_t] operand
    JUMP_ADDR, // 1 ptr operand
    JUMP_IF_DIFF, //the condition is set by the next byte 
    JUMP_IF_ADDR, //the condition is set by the next byte
    #pragma region NOW N.T REALISED +++
    JUMP_ADDR_REG = 0x4C, //JUMP EAX
    JUMP_IF_ADDR_REG = 0x4D,//JZ ECX
    #pragma endregion

    INC_REG = 0x3C,
    DEC_REG,

    OUT_REG,
    OUT_FREG,
    OUT_C_STRING,
    IN_REG, //64 bit
    IN_FREG,

    HLT,

    #pragma region NOW N.T REALISED +++
    CMP_REG_VAL = 0x44,
    CMP_REG_REG = 0x45,
    CMP_FREG_VAL = 0x46,
    CMP_FREG_FREG = 0x47,
    #pragma endregion

    #pragma region NOW NOT REALISED
    CALL_ADDR = 0x48,
    CALL_REG  = 0x49,
    RET       = 0x4A,
    #pragma endregion
    R_E_S_E_R_V_E_D__1 = 0x4B,
    R_E_S_E_R_V_E_D__JUMP_ADDR_REG = 0x4C,
    R_E_S_E_R_V_E_D__JUMP_IF_ADDR_REG = 0x4D,
    R_E_S_E_R_V_E_D__MOV_CONST_PTR_REG = 0x4E,
    R_E_S_E_R_V_E_D__MOV_CONST_PTR_FREG = 0x4F,

    #pragma region NOW N.T REALISED +++
    PASS = 0x50,
    #pragma endregion

    #pragma region NOW NOT REALISED
    OUT_CONST_PTR_C_STRING = 0x51, // OUT [next_line]
    #pragma endregion
};


enum REG
{
    AL = 0b001,
    AX = 0b010,
    EAX = 0b011,
    RAX = 0b100,

    BL = 0b0101,
    BX = 0b0110,
    EBX = 0b0111,
    RBX = 0b1000,

    CL,
    CX,
    ECX,
    RCX,

    DL,
    DX,
    EDX,
    RDX,

    #define x(n) \
    R##n##B,     \
    R##n##W,     \
    R##n##D,     \
    R##n        

    x(0),
    x(1),
    x(2),
    x(3),
    x(4),
    x(5),
    x(6),
    x(7),
    x(8),
    x(9),
    x(10),
    x(11),
    x(12),
    x(13),
    x(14),
    x(15),

    #undef x

    HEH_JUST_END_REG_NOT_USE_IT_VALUE_PLEASE,
};

enum FREG
{
    FAX = 1,
    FBX,
    FCX,
    FDX,

};

enum REG_BYTES
{
    REG_1B = 0x1, 
    REG_2B = 0x2, 
    REG_4B = 0x3, 
    REG_8B = 0x4, 

    #define x(n) FR##n

    x(0),
    x(1),
    x(2),
    x(3),
    x(4),
    x(5),
    x(6),
    x(7),
    x(8),
    x(9),
    x(10),
    x(11),
    x(12),
    x(13),
    x(14),
    x(15),

    #undef x

};

static const uint64_t REG_1B_MASK = 0xFF;
static const uint64_t REG_2B_MASK = 0xFFFF;
static const uint64_t REG_4B_MASK = 0xFFFFFFFF;
static const uint64_t REG_8B_MASK = 0xFFFFFFFFFFFFFFFF;
static const uint64_t REG_B_MASKS[4] = {0xFF, 0xFFFF, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF};
static const uint64_t REG_B_INV_MASKS[4] = {0xFFFFFFFFFFFFFF00, 0xFFFFFFFFFFFF0000, 0xFFFFFFFF00000000, 0x0};
static const uint64_t REG_LAST_BIT_MASKS[4] = {0x80, 0x8000, 0x80000000, 0x8000000000000000};

enum { REG_PTR = REG_4B };

enum TYPE_OF_REG
{
    iGP = 0x1,//general purpose integer register
    fGP = 0x2,//general purpose double register 
};


enum REG_FLAGS
{
    FL_Z = 0b1,  //ZERO
    FL_OF = 0b10,//OVERFLOW (unsigned)
    FL_AZ = 0b100, //ABOVE ZERO
    FL_MZ = 0b100, //MORE THAN ZERO
};

enum JUMP_IFS
{
    JIF_MIN_VALID = 1,
    JIF_Z = 1,//ZERO
    JIF_NZ,//NOT ZERO
    JIF_OF,//OVERFLOW
    JIF_AZ,//ABOVE ZERO
    JIF_AEZ,//ABOVE OR EQUAL ZERO
    JIF_LZ,//LESS THAN ZERO
    JIF_LEZ,//LESS OR EQUAL ZERO

    JIF_MAX_VALID = 7,

};
#endif