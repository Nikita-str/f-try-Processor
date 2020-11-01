#include "processor.h"

//next here cause when we include processor.h we not want see function from next headers
#include "Auxiliary/generic_function.h"
#include "Auxiliary/IN_support.h"
#define PROCESSOR_CODE
#include "__processor_utility.h"
#undef PROCESSOR_CODE

PROC_CMD_ERROR processor_next_cmd(Processor *proc)
{
    int64_t rip = proc->reg.RIP;
    uint8_t cmd[PROC_MAX_CMD_LEN] = {0};
    {
        uint8_t add_rip = 0;
        _Bool moreByte = 0;
        do {
            uint8_t cmd_byte = proc->mem.memory[rip];
            moreByte = cmd_byte & OpCodeOneMoreByte;
            cmd[add_rip] = cmd_byte;
            rip += 1;
            add_rip += 1;
            if (moreByte && add_rip == PROC_MAX_CMD_LEN) {
                return NO_SUCH_CMD;
            }
        } while (moreByte);
    }

    #define read_type(type) __read_n(sizeof(type), proc->mem.memory + rip); rip += sizeof(type);
    #define read_reg() read_type(uint8_t);
    #define read_byte() read_type(uint8_t);
    #define read_iproc() read_type(iproc_t);

    #define get_c_string_ptr() ((char *)(proc->mem.memory + rip));

    #define read_double() __d_read_n(proc->mem.memory + rip); rip += sizeof(double);

    #define read_n(n) __read_n(n, proc->mem.memory + rip); rip += n;

    switch (cmd[0]) {
    case PUSH_4:
    {
        iproc_t elem = read_iproc();
        generic_stack_push(iproc_t)(proc->stack, elem);
        goto RETURN;
    }
    case PUSH_8:
    {
        iproc_t elem_1 = read_iproc();
        iproc_t elem_2 = read_iproc();
        generic_stack_push(iproc_t)(proc->stack, elem_1);
        generic_stack_push(iproc_t)(proc->stack, elem_2);
        goto RETURN;
    }
    case PUSH_EAX:
    {
        generic_stack_push(iproc_t)(proc->stack, proc->reg.EAX);
        goto RETURN;
    }
    case PUSH_F:
    {
        double elem = 0;
        uint64_t *ptr_elem = &elem;
        *ptr_elem = read_double(); 
        generic_stack_push(double)(proc->stack_f, elem);
        goto RETURN;
    }
    case PUSH_FAX:
    {
        generic_stack_push(double)(proc->stack_f, proc->reg.FAX);
        goto RETURN;
    }
    case PUSH_REG_1B:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        uint64_t value = get_reg_value(pr);//((uint64_t *)pr.reg_ptr)[0]; //think [0] more clear than: *((uint64_t *)pr.reg_ptr)

        if (pr.reg_bytes > REG_4B) {
            if (pr.reg_bytes != REG_8B)return FUTURE_ERROR;
            else {
                generic_stack_push(iproc_t)(proc->stack, (iproc_t)value);
                generic_stack_push(iproc_t)(proc->stack, (iproc_t)(value >> 32));
            }
        } else {
            generic_stack_push(iproc_t)(proc->stack, (iproc_t)value);
        }

        goto RETURN;
    }

    case PUSH_F_REG_1B:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        generic_stack_push(double)(proc->stack_f, get_f_reg_value(pr));
        goto RETURN;
    }

    case POP:
        if (proc->stack->size < 1)return POP_ERROR;
        generic_stack_pop(iproc_t)(proc->stack);
        goto RETURN;

    case POP_EAX:
        proc->reg.RAX = 0; // TODO:?
        if (proc->stack->size < 1)return POP_ERROR;
        proc->reg.EAX = generic_stack_pop(iproc_t)(proc->stack);
        goto RETURN;

    case POP_F:
        if (proc->stack_f->size < 1)return POP_ERROR;
        generic_stack_pop(double)(proc->stack_f);
        goto RETURN;

    case POP_FAX:
        if (proc->stack_f->size < 1)return POP_ERROR;
        proc->reg.FAX = generic_stack_pop(double)(proc->stack_f);
        goto RETURN;

    case POP_F_REG_1B:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        if (proc->stack_f->size < 1)return POP_ERROR;
        //((double *)pr.reg_ptr)[0] = generic_stack_pop(double)(proc->stack_f);
        set_f_reg_value(pr, generic_stack_pop(double)(proc->stack_f));
        goto RETURN;
    }

    case POP_REG_1B:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        if (proc->stack->size < 1)return POP_ERROR;
        uint64_t elem = generic_stack_pop(iproc_t)(proc->stack);
        if (pr.reg_bytes > REG_4B) {
            if (pr.reg_bytes > REG_8B)return FUTURE_ERROR;
            if (proc->stack->size < 1)return POP_ERROR;
            elem = (elem << 32) + generic_stack_pop(iproc_t)(proc->stack);
        }
        //((uint64_t *)pr.reg_ptr)[0] = elem;
        set_reg_value(pr, elem);
        goto RETURN;
    }

    case ADD:
    {
        if (proc->stack->size < 2)return POP_ERROR;
        iproc_t x = generic_stack_pop(iproc_t)(proc->stack);
        iproc_t y = generic_stack_pop(iproc_t)(proc->stack);
        generic_stack_push(iproc_t)(proc->stack, (x + y));
        goto RETURN;
    }

    case SUB:
    {
        if (proc->stack->size < 2)return POP_ERROR;
        iproc_t x = generic_stack_pop(iproc_t)(proc->stack);
        iproc_t y = generic_stack_pop(iproc_t)(proc->stack);
        generic_stack_push(iproc_t)(proc->stack, (x - y));
        goto RETURN;
    }

    case MUL:
    {
        if (proc->stack->size < 2)return POP_ERROR;
        iproc_t x = generic_stack_pop(iproc_t)(proc->stack);
        iproc_t y = generic_stack_pop(iproc_t)(proc->stack);
        i2proc_t z = x * (i2proc_t)y;
        generic_stack_push(iproc_t)(proc->stack, (iproc_t)z);
        generic_stack_push(iproc_t)(proc->stack, (iproc_t)(z >> 32));
        goto RETURN;
    }

    case DIV:
    {
        if (proc->stack->size < 2)return POP_ERROR;
        iproc_t x = generic_stack_pop(iproc_t)(proc->stack);
        iproc_t y = generic_stack_pop(iproc_t)(proc->stack);
        if (y == 0)return DIV_ZERO_ERROR;
        iproc_t z = x / y;
        generic_stack_push(iproc_t)(proc->stack, (iproc_t)z);
        goto RETURN;
    }

    case ADD_F:
    case SUB_F:
    case MUL_F:
    {
        if (proc->stack_f->size < 2)return POP_ERROR;
        double x = generic_stack_pop(double)(proc->stack_f);
        double y = generic_stack_pop(double)(proc->stack_f);
        double z = 0;
        switch (cmd[0]) {
        case ADD_F: z = x + y; break;
        case SUB_F: z = x - y; break;
        case MUL_F: z = x * y; break;
        }
        generic_stack_push(double)(proc->stack_f, z);
        goto RETURN;
    }
    case DIV_F:
    {
        if (proc->stack_f->size < 2)return POP_ERROR;
        double x = generic_stack_pop(double)(proc->stack_f);
        double y = generic_stack_pop(double)(proc->stack_f);
        if (DoubleEqualZero(y))return DIV_ZERO_ERROR;
        generic_stack_push(double)(proc->stack_f, x / y);
        goto RETURN;
    }

    case ADD_REG_VAL:
    case SUB_REG_VAL:
    case MUL_REG_VAL:
    case DIV_REG_VAL:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        uint8_t value_byte_len = 1 << (pr.reg_bytes - 1);

        uint64_t value = read_n(value_byte_len);
        if ((cmd[0] == DIV_REG_VAL) && (value == 0))return DIV_ZERO_ERROR;
        if ((cmd[0] == MUL_REG_VAL) && (pr.reg_bytes != REG_8B))pr.reg_bytes += 1;
        uint64_t reg_now_value = get_reg_value(pr);//((uint64_t *)pr.reg_ptr)[0];
        switch (cmd[0]) {
        case ADD_REG_VAL: value = reg_now_value + value; break;
        case SUB_REG_VAL: value = reg_now_value - value; break;
        case MUL_REG_VAL: value = ((int64_t)reg_now_value) * (int64_t)value; break;
        case DIV_REG_VAL: value = ((int64_t)reg_now_value) / (int64_t)value; break;
        }
        //((uint64_t *)pr.reg_ptr)[0] = value;
        set_reg_value(pr, value);
        goto RETURN;
    }

    case ADD_REG_REG:
    case SUB_REG_REG:
    case MUL_REG_REG:
    case DIV_REG_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;
        uint64_t reg_2_value = get_reg_value(pr_2);

        if ((cmd[0] == DIV_REG_REG) && (reg_2_value == 0))return DIV_ZERO_ERROR;
        if ((cmd[0] == MUL_REG_REG) && (pr.reg_bytes != REG_8B))pr.reg_bytes += 1;

        uint64_t reg_now_value = get_reg_value(pr);//((uint64_t *)pr.reg_ptr)[0];//get_reg_value?
        switch (cmd[0]) {
        case ADD_REG_REG: reg_now_value = reg_now_value + reg_2_value; break;
        case SUB_REG_REG: reg_now_value = reg_now_value - reg_2_value; break;
        case MUL_REG_REG: reg_now_value = ((int64_t)reg_now_value) * (int64_t)reg_2_value; break;
        case DIV_REG_REG: reg_now_value = ((int64_t)reg_now_value) / (int64_t)reg_2_value; break;
        }
        //((uint64_t *)pr.reg_ptr)[0] = reg_now_value;
        set_reg_value(pr, reg_now_value);
        goto RETURN;
    }

    case ADD_F_REG_VAL:
    case SUB_F_REG_VAL:
    case MUL_F_REG_VAL:
    case DIV_F_REG_VAL:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        double value = read_double();
        if ((cmd[0] == DIV_F_REG_VAL) && DoubleEqualZero(value))return DIV_ZERO_ERROR;

        double reg_now_value = get_f_reg_value(pr);
        switch (cmd[0]) {
        case ADD_F_REG_VAL: value = reg_now_value + value; break;
        case SUB_F_REG_VAL: value = reg_now_value - value; break;
        case MUL_F_REG_VAL: value = ((int64_t)reg_now_value) * (int64_t)value; break;
        case DIV_F_REG_VAL: value = ((int64_t)reg_now_value) / (int64_t)value; break;
        }
        set_f_reg_value(pr, value);
        goto RETURN;
    }

    case ADD_F_REG_REG:
    case SUB_F_REG_REG:
    case MUL_F_REG_REG:
    case DIV_F_REG_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;
        double reg_2_value = get_f_reg_value(pr_2);

        if ((cmd[0] == DIV_REG_REG) && (reg_2_value == 0))return DIV_ZERO_ERROR;

        double reg_now_value = get_f_reg_value(pr);
        switch (cmd[0]) {
        case ADD_F_REG_REG: reg_now_value = reg_now_value + reg_2_value; break;
        case SUB_F_REG_REG: reg_now_value = reg_now_value - reg_2_value; break;
        case MUL_F_REG_REG: reg_now_value = reg_now_value * reg_2_value; break;
        case DIV_F_REG_REG: reg_now_value = reg_now_value / reg_2_value; break;
        }
        set_f_reg_value(pr, reg_now_value);
        goto RETURN;
    }

    case MOV_REG_VAL:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        uint8_t value_byte_len = 1 << (pr.reg_bytes - 1);
        uint64_t value = read_n(value_byte_len);

        set_reg_value(pr, value);
        goto RETURN;
    }

    case MOV_REG_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;
        
        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;

        set_reg_value(pr, get_reg_value(pr_2));
        goto RETURN;
    }

    case MOV_F_REG_VAL:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        double value = read_double();

        set_f_reg_value(pr, value);
        goto RETURN;
    }

    case MOV_FREG_FREG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;

        set_f_reg_value(pr, get_f_reg_value(pr_2));
        goto RETURN;
    }

    case MOV_FREG_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;

        double value = (double)get_reg_value(pr_2);

        set_f_reg_value(pr, value);
        goto RETURN;
    }

    case MOV_REG_FREG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        reg_byte = read_reg();
        struct __proc_reg pr_2 = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr_2.reg_error)return REG_ERROR;

        int64_t value = (int64_t)get_f_reg_value(pr_2);

        set_reg_value(pr, (uint64_t)value);
        goto RETURN;
    }

    case JUMP_ADDR:
    {
        proc_ptr_t ptr = read_type(proc_ptr_t);
        proc->reg.RIP = ptr;
        goto RETURN_WO_CHANGE_RIP;
    }

    case JUMP_DIFF:
    {
        proc_delta_ptr_t delta_ptr = read_type(proc_delta_ptr_t);
        proc->reg.RIP += delta_ptr;
        goto RETURN_WO_CHANGE_RIP;
    }

    case JUMP_IF_ADDR:
    {
        uint8_t if_byte = read_byte();
        proc_ptr_t ptr = read_type(proc_ptr_t);
        if (if_byte < JIF_MIN_VALID || if_byte > JIF_MAX_VALID)return NO_SUCH_JUMP_IF;
        uint64_t flags = proc->reg.FLAGS;
        if (proc_check_condition(flags, if_byte)) {
            proc->reg.RIP = ptr;
            goto RETURN_WO_CHANGE_RIP;
        }
        goto RETURN;
    }

    case JUMP_IF_DIFF:
    {
        uint8_t if_byte = read_byte();
        proc_delta_ptr_t delta_ptr = read_type(proc_delta_ptr_t);
        if (if_byte < JIF_MIN_VALID || if_byte > JIF_MAX_VALID)return NO_SUCH_JUMP_IF;
        uint64_t flags = proc->reg.FLAGS;
        if (proc_check_condition(flags, if_byte)) {
            proc->reg.RIP += delta_ptr;
            goto RETURN_WO_CHANGE_RIP;
        }
        goto RETURN;
    }

    case INC_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        uint64_t value = get_reg_value(pr) + 1;
        set_reg_value(pr, value);
        goto RETURN;
    }

    case DEC_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        uint64_t value = get_reg_value(pr) - 1;
        set_reg_value(pr, value);
        goto RETURN;
    }

    case OUT_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        int64_t value = (int64_t)get_reg_value(pr);
        printf("%lld", value);

        goto RETURN;
    }

    case OUT_FREG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        double value = get_f_reg_value(pr);
        printf("%lf", value);

        goto RETURN;
    }

    case OUT_C_STRING:
    {
        uint8_t str_len = read_byte();//TODO:i think 255 it's ok

        char *c_ptr = get_c_string_ptr();
        printf("%.*s", str_len, c_ptr);
        rip += str_len;
        goto RETURN;
    }

    case IN_REG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(iGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        int64_t value = 0;
        if (IN_read_int64(&value))return IN_ERROR; //TODO: or we can try again ....
        
        set_reg_value(pr, value);
        goto RETURN;
    }

    case IN_FREG:
    {
        uint8_t reg_byte = read_reg();
        struct __proc_reg pr = processor_reg_get_ptr(fGP, reg_byte, proc);
        if (pr.reg_error)return REG_ERROR;

        double value = 0;
        if (IN_read_double(&value))return IN_ERROR; //TODO: or we can try again ....
        
        set_f_reg_value(pr, value);
        goto RETURN;
    }
    case HLT:
    {
        proc->reg.RIP = rip;
        return CMD_EXIT;
    }

    default:
        return NO_SUCH_CMD;
    }

    #undef read_double
    #undef read_iproc
    #undef read_byte
    #undef read_reg
    #undef read_type

    #undef get_c_string_ptr

    #undef read_n


