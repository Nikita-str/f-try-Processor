#pragma once
#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include <stdint.h>
#include <string.h>

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

    // +++++++       REG Rn RnD ... RnB
    #define x(n)           \
    union                  \
    {                      \
        int8_t R##n##B;    \
        int16_t R##n##W;    \
        int32_t R##n##D;    \
        int64_t R##n;       \
    }

    x(0);
    x(1);
    x(2);
    x(3);
    x(4);
    x(5);
    x(6);
    x(7);
    x(8);
    x(9);
    x(10);
    x(11);
    x(12);
    x(13);
    x(14);
    x(15);

    #undef x
    // -----       REG RnN

    //F mean with float point(double)

    double FAX;
    double FBX;
    double FCX;
    double FDX;

    // +++++       REG FRn    
    #define x(n) double FR##n

    x(0);
    x(1);
    x(2);
    x(3);
    x(4);
    x(5);
    x(6);
    x(7);
    x(8);
    x(9);
    x(10);
    x(11);
    x(12);
    x(13);
    x(14);
    x(15);

    #undef x
    // -----       REG FRn    

    uint64_t FLAGS;

    proc_ptr_t RIP; 

    //it slightly hard : int64_t RSP;
}Registers;

typedef struct Memory
{
    generic_stack(iproc_t) stack; // ?  
    generic_stack(double) stack_f; // ?  
    uint8_t *memory; 
    //TODO: size of memory
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


typedef enum PROC_CMD_ERROR//TODO:MOVE:processor.h
{
    NO_ERROR = 0x0,
    NO_SUCH_CMD = 0x1,
    POP_ERROR = 0x2,
    REG_ERROR = 0x3,
    FUTURE_ERROR = 0x4,//eah.. this for case of cyberpunk
    DIV_ZERO_ERROR = 0x5,
    NO_SUCH_JUMP_IF = 0x6,

    IN_ERROR = 0x7,

    CMD_EXIT = 0x8,

    NO_REG_PTR = 0x9,
}PROC_CMD_ERROR;
 
/// <summary>continue execution from last command (for example when we have error in IN cmd)</summary>
extern PROC_CMD_ERROR processor_continue_execution(Processor *proc);
/// <summary>execute one next command</summary>
extern PROC_CMD_ERROR processor_next_cmd(Processor *proc);
/// <summary>execute command while not error</summary>
extern PROC_CMD_ERROR processor_execute(Processor *proc, proc_ptr_t start_execute_address);
extern Processor *processor_create(uint8_t *memory);
extern void processor_free(Processor *proc, _Bool memory_free);

extern void processor_output_error_code(PROC_CMD_ERROR error_code);

extern void processor_mem_map(Processor *proc, proc_ptr_t start_position, uint8_t *mem_for_map, size_t map_bytes, _Bool set_next_cmd_on_mapped_mem);

extern proc_ptr_t processor_set_next_cmd(Processor *proc, proc_ptr_t shift_from_mem_start);