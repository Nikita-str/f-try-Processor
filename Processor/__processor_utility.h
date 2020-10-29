#pragma once

#ifndef PROCESSOR_CODE
#error only processor must use this header :|
#endif

#include <assert.h>
#include <stdint.h>
#include "opcodes.h"

struct __proc_reg
{
    void *reg_ptr;
    uint64_t *flags_ptr;
    enum REG_BYTES reg_bytes;
    _Bool reg_error;
};

/// <summary>return ptr on register</summary>
/// <param name="type_of_reg">TYPE_OF_REG</param>
struct __proc_reg
    processor_reg_get_ptr(uint8_t type_of_reg, uint8_t reg_byte, Registers regs)
{
    enum {REG_OK = 0 };
    enum {REG_ERROR = 1 };
    #define x struct __proc_reg
    switch (type_of_reg) {
    case iGP:
    {
        enum REG_BYTES bytes = reg_byte & 3;
        if (!bytes) bytes = REG_8B;
        switch (reg_byte) {
            //c(r) mean case(reg distinctive char), for example, r = A => AL, AX, EAX, RAX 
            #define c(r) case r##L: case r##X: case E##r##X: case R##r##X: return (x) { &(regs.R##r##X), &(regs.FLAGS), bytes, REG_OK };
            c(A);
            c(B);
            c(C);
            c(D);
            #undef c
        }
    }
    case fGP:
    {
        enum REG_BYTES bytes = REG_8B;
        switch (reg_byte) {
            #define c(reg_dist_char) case reg_dist_char: return (x) { &(regs.##reg_dist_char), &(regs.FLAGS), bytes, REG_OK };
            c(FAX);
            c(FBX);
            c(FCX);
            c(FDX);
            #undef c
        }
    }
    }
    return (x){NULL, NULL, 0, .reg_error = REG_ERROR};
    #undef x
}

//TODO:memcpy
uint64_t __read_n(int n, void *ptr)
{
    //MAYBE:CHECK THAT n is 1/2/4/8 ?
    assert(n == 1 || n == 2 || n == 4 || n == 8);
    uint64_t value = 0;
    memcpy(&value, ptr, n);
    return value;
}

inline double __d_read_n(void *ptr)
{
    double value = 0;
    memcpy(&value, ptr, sizeof(double));
    return value;
}


uint64_t get_reg_value(struct __proc_reg pr)
{
    switch (pr.reg_bytes) {
    case REG_1B: return ((uint8_t *)pr.reg_ptr)[0];
    case REG_2B: return ((uint16_t *)pr.reg_ptr)[0];
    case REG_4B: return ((uint32_t *)pr.reg_ptr)[0];
    case REG_8B: return ((uint64_t *)pr.reg_ptr)[0];
    default: assert("error"); return 0;
    }
}

void set_reg_value(struct __proc_reg pr, uint64_t value)
{
    switch (pr.reg_bytes) {
    case REG_1B: ((uint8_t *)pr.reg_ptr)[0] = (uint8_t)value; break;
    case REG_2B: ((uint16_t *)pr.reg_ptr)[0] = (uint16_t)value; break;
    case REG_4B: ((uint32_t *)pr.reg_ptr)[0] = (uint32_t)value; break;
    case REG_8B: ((uint64_t *)pr.reg_ptr)[0] = value; break;
    default: assert("error");
    }

    pr.flags_ptr[0] = 0;
    int ind = pr.reg_bytes - 1;
    if (!(value & REG_B_MASKS[ind]))pr.flags_ptr[0] |= FL_Z;
    if(value & REG_B_INV_MASKS[ind])pr.flags_ptr[0] |= FL_OF; //TODO : WE CANT CATCH OVERFLOW WITH 8byte-reg in that way ://
    if (value & REG_LAST_BIT_MASKS[ind])pr.flags_ptr[0] |= FL_AZ;
}


inline double get_f_reg_value(struct __proc_reg pr)
{
    return ((double *)pr.reg_ptr)[0];
}

inline void set_f_reg_value(struct __proc_reg pr, double value)
{
    ((double *)pr.reg_ptr)[0] = value;
    pr.flags_ptr[0] = 0;
    if(DoubleEqualZero(value))pr.flags_ptr[0] |= FL_Z;
    if(DoubleAboveZero(value))pr.flags_ptr[0] |= FL_AZ;
}

/// <summary> </summary>
/// <param name="flags"></param>
/// <param name="if_byte">only valid byte myst pass here, in other case will return 0</param>
/// <returns></returns>
_Bool proc_check_condition(uint64_t flags, uint8_t if_byte)
{
    switch (if_byte) {
    case JIF_Z: return (flags & FL_Z);
    case JIF_NZ: return !(flags & FL_Z);
    case JIF_OF: return (flags & FL_OF);
    case JIF_AZ: return (flags & FL_AZ);
    case JIF_AEZ: return (flags & FL_AZ) || (flags & FL_Z);
    case JIF_LZ: return !((flags & FL_AZ) || (flags & FL_Z));
    case JIF_LEZ: return !(flags & FL_AZ);
    }
    return 0;
}