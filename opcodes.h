#pragma once

//if (opcode_byte & OpCodeOneMoreByte) => the next byte also belongs to the cmd
enum{OpCodeOneMoreByte = 0x80}; 

//opcode = opcode_byte & OpCodeByte
enum{OpCodeByte = 0x7F};


//postfix _F mean float point instr (double)
enum OpCode_1_byte
{
    PUSH     = 0b100,
    PUSH_4   = 0b100, // 1 value-operand
    PUSH_8   = 0b101, // 1 value-operand
    PUSH_EAX = 0b110, // 0 operand : EAX i.e. 32 byte more comfortable
    PUSH_F   = 0b111, // 1 value-operand when we push double
    FLD      = 0b111, // another name for PUSH_FAX instruction
    PUSH_REG_1B = PUSH | OpCodeOneMoreByte,  // 1 reg-operand 
    PUSH_F_REG_1B = PUSH_F | OpCodeOneMoreByte, // 1 reg-operand 

    PUSH_FAX = 0b1001, // 0 operand 

    POP      = 0b1000, // 0 operand
    //RESERVED FOR:PUSH_FAX  0b1001
    POP_EAX  = 0b1010, // 0 operand : EAX i.e. 32 byte more comfortable
    POP_F    = 0b1011, // 0 operand 
    POP_FAX  = 0b1100, // 0 operand
    POP_REG_1B = POP | OpCodeOneMoreByte,
    POP_F_REG_1B = POP_F | OpCodeOneMoreByte,

};

enum REG
{
     AL = 0b001,
     AX = 0b010,
    EAX = 0b011,
    RAX = 0b100,

    BL  = 0b0101,
    BX  = 0b0110,
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
};

enum TYPE_OF_REG
{
    iGP,//general purpose
    fGP,
};