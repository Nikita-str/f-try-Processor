from opcodes import OPCODE_PASS;
from values import PTR_BYTE, is_valid_value, need_bytes_for_ptr_value, value_to_byte;

#cptr - const ptr
#ncptr - not const ptr

#used for: [a*x+b+....]
#but now it can only be like : [const_1 * var + const_2]
class cptr_expression:
    def __init__(self, position, mul = 1, variable = 0, add = 0):
        self.valid = True
        if(not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = mul
        elif(not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = add
        else:
            if(type(variable) == int):
                self.value = mul*variable + add;
            else:
                self.value = None
                self.position = position
                self.add = add
                self.variable = variable
                Self.mul = mul

    #must be called only in is_cptr function
    def is_valid(self):return self.valid    
    
    def need_variable_define(self):
        return (self.value == None)

    def get_need_variable_define(self):
        if(self.value == None): return [self.variable]
        return []
    
    def get_value(self): return self.value
    def get_position(self): return self.position #only if we dont know value initial

    #return: was value updated?
    def upd_value(self, value, variable = None):
        if(self.value != None):return False
        if((variable != None) and (self.variable != variable)):return False
        self.value = value
        return True

    def to_bytes(self):
        pass#TODO: if value is None then PASS*4


#used for: [a*x+b+....]
#but now it can only be like : [var_1 * reg + var_2] / [const_1 * reg + const_2]
class ncptr_expression:
    ADD_SHIFT = 0
    MUL_SHIFT = 2
    IS_SUB_SHIFT = 4
    # [mul*reg + add]
    def __init__(self, position, reg, mul = 1, add = 0):

        #TODO:CANT WHILE mul or add is a name, but not a number
        
        self.valid = True
        if(not is_valid_value(mul, PTR_BYTE)):
            self.valid = False
            self.too_big_value = mul
        elif(not is_valid_value(add, PTR_BYTE)):
            self.valid = False
            self.too_big_value = add
        else:
            self.reg = reg

            self.add = add
            self.mul = mul

            self.is_sub = 0

            self.position = position

            self.__try_cmd();
        pass

    def __try_cmd(self):
        if(self.cmd_byte != None):return;
        
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
            self.is_sub = 1;
            self.add = -self.add;
        
        self.cmd_byte = ((self.is_sub) << ncptr_expression.IS_SUB_SHIFT)
        self.cmd_byte += ((self.byte_add) << ncptr_expression.ADD_SHIFT)
        self.cmd_byte += ((self.byte_mul) << ncptr_expression.MUL_SHIFT)

    #must be called only in is_cptr function
    def is_valid(self):return self.valid    

    def get_position(self): return self.position
    
    def need_variable_define(self):
        return (type(self.add) != int or type(self.mul) != int)

    def get_need_variable_define(self):
        ret = []
        if(type(self.add) != int): ret += [self.add]
        if(type(self.mul) != int): ret += [self.mul]
        return ret

    def get_cmd_byte(self): return self.cmd_byte
    
    def to_bytes(self, with_cmd_byte = False):
        ret = [] #bytes

        self.__try_cmd()
        
        if(self.cmd_byte == None):
            if(with_cmd_byte): ret += [OPCODE_PASS]
            ret += [self.reg]
            ret += [OPCODE_PASS]*(self.byte_mul + self.byte_add)
        else:
            if(with_cmd_byte): ret += [self.cmd_byte]
            ret += [self.reg]
            value_to_byte(ret, mul, self.byte_mul)
            value_to_byte(ret, add, self.byte_add)
        
        return ret
    

        



    
