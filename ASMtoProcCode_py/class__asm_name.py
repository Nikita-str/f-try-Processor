from values import value_to_byte, PTR_BYTE
from variable_types import sizeof_variable_type, TypeofName, TypeofNameAction

class asm_name:
    def __init__(self, name, define_position, name_type, local, var_type = None, arr_len = None):
        self.name = name
        self.position = define_position

        self.name_type = name_type
        if(name_type != TypeofName.var):var_type = None; arr_len = None
        self.var_type = var_type
        self.arr_len = arr_len 

        self.local = local

        self.ptr_byte_form = value_to_byte([], self.position, PTR_BYTE)
 
    def get_len(self):
        #if self.arr_len == None => error(scalar type)
        return self.arr_len

    def get_sz(self):
        return sizeof_variable_type(self.var_type)

    def get_value_ptr(self):
        return self.position

    def get_value_by_typeof_act(self, typeof_action):
        if(typeof_action == TypeofNameAction.PTR): return self.get_value_ptr()
        elif(typeof_action == TypeofNameAction.SZ): return self.get_sz()
        elif(typeof_action == TypeofNameAction.LEN): return self.get_len()
        raise Exception('wrong action type :|')

    def __str__(self):
        #TODO:change in way that allow create header by just file.write(str(asm_name))
        return self.name
    
    def __repr__(self):return self.name
