from opcodes import OPCODE_PASS
from values import PTR_BYTE, is_valid_value, need_bytes_for_ptr_value, value_to_byte
from global_variable import get_pcode_pos, set_pcode_pos, write_bytes_pcode

class interface_ptr_expression:
    __except = Exception('not realise')
    def need_variable_define(self): raise interface_ptr_expression.__except
    def get_need_variable_define(self): raise interface_ptr_expression.__except

#cptr - const ptr
#ncptr - not const ptr

#used for: [a*x+b+....]
#but now it can only be like : [const_1 * var + const_2]
class cptr_expression(interface_ptr_expression):
    def __init__(self, position, mul = 1, variable = 0, add = 0):
        self.valid = True
        if(not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = mul
        elif(not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = add
        else:
            self.position = position
            if(type(variable) == int):
                self.variable = None
                self.value = mul*variable + add
                
            else:
                self.value = None
                self.add = add
                self.variable = variable
                self.mul = mul

    #must be called only in is_cptr function
    def is_valid(self):return self.valid    
    
    def need_variable_define(self):
        return (self.value == None)

    def get_need_variable_define(self):
        if(self.value == None): return [self.variable]
        return []

    def get_value(self): return self.value
    def get_position(self): return self.position #only if we dont know value initial


    #return bool: can to substitute
    def upd_value(self, value, variable = None, with_check_var = True):
        #if(self.value != None):return False
        if(with_check_var and self.variable != variable):return False
        self.value = value
        return True

    def value_substitute(self, set_pcode_file_back = False):
        if self.need_variable_define(): return False
        if set_pcode_file_back: back_pos = get_pcode_pos()
        
        set_pcode_pos(self.position)
        write_bytes_pcode(self.to_bytes())

        if set_pcode_file_back: set_pcode_pos(back_pos)
        return True

    def to_bytes(self):
        ret = [] #bytes
        
        if self.need_variable_define():
            ret += [OPCODE_PASS]*PTR_BYTE
        else:
            value_to_byte(ret, self.value, PTR_BYTE)
        
        return ret

    def warning(self): return None


#used for: [a*x+b+....]
#but now it can only be like : [var_1 * reg + var_2] / [const_1 * reg + const_2]
class ncptr_expression:
    ADD_SHIFT = 0
    MUL_SHIFT = 2
    IS_SUB_SHIFT = 4
    # [mul*reg + add]
    def __init__(self, cmd_pos, op_pos, reg, mul = 1, add = 0):
        self.valid = True
        if(type(mul) == int and not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = mul
        elif(type(add) == int and not is_valid_value(add, PTR_BYTE)):
            self.valid = False
            self.too_big_value = add
        else:
            #data for warning:
            self.__bytes_initial = 0
            self.__bytes_finite = 0
            self.__come_back = False

            self.reg = reg

            self.add = add
            self.mul = mul

            self.is_sub = 0

            self.cmd_pos = cmd_pos
            self.op_pos = op_pos

            self.cmd_byte = None
            self.__try_cmd()
        #pass

    def __try_cmd(self):
        if(self.cmd_byte != None):return
        
        if(type(self.add) != int or type(self.mul) != int):
            self.cmd_byte = None
            self.byte_mul = PTR_BYTE
            self.byte_add = PTR_BYTE
            if(type(self.add) == int): self.byte_add = need_bytes_for_ptr_value(self.add, 0, True)
            if(type(self.mul) == int): self.byte_mul = need_bytes_for_ptr_value(self.mul, 1, False)
            return
        
        self.byte_mul = need_bytes_for_ptr_value(self.mul, 1, False)
        self.byte_add = need_bytes_for_ptr_value(self.add, 0, True)
        
        if(self.add < 0):
            self.is_sub = 1
            self.add = -self.add
        
        self.cmd_byte = ((self.is_sub) << ncptr_expression.IS_SUB_SHIFT)
        self.cmd_byte += ((self.byte_add) << ncptr_expression.ADD_SHIFT)
        self.cmd_byte += ((self.byte_mul) << ncptr_expression.MUL_SHIFT)

    #must be called only in is_cptr function
    def is_valid(self):return self.valid    
    
    def need_variable_define(self):
        return (type(self.add) != int or type(self.mul) != int)

    def get_need_variable_define(self):
        ret = []
        if(type(self.add) != int): ret += [self.add]
        if(type(self.mul) != int): ret += [self.mul]
        return ret

    #return bool: can to substitute
    def upd_value(self, value, variable):
        if(type(variable)!=str): raise Exception('wrong param')
        if variable == self.add: self.add = value
        if variable == self.mul: self.mul = value
        return self.need_variable_define

    def get_cmd_byte(self): return self.cmd_byte

    def value_substitute(self, set_pcode_file_back = False):
        if self.need_variable_define(): return False
        
        if set_pcode_file_back: back_pos = get_pcode_pos()
        
        self.__try_cmd()
        
        set_pcode_pos(self.cmd_pos)
        write_bytes_pcode(self.get_cmd_to_bytes())

        set_pcode_pos(self.op_pos)
        write_bytes_pcode(self.to_bytes())

        if set_pcode_file_back: set_pcode_pos(back_pos)
        
        return True

    def get_cmd_to_bytes(self): 
        if self.cmd_byte == None: return [OPCODE_PASS]
        return [self.cmd_byte]

    def to_bytes(self, with_cmd_byte = False):
        ret = [] #bytes

        self.__try_cmd()
        if self.__bytes_initial == 0: self.bytes_initial = (self.byte_mul + self.byte_add)

        if(self.cmd_byte == None):
            self.__come_back = True
            if(with_cmd_byte): ret += [OPCODE_PASS]
            ret += [self.reg]
            ret += [OPCODE_PASS]*(self.byte_mul + self.byte_add)
        else:
            self.__bytes_finite = (self.byte_mul + self.byte_add)
            if(with_cmd_byte): ret += [self.cmd_byte]
            ret += [self.reg]
            value_to_byte(ret, self.mul, self.byte_mul)
            value_to_byte(ret, self.add, self.byte_add)
        
        return ret

    def warning(self): 
        if not self.__come_back: return None
        if self.__bytes_finite == self.__bytes_initial: 
            return 'in current case cmd len is the same, but general case if you define the variable in advance you can save space'
        delta = self.__bytes_initial - self.__bytes_finite
        return 'if you define variable in advance you can save '+str(delta)+' bytes'

    

        



    
