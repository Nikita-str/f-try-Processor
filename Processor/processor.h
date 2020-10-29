#pragma once
#define _CRT_SECURE_NO_WARNINGS

#include <stdint.h>

typedef int32_t iproc_t;
typedef int64_t i2proc_t;

typedef uint32_t proc_ptr_t;
typedef int32_t proc_delta_ptr_t;


#include "Stack/GenericStackSetEmptyConfig.h"
#define WITHOUT_AUTO_CHECK_VALID
#define GENERIC_STACK_TYPE iproc_t
#include "Stack/GenericStack.h"
#undef GENERIC_STACK_TYPE
#define GENERIC_STACK_TYPE double
#include "Stack/GenericStack.h"
#undef GENERIC_STACK_TYPE

#include "opcodes.h"


typedef struct Registers
{
    //TODO: hmm.. i think there is no sence in 8 & 16 bit regs
    union
    {
        int8_t AL;
        int16_t AX;
        int32_t EAX;
        int64_t RAX;
    };
    union
    {
        int8_t BL;
        int16_t BX;
        int32_t EBX;
        int64_t RBX;
    };
    union
    {
        int8_t CL;
        int16_t CX;
        int32_t ECX;
        int64_t RCX;
    };
    union
    {
        int8_t DL;
        int16_t DX;
        int32_t EDX;
        int64_t RDX;
    };

    //F mean with float point(double)

    double FAX;
    double FBX;
    double FCX;
    double FDX;

    

    uint64_t FLAGS;

    proc_ptr_t RIP; 

    //it slightly hard : int64_t RSP;
}Registers;

typedef struct Memory
{
    uint8_t *memory; 
    //TODO:
    //MAYBE:DO:MEMORY WITH FLAGS ? (EXECUTE / ...) 
    //      for example: uint8_t *flags; //each n:bit(where n = 1 or 2, in other cases it's expensive) responsible for corresp. byte
}Memory;

typedef struct Processor
{   
    generic_stack(iproc_t) *stack; // ?  
    generic_stack(double) *stack_f; // ?  
    Registers reg;
    Memory mem;
}Processor;


