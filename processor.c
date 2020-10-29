#include "processor.h"

#define PR_NOT_USER_CODE
#include "__processor_utility.h"
#undef PR_NOT_USER_CODE

typedef enum PROC_CMD_ERROR//TODO:MOVE:processor.h
{
    NO_ERROR = 0x0,
    NO_SUCH_CMD = 0x1,
    POP_ERROR = 0x2,
    REG_ERROR = 0x3,
    FUTURE_ERROR = 0x4,//eah.. this is in case of cyberpunk
}PROC_CMD_ERROR;

inline PROC_CMD_ERROR processor_next_cmd(Processor proc)
{
    uint8_t add_rip = 0;
    int64_t rip = proc.reg.RIP;
    uint8_t cmd[8] = 0;
    {
        _Bool moreByte = 0;
        do {
            uint8_t cmd_byte = proc.mem.memory[rip];
            moreByte = cmd_byte & OpCodeOneMoreByte;
            cmd[add_rip] = cmd_byte;
            rip += 1;
            add_rip += 1;
        } while (moreByte);
    }


    switch (cmd[0]) {
    case PUSH_4:
    {
        int32_t elem = ((int32_t *)(proc.mem.memory + rip))[0];
        generic_stack_push(int32_t)(proc.stack, elem);
        add_rip += 4;
        goto RETURN;
    }
    case PUSH_8:
    {
        int32_t elem_1 = ((int32_t *)(proc.mem.memory + rip))[0];
        int32_t elem_2 = ((int32_t *)(proc.mem.memory + rip))[1];
        generic_stack_push(int32_t)(proc.stack, elem_1);
        generic_stack_push(int32_t)(proc.stack, elem_2);
        add_rip += 8;
        goto RETURN;
    }
    case PUSH_EAX:
    {
        generic_stack_push(int32_t)(proc.stack, proc.reg.EAX);
        goto RETURN;
    }
    case PUSH_F:
    {
        double elem = 0;
        uint64_t *ptr_elem = &elem;
        *ptr_elem = ((uint64_t *)(proc.mem.memory + rip))[0];
        generic_stack_push(double)(proc.stack_f, elem);
        add_rip += 8;
        goto RETURN;
    }
    case PUSH_FAX:
    {
        generic_stack_push(double)(proc.stack_f, proc.reg.FAX);
        goto RETURN;
    }
    case PUSH_REG_1B:
    {
        struct __proc_reg_int_info prii = processor_reg_int_get_value(cmd[1], proc.reg);
        struct __proc_reg pr = processor_reg_get_ptr(iGP, cmd[1], proc.reg);
        if (prii.reg_error)return REG_ERROR;
        uint64_t value = prii.value;

        if (prii.r_bytes > REG_4B) {
            if (prii.r_bytes != REG_8B)return FUTURE_ERROR;
            else {
                generic_stack_push(int32_t)(proc.stack, (int32_t)value);
                generic_stack_push(int32_t)(proc.stack, value >> 32);
            }
        } else {
            generic_stack_push(int32_t)(proc.stack, (int32_t)value);
        }

        goto RETURN;
    }

    case PUSH_F_REG_1B:
    {
        struct __proc_reg_f_info prfi = processor_reg_f_get_value(cmd[1], proc.reg);
        if (prfi.reg_error)return REG_ERROR;
        generic_stack_push(double)(proc.stack_f, prfi.value);
        goto RETURN;
    }

    case POP:
        if (proc.stack->size < 1)return POP_ERROR;
        generic_stack_pop(int32_t)(proc.stack);
        goto RETURN;

    case POP_EAX:
        proc.reg.RAX = 0; // TODO:?
        if (proc.stack->size < 1)return POP_ERROR;
        proc.reg.EAX = generic_stack_pop(int32_t)(proc.stack);
        goto RETURN;

    case POP_F:
        if (proc.stack_f->size < 1)return POP_ERROR;
        generic_stack_pop(double)(proc.stack_f);
        goto RETURN;

    case POP_FAX:
        if (proc.stack_f->size < 1)return POP_ERROR;
        proc.reg.FAX = generic_stack_pop(double)(proc.stack_f);
        goto RETURN;

    case POP_F_REG_1B:
    {
        struct __proc_reg_offset st_off = processor_reg_f_get_offset(cmd[1]);
        if (st_off.reg_error)return REG_ERROR;
        if (proc.stack_f->size < 1)return POP_ERROR;
        ((double *)&proc.reg)[st_off.reg_offset] = generic_stack_pop(double)(proc.stack_f);
        goto RETURN;
    }

    case POP_REG_1B:
    {
        struct __proc_reg_offset st_off = processor_reg_int_get_offset(cmd[1]);
        if (st_off.reg_error)return REG_ERROR;
        if (proc.stack->size < 1)return POP_ERROR;
        uint64_t elem = generic_stack_pop(int32_t)(proc.stack);
        if (st_off.r_bytes > REG_4B) {
            if (st_off.r_bytes > REG_8B)return FUTURE_ERROR;
            if (proc.stack->size < 1)return POP_ERROR;
            elem = (elem << 32) + generic_stack_pop(int32_t)(proc.stack);
        }
        ((uint64_t *)&proc.reg)[st_off.reg_offset] = elem;
        goto RETURN;
    }

    default:
        return NO_SUCH_CMD;
    }

RETURN:
    proc.reg.RIP += add_rip;
    return NO_ERROR;
}