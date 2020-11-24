from values import is_num, is_ptr_reg, valid_name, PTR_BYTE, IS_PTR_REG, NOT_PTR_REG
from variable_types import TypeofName, TypeofNameAction
from class__ptr_expression import cptr_expression, ncptr_expression
from class__expected_name import expected_name

from global_variable import get_pcode_pos, check_name, add_expected_name

#WARNING: IN is_cptr & is_ncptr A LOT OF COPY-PASTE  (it not hard to del, but then it bad to read...)
#                                                    (or if it will be easy to read, it take a while; now i don't have time for this)
#                                                    AND
#                                                    it easier and more correct to rewrite with parse expresion, so
#                                                    the current solution is temporary

#TODO:ADD:PARSE EXPRESSIONS: numbers, opearstion = {-,+,*}, variable

IS_PTR_RET__NOT_PTR = 0
IS_PTR_RET__OK = 1
IS_PTR_RET__NOT_PARSEABLE = 2
IS_PTR_RET__INVALID_NAME = 3
IS_PTR_RET__NOT_VALID_REG_PTR = 4
IS_PTR_RET__TOO_BIG_VALUE = 5
IS_PTR_RET__INVALID_NAME_ACTION = 6
#IS_PTR_RET__TOO_MANY_REG =

def is_str_ptr(operand):
    op_len = len(operand)
    if(operand[0] != '[' or operand[op_len-1] != ']'): return False
    return True

#now only ptr that have appearance like:  [const_1 * var + const_2] //var mean ptr on var
def is_cptr(operand, not_write_previous_byte):
    op_len = len(operand)
    if(operand[0] != '[' or operand[op_len-1] != ']'): return (IS_PTR_RET__NOT_PTR, 'not ptr')
    operand = operand[1:op_len-1]
    op_len -= 2

    add = 0
    mul = 1
    var = 0
    
    if(operand.find('-') != -1):
        p = operand.find('-')
        operand = operand[0:p]+'+'+operand[p:]
        
    add_pos = operand.find('+')
    mul_pos = operand.find('*')
    
    if(mul_pos == -1 and add_pos == -1):
        term = operand.strip()
        is_num_1 = is_num(term)
        if(is_num_1[0]):
            add = is_num_1[1]
        else:
            var = term
    elif(add_pos == -1):
        term_1 = operand[0:mul_pos].strip()
        term_2 = operand[mul_pos+1:].strip()
        is_num_1 = is_num(term_1)
        is_num_2 = is_num(term_2)
        if(is_num_1[0] == is_num_2[0]):
            add = is_num_1[1] * is_num_2[1]
        elif(is_num_1[0]):
            mul = is_num_1[1]
            var = term_2
        elif(is_num_2[0]):
            mul = is_num_2[1]
            var = term_1
        else:
            return (IS_PTR_RET__NOT_PARSEABLE, 'while ptr expresion with one mul(*) operation may be like(c1,c2 = const, v = var_name): [c1*v]/[c1*c2]/[v*c1]')
    elif(mul_pos == -1):
        term_1 = operand[0:add_pos].strip()
        term_2 = operand[add_pos+1:].strip()
        is_num_1 = is_num(term_1)
        is_num_2 = is_num(term_2)
        if(is_num_1[0] == is_num_2[0] and is_num_1[0] == True):
            add = is_num_1[1] + is_num_2[1]
        elif(is_num_1[0]):
            add = is_num_1[1]
            var = term_2
        elif(is_num_2[0]):
            add = is_num_2[1]
            var = term_1
        else:
            return (IS_PTR_RET__NOT_PARSEABLE, 'while ptr expresion with one add(+) operation may be like(c1,c2 = const, v = valid_name): [c1+v]/[c1+c2]/[v+c1]')
    else: #[c1*v + c2] or [c1 + c2*v]
        if(mul_pos < add_pos):
            term_1 = operand[0:mul_pos]        #c1   c1    v     c1              
            term_2 = operand[mul_pos+1:add_pos]#v    c2    c1    c2           
            term_3 = operand[add_pos+1:]       #c2   v     c2    c3   
        else:
            term_1 = operand[add_pos+1:mul_pos]              
            term_2 = operand[mul_pos+1:]       
            term_3 = operand[:add_pos]

        term_1 = term_1.strip()
        term_2 = term_2.strip()
        term_3 = term_3.strip()
            
        is_num_1 = is_num(term_1)
        is_num_2 = is_num(term_2)
        is_num_3 = is_num(term_3)
        if(is_num_1[0] == True and is_num_1 == is_num_2 == is_num_3):
            add = is_num_1[1]*is_num_2[1] + is_num_3[1]
        elif(is_num_1[0] == True and is_num_1 == is_num_3):
            mul = is_num_1[1]
            var = term_2
            add = is_num_3[1]
        elif(is_num_2[0] == True and is_num_2 == is_num_3):
            var = term_1
            mul = is_num_2[1]
            add = is_num_3[1]
        elif(is_num_1[0] == True and is_num_1 == is_num_2):
            add = is_num_1[1]*is_num_2[1]
            var = term_3
        else:
            return (IS_PTR_RET__NOT_PARSEABLE, 'while ptr expr with appearance like [x*y + z] may be only like(c1,c2,c3 = const, v = valid_name): [c1*c2+c3]/[c1*v+c2]/[c1*c2+v]/[v*c1+c2]')

    if(mul == 0): var = 0
    add_exp_var = False
    if(type(var) == str):
        temp = valid_name(var, False)
        typeof_act = temp[0]
        if typeof_act == TypeofNameAction.ERROR: return(IS_PTR_RET__INVALID_NAME, temp[1])
        var = temp[1]
        temp = check_name(var)
        if(temp != None): var = temp.get_value_by_typeof_act(typeof_act)
        else: add_exp_var = True

    cptr_expr = cptr_expression(get_pcode_pos() + not_write_previous_byte, mul, var, add)
    if(not cptr_expr.is_valid()): return (IS_PTR_RET__TOO_BIG_VALUE, 'value: '+str(cptr_expr.too_big_value)+' is very big for ptr')

    if add_exp_var:
        exp_name = expected_name(None, var, typeof_act, dependent=[cptr_expr])
        if not exp_name.is_valid(): return (IS_PTR_RET__INVALID_NAME_ACTION, 'such action with "'+var+'" is invalid')
        add_expected_name(exp_name)

    return [IS_PTR_RET__OK, cptr_expr]