RETURN:
    proc->reg.RIP = rip;
RETURN_WO_CHANGE_RIP:
    return NO_ERROR;

}

PROC_CMD_ERROR processor_continue_execution(Processor *proc)
{
    return processor_execute(proc, proc->reg.RIP);
}

PROC_CMD_ERROR processor_execute(Processor *proc, proc_ptr_t start_execute_address)
{
    proc->reg.RIP = start_execute_address;
    PROC_CMD_ERROR state_of_proc = NO_ERROR;
    while ((state_of_proc = processor_next_cmd(proc)) == NO_ERROR);
    return state_of_proc;
}

Processor *processor_create(uint8_t *memory)
{
    Processor *proc = calloc(1, sizeof(*proc));
    if (proc == NULL)return NULL;
    proc->mem.stack = new_generic_stack(iproc_t)(8);
    proc->mem.stack_f = new_generic_stack(double)(8);
    proc->stack = &(proc->mem.stack);
    proc->stack_f = &(proc->mem.stack_f);
    proc->mem.memory = memory;
    return proc;
}

void processor_free(Processor *proc, _Bool memory_free)
{
    if (memory_free)free(proc->mem.memory);
    free_generic_stack(iproc_t)(proc->stack);
    free_generic_stack(double)(proc->stack_f);
    free(proc);
}


void processor_output_error_code(PROC_CMD_ERROR error_code)
{
    switch (error_code) {
    case NO_ERROR:
        printf("no error (but if you get it in end then something went ... weird?!)\n");
        break;
    case CMD_EXIT:
        printf("completed successfully\n");
        break;
    case NO_SUCH_CMD:
        printf("error opcode of command\n");
        break;
    case POP_ERROR:
        printf("error opcode of command\n");
        break;
    case REG_ERROR:
        printf("in command was no exist register!\n");
        break;
    case FUTURE_ERROR:
        printf("WOw we are in the future!\n");
        break;
    case DIV_ZERO_ERROR:
        printf("see how I can (not) : x/0\n");
        break;
    case NO_SUCH_JUMP_IF:
        printf("weird condition of jump... such command not exist\n");
        break;
    case IN_ERROR:
        printf("incorrect data was entered\n");
        break;
    default:
        printf("Unknown error\n");
        break;
    }
}