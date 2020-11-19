from values import value_to_byte, PTR_BYTE;
from variable_types import sizeof_variable_type;

class asm_name:
    def __init__(self, name, define_position, var_type, arr_len = None):
        self.name = name
        self.position = define_position

        self.var_type = var_type
        self.arr_len = arr_len 

        self.ptr_byte_form = value_to_byte([], self.position, PTR_BYTE)
        
    def get_len(self):
        #if self.arr_len == None => error(scalar type)
        return self.arr_len

    def get_sz(self):
        return sizeof_variable_type(self.var_type)