#now only ptr that have appearance like:  [var * reg + var] or [const_1 * reg + const_2]
def is_ncptr(operand, cmd_shift, operand_shift):
    op_len = len(operand)
    if(operand[0] != '[' or operand[op_len-1] != ']'): return (IS_PTR_RET__NOT_PTR, 'not reg-sensitive ptr')
    operand = operand[1:op_len-1]
    op_len -= 2

    add = 0
    mul = 1
    reg = None

    if(operand.find('-') != -1):
        p = operand.find('-')
        operand = operand[0:p]+'+'+operand[p:]
    
    add_pos = operand.find('+')
    mul_pos = operand.find('*')

    if(mul_pos == -1 and add_pos == -1):
        term = operand.strip()
        is_pr_1 = is_ptr_reg(term)
        if(is_pr_1[0] == NOT_PTR_REG): return (IS_PTR_RET__NOT_VALID_REG_PTR, 'not valid reg-sensitive ptr')
        reg = is_pr_1[1]
    elif(add_pos == -1):
        term_1 = operand[0:mul_pos].strip()
        term_2 = operand[mul_pos+1:].strip()
        is_pr_1 = is_ptr_reg(term_1)
        is_pr_2 = is_ptr_reg(term_2)
        if((is_pr_1[0] + is_pr_2[0]) != IS_PTR_REG): return (IS_PTR_RET__NOT_VALID_REG_PTR, 'not valid reg-sensitive ptr')
        if(is_pr_1[0] == True):
            reg = is_pr_1[1]
            is_num_2 = is_num(term_2)
            if(is_num_2[0]): mul = is_num_2[1]  
            else: mul = term_2
        else:#is_pr_2[0]==True
            reg = is_pr_2[1]
            is_num_1 = is_num(term_1)
            if(is_num_1[0]): mul = is_num_1[1]  
            else: mul = term_1            
    elif(mul_pos == -1):
        term_1 = operand[0:add_pos].strip()
        term_2 = operand[add_pos+1:].strip()
        is_pr_1 = is_ptr_reg(term_1)
        is_pr_2 = is_ptr_reg(term_2)
        if((is_pr_1[0] + is_pr_2[0]) != IS_PTR_REG): return (IS_PTR_RET__NOT_VALID_REG_PTR, 'not valid reg-sensitive ptr')
        if(is_pr_1[0] == True):
            reg = is_pr_1[1]
            is_num_2 = is_num(term_2)
            if(is_num_2[0]): add = is_num_2[1]  
            else: add = term_2
        else:#is_pr_2[0]==True
            reg = is_pr_2[1]
            is_num_1 = is_num(term_1)
            if(is_num_1[0]): add = is_num_1[1]  
            else: add = term_1
    else: # with mul & add
        if(mul_pos < add_pos):
            term_1 = operand[0:mul_pos]        #c1   c1    v     c1              
            term_2 = operand[mul_pos+1:add_pos]#v    c2    c1    c2           
            term_3 = operand[add_pos+1:]       #c2   v     c2    c3   
        else:
            term_1 = operand[add_pos+1:mul_pos]              
            term_2 = operand[mul_pos+1:]       
            term_3 = operand[:add_pos]

        #[x*reg + x]  x is num or valid name
        term_1 = term_1.strip()
        term_2 = term_2.strip()
        term_3 = term_3.strip()

        is_pr_1 = is_ptr_reg(term_1)
        is_pr_2 = is_ptr_reg(term_2)
        is_pr_3 = is_ptr_reg(term_3)
        bool_done = False
        if((is_pr_1[0] + is_pr_2[0] + is_pr_3[0]) != IS_PTR_REG): return (IS_PTR_RET__NOT_VALID_REG_PTR, 'not valid reg-sensitive ptr')
        if(is_pr_1[0] == IS_PTR_REG):
            reg = is_pr_1[1]
        if(is_pr_2[0] == IS_PTR_REG):
            reg = is_pr_2[1]
            term_2 = term_1
        if(is_pr_3[0] == IS_PTR_REG):
            reg = is_pr_3[1]
            is_num_1 = is_num(term_1)
            is_num_2 = is_num(term_2)
            if(not is_num_1[0] or not is_num_1[0]): return (IS_PTR_RET__NOT_PARSEABLE, 'now not can be parse  [not_const*name + reg]')
            else:
                add = is_num_1[1]*is_num_2[1]
                bool_done = True
        
        if(not bool_done):
            #term_2 == mul; term_3 == add;
            is_num_2 = is_num(term_2)
            is_num_3 = is_num(term_3)
            if(is_num_2[0]): mul = is_num_2[1]
            else: mul = term_2
            if(is_num_3[0]): add = is_num_3[1]
            else: add = term_3

    add_expect_add = False
    add_expect_mul = False

    if(type(add) == str):
        temp = valid_name(add, False)
        typeof_act_add = temp[0]
        if typeof_act_add == TypeofNameAction.ERROR: return(IS_PTR_RET__INVALID_NAME, temp[1])
        add = temp[1]
        temp = check_name(add)
        if(temp != None): add = temp.get_value_by_typeof_act(typeof_act_add)
        else: add_expect_add = True
    if(type(mul) == str):
        temp = valid_name(mul, False)
        typeof_act_mul = temp[0]
        if typeof_act_mul == TypeofNameAction.ERROR: return(IS_PTR_RET__INVALID_NAME, temp[1])
        mul = temp[1]
        temp = check_name(mul)
        if(temp != None): mul = temp.get_value_by_typeof_act(typeof_act_mul)
        else: add_expect_mul = True

    ncptr_expr = ncptr_expression(get_pcode_pos() + cmd_shift, get_pcode_pos() + operand_shift, reg, mul, add)
    if(not ncptr_expr.is_valid()): return (IS_PTR_RET__TOO_BIG_VALUE, 'value: '+str(ncptr_expr.too_big_value)+' is very big for ptr')

    if add_expect_add:
        exp_name = expected_name(None, add, typeof_act_add, dependent=[ncptr_expr])
        if not exp_name.is_valid(): return (IS_PTR_RET__INVALID_NAME_ACTION, 'such action with "'+add+'" is invalid')
        add_expected_name(exp_name)

    if add_expect_mul:
        exp_name = expected_name(None, mul, typeof_act_mul, dependent=[ncptr_expr])
        if not exp_name.is_valid(): return (IS_PTR_RET__INVALID_NAME_ACTION, 'such action with "'+mul+'" is invalid')
        add_expected_name(exp_name)

    return [IS_PTR_RET__OK, ncptr_expr]
