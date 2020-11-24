from opcodes import OPCODE_PASS
from values import PTR_BYTE, value_to_byte
from global_variable import get_pcode_pos, set_pcode_pos, write_bytes_pcode

class I_deferred_define:
    __except = Exception('not realise')
    def need_variable_define(self): raise I_deferred_define.__except
    def get_need_variable_define(self): raise I_deferred_define.__except
    def upd_variable(self, a_name): raise I_deferred_define.__except # a_name is asm_name
    def upd_value(self, value, variable): raise I_deferred_define.__except # TODO:TRY:DEL
    def value_substitute(self, set_pcode_file_back = False): raise I_deferred_define.__except
    def to_bytes(self): raise I_deferred_define.__except
    def warning(self): raise I_deferred_define.__except