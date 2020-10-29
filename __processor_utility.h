#pragma once

#ifndef PR_NOT_USER_CODE
#error only processor must use this header :|
#endif

#include "opcodes.h"

struct __proc_reg_int_info
{
    uint64_t value;
    enum REG_BYTES r_bytes;
    _Bool reg_error;
};
//return value of register by enum REG value (use for PUSH-REG)
struct __proc_reg_int_info
processor_reg_int_get_value(uint8_t reg_byte, Registers regs)
{
    #define x struct __proc_reg_int_info
    #define c(a, b) case a: return (x) { regs.##a, b, 0 }
    switch (reg_byte) {
        c(AL, REG_1B); //case AL: return (x) { regs.AL, REG_1B, 0 };
        c(BL, REG_1B); //case BL: return (x) { regs.AL, REG_1B, 0 };
        c(CL, REG_1B); //case CL: return (x) { regs.CL, REG_1B, 0 };
        c(DL, REG_1B); //case DL: return (x) { regs.DL, REG_1B, 0 };

        c(AX, REG_2B);
        c(BX, REG_2B);
        c(CX, REG_2B);
        c(DX, REG_2B);

        c(EAX, REG_4B);
        c(EBX, REG_4B);
        c(ECX, REG_4B);
        c(EDX, REG_4B);

        c(RAX, REG_8B);
        c(RBX, REG_8B);
        c(RCX, REG_8B);
        c(RDX, REG_8B);

    default:
        return (x) { 0, 0, .reg_error = 1 };
    }
    #undef c
    #undef x
}



struct __proc_reg_f_info
{
    double value;
    _Bool reg_error;
};
struct __proc_reg_f_info
processor_reg_f_get_value(uint8_t reg_byte, Registers regs)
{
    #define x struct __proc_reg_f_info
    #define c(a) case a: return (x) { regs.##a, 0 }
    switch (reg_byte) {
        c(FAX);
        c(FBX);
        c(FCX);
        c(FDX);
    default:
        return (x) { 0, .reg_error = 1 };
    }

    #undef c
    #undef x
}

struct __proc_reg_offset
{
    uint8_t reg_offset;
    enum REG_BYTES r_bytes;
    _Bool reg_error;
};
struct __proc_reg_offset
processor_reg_int_get_offset(uint8_t reg_byte)
{
    enum REG_BYTES bytes = reg_byte & 3;
    if (!bytes) bytes = REG_8B;
    #define x struct __proc_reg_offset
    switch (reg_byte) {
    case AL: case AX: case EAX: case RAX: return (x) { A_OFF, bytes, 0 };
    case BL: case BX: case EBX: case RBX: return (x) { B_OFF, bytes, 0 };
    case CL: case CX: case ECX: case RCX: return (x) { C_OFF, bytes, 0 };
    case DL: case DX: case EDX: case RDX: return (x) { D_OFF, bytes, 0 };
    default:
        return (x) { 0, 0, .reg_error = 1 };
    }
    #undef x
}

struct __proc_reg_offset
processor_reg_f_get_offset(uint8_t reg_byte)
{
    #define x struct __proc_reg_offset
    switch (reg_byte) {
    case FAX: return (x) { FA_OFF, REG_8B, 0 };
    case FBX: return (x) { FB_OFF, REG_8B, 0 };
    case FCX: return (x) { FC_OFF, REG_8B, 0 };
    case FDX: return (x) { FD_OFF, REG_8B, 0 };
    default:
        return (x) { 0, 1 };
    }
    #undef x
}

void processor_reg_get_ptr()
{

}
