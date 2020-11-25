#pragma once

#ifndef PROCESSOR_CODE
#error only processor must use this header :|
#endif

#include <assert.h>
#include <stdint.h>
#include "opcodes.h"
#include "processor.h"
#include "Auxiliary/generic_function.h"

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
processor_reg_get_ptr(uint8_t type_of_reg, uint8_t reg_byte, Processor *proc)
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
            #define c(r) case r##L: case r##X: case E##r##X: case R##r##X: return (x) { &(proc->reg.R##r##X), &(proc->reg.FLAGS), bytes, REG_OK };
            c(A);
            c(B);
            c(C);
            c(D);
            #undef c
            #define c(n) case R##n##B: case R##n##W: case R##n##D: case R##n: return (x) { &(proc->reg.R##n), &(proc->reg.FLAGS), bytes, REG_OK };
            c(0);
            c(1);
            c(2);
            c(3);
            c(4);
            c(5);
            c(6);
            c(7);
            c(8);
            c(9);
            c(10);
            c(11);
            c(12);
            c(13);
            c(14);
            c(15);
            #undef c
        }
    }
    case fGP:
    {
        enum REG_BYTES bytes = REG_8B;
        switch (reg_byte) {
            #define c(r) case F##r##X: return (x) { &(proc->reg.F##r##X), &(proc->reg.FLAGS), bytes, REG_OK };
            c(A);
            c(B);
            c(C);
            c(D);
            #undef c
            #define c(n) case FR##n: return (x) { &(proc->reg.FR##n), &(proc->reg.FLAGS), bytes, REG_OK };
            c(0);
            c(1);
            c(2);
            c(3);
            c(4);
            c(5);
            c(6);
            c(7);
            c(8);
            c(9);
            c(10);
            c(11);
            c(12);
            c(13);
            c(14);
            c(15);
            #undef c
        }
    }
    }
    return (x){NULL, NULL, 0, .reg_error = REG_ERROR};
    #undef x
}

uint64_t __read_n(int n, void *ptr)
{
    //MAYBE:CHECK THAT n is 1/2/4/8 ? or not... for example 3 already use  
    assert(n == 1 || n == 2 || n == 3 || n == 4 || n == 8);
    uint64_t value = 0;
    memcpy(&value, ptr, n);
    return value;
}

//not use
static inline void __write_value_n(int n, uint64_t value, void *ptr)
{
    memcpy(ptr, &value, n);
}

static inline double __d_read_n(void *ptr)
{
    double value = 0;
    memcpy(&value, ptr, sizeof(double));
    return value;
}

//not use
static inline void __d_write_value(double value, void *ptr)
{
    memcpy(ptr, &value, sizeof(double));
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

void upd_reg_flags(struct __proc_reg pr, uint64_t value)
{
    pr.flags_ptr[0] = 0;
    int ind = pr.reg_bytes - 1;
    if (!(value & REG_B_MASKS[ind]))pr.flags_ptr[0] |= FL_Z;
    if (value & REG_B_INV_MASKS[ind])pr.flags_ptr[0] |= FL_OF; //TODO : WE CANT CATCH OVERFLOW WITH 8byte-reg in that way ://
    if (value & REG_LAST_BIT_MASKS[ind])pr.flags_ptr[0] |= FL_AZ;
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

    upd_reg_flags(pr, value);
}


static inline double get_f_reg_value(struct __proc_reg pr)
{
    return ((double *)pr.reg_ptr)[0];
}

static inline void upd_freg_flags(struct __proc_reg pr, double value)
{
    pr.flags_ptr[0] = 0;
    if (DoubleEqualZero(value))pr.flags_ptr[0] |= FL_Z;
    if (DoubleAboveZero(value))pr.flags_ptr[0] |= FL_AZ;
}

static inline void set_f_reg_value(struct __proc_reg pr, double value)
{
    ((double *)pr.reg_ptr)[0] = value;
    upd_freg_flags(pr, value);
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

proc_ptr_t get_not_const_ptr(uint8_t cmd_get_not_const_ptr_byte, Processor *proc, proc_ptr_t *instead_rip, enum PROC_CMD_ERROR *error)
{
    *error = NO_ERROR;
    static const uint8_t no_such_cmd = 0b11110000;
    if (cmd_get_not_const_ptr_byte & no_such_cmd) { *error = NO_SUCH_CMD; return 0; }//0 is valid address
    uint8_t byte_for_add = cmd_get_not_const_ptr_byte & 0b0011;
    uint8_t byte_for_mul = (cmd_get_not_const_ptr_byte & 0b1100) >> 2;
    uint32_t mul = 1;
    uint32_t add = 0;

    //read ptr reg:
    uint8_t reg_byte = (uint8_t)__read_n(sizeof(reg_byte), (void *)(proc->mem.memory + *instead_rip));
    (*instead_rip) += sizeof(reg_byte);
    struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
    if (pr.reg_error) {*error = REG_ERROR; return 0; }
    if (pr.reg_bytes != REG_PTR) { *error = NO_REG_PTR; return 0; }

    if (byte_for_mul) {//read mul
        mul = (uint32_t)__read_n(byte_for_mul, (void *)(proc->mem.memory + *instead_rip));
        (*instead_rip) += byte_for_mul;
    }
    if (byte_for_add) {//read add
        add = (uint32_t)__read_n(byte_for_add, (void *)(proc->mem.memory + *instead_rip));
        (*instead_rip) += byte_for_add;
    }

    return (proc_ptr_t)(mul * get_reg_value(pr) + add);
}