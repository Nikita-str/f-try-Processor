#from opcodes import OPCODE_PASS
#from values import PTR_BYTE, value_to_byte
#from global_variable import get_pcode_pos, set_pcode_pos, write_bytes_pcode

from I_deferred_define import * 
from variable_types import TypeofName, TypeofNameAction

def std_diff_func(obj, def_position): return def_position - obj.position

def std_diff_with_shift_func(shift): return lambda obj, def_pos: shift + def_pos - obj.position

class expected_name(I_deferred_define):

    #dependent: if it used in ptr expr, for example [arr + ecx*SZ(arr)], then dependent = [ptr_expr]
    def __init__(self, position, variable, typeof_action = TypeofNameAction.PTR, typeof_name = None, dependent = False, ptr_func = None, valid_var_types = None):
        self.valid = True

        if typeof_name == None:
            if typeof_action == TypeofNameAction.PTR: typeof_name = TypeofName.any_name
            else: typeof_name = TypeofName.var # SZ LEN

        if ptr_func and typeof_action != TypeofNameAction.PTR: self.valid = False
        if typeof_name < TypeofName.no_one or typeof_name > TypeofName.any_name: print('DEL_IT_1'); self.valid = False
        if typeof_action < TypeofNameAction._min_value or typeof_action > TypeofNameAction._max_value:print('DEL_IT_2');  self.valid = False
        if typeof_action!=TypeofNameAction.PTR and (~TypeofName.var ^ typeof_name)!=0: print('DEL_IT_3'); self.valid = False

        if self.valid:
            self.valid_var_types = valid_var_types
            self.ptr_func = ptr_func
            self.dependent = dependent
            self.typeof_name = typeof_name
            self.typeof_act = typeof_action
            self.position = position
            self.variable = variable # name or ptr

    def is_valid(self): return self.valid

    def need_variable_define(self): return type(self.variable) != int
    def get_need_variable_define(self): 
        if self.need_variable_define(): return [self.variable]
        return []

    def upd_value(self, value, variable):
        if(type(variable)!=str): raise Exception('wrong param')
        if(self.typeof_act != TypeofNameAction.PTR): raise Exception('use upd_variable(aname)')
        if variable == self.variable: self.variable = value
        return self.need_variable_define 

    def is_variable_ok(self, a_name):
        if self.valid_var_types != None:
            if a_name.var_type not in self.valid_var_types: return False
        if a_name.name == self.variable: 
            return (self.typeof_name & a_name.name_type) > 0
        return True#None

    def upd_variable(self, a_name):
        if a_name.name == self.variable: 
            if self.ptr_func:
                value = self.ptr_func(self, a_name.get_value_ptr())
            else:
                value = a_name.get_value_by_typeof_act(self.typeof_act)
            #if self.dependent: 
            #    for x in self.dependent:
            #        x.upd_variable(a_name)
            self.variable = value
        return self.need_variable_define
    
    def to_bytes(self):
        if self.dependent: raise Exception('for depend expected_name method to_bytes not will be call')

        ret = []
        
        if self.need_variable_define():
            ret += [OPCODE_PASS]*PTR_BYTE
        else:
            value_to_byte(ret, self.variable, PTR_BYTE)
        
        return ret

    def value_substitute(self, set_pcode_file_back = False):
        if self.need_variable_define(): return False
        
        if set_pcode_file_back: back_pos = get_pcode_pos()
        
        if self.dependent: # if it used in [...]
            for x in self.dependent:
                x.value_substitute(set_pcode_file_back = False)
        else:
            set_pcode_pos(self.position)
            write_bytes_pcode(self.to_bytes())

        if set_pcode_file_back: set_pcode_pos(back_pos)
        return True
    
    def warning(self): return None