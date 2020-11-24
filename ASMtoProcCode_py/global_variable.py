import config

def get_pcode_pos():
    return config.pcode_file.tell()

def set_pcode_pos(pos):
    return config.pcode_file.seek(pos)

def write_bytes_pcode(arr_bytes):
    config.pcode_file.write(bytearray(arr_bytes))

def get_pcode_size():
    config.pcode_file.seek(0, 2)
    return config.pcode_file.tell()

def check_name(name, with_vars = True, with_funcs = True, with_labels = True):
    if with_vars:
        for aname in config.parse_info['loc_vars']:
            if(aname.name == name):
                check_name.last_name_is_local = True
                return aname    
        for aname in config.parse_info['glob_vars']:
            if(aname.name == name):
                check_name.last_name_is_local = False
                return aname 
    if with_funcs:
        for aname in config.parse_info['loc_funcs']:
            if(aname.name == name):
                check_name.last_name_is_local = True
                return aname    
        for aname in config.parse_info['glob_funcs']:
            if(aname.name == name):
                check_name.last_name_is_local = False
                return aname 
    if with_labels:
        for aname in config.parse_info['labels']:
            if(aname.name == name):
                check_name.last_name_is_local = True
                return aname 
    return None
check_name.last_name_is_local = None

def DEL__add_expected_name(name, not_write_bytes):
    pos = get_pcode_pos() + not_write_bytes
    if config.expected_names.get(name):
        config.expected_names[name] += [(pos, config.ind_line)] 
    else:
        config.expected_names[name] = [(pos, config.ind_line)] 

def add_expected_name(exp_name):
    for name in exp_name.get_need_variable_define():
        if config.expected_names.get(name):
            config.expected_names[name] += [(exp_name, config.ind_line)] 
        else:
            config.expected_names[name] = [(exp_name, config.ind_line)] 
        

def add_expected_ptr_expression(ptr_expr):#TODO:DEL
    return
    for name in ptr_expr.get_need_variable_define():
        if config.expected_ptr_expression.get(name):
            config.expected_ptr_expression[name] += [(ptr_expr, config.ind_line)] 
        else:
            config.expected_ptr_expression[name] = [(ptr_expr, config.ind_line)] 


def exist_expected_names():
    return (len(config.expected_names) + len(config.expected_ptr_expression)) != 0

def print_all_expected_names():
    for x in config.expected_names:
        print('"'+ x[0].variable +'"    in line: '+ str(x[1]))

def name_substitute(aname):
    from class__asm_name import asm_name
    if type(aname) != asm_name: raise Exception('wrong type')
    
    back_pos = get_pcode_pos()
    change_pos = False
    
    name = config.expected_names.get(aname.name)
    if name:
        for x in name:
            exp_name = x[0]
            if exp_name.is_variable_ok(aname) == False:
                return [False, "wrong type of name: "+aname.name]

            if exp_name.upd_variable(aname):
                exp_name.value_substitute()
                warning = exp_name.warning()
                if warning: 
                    print('warning: in line: '+str(x[1])+'   variable: '+name)
                    print('         ' + warning)
                change_pos = True
        config.expected_names.pop(aname.name)

    name = config.expected_ptr_expression.get(aname.name)
    if name:
        for x in name:
            ptr_expr = x[0]
            if ptr_expr.upd_variable(aname):
                ptr_expr.value_substitute()
                warning = ptr_expr.warning()
                if warning: 
                    print('warning: in line: '+str(x[1])+'   variable: '+name)
                    print('         ' + warning)
                change_pos = True
        config.expected_ptr_expression.pop(aname.name)

    if change_pos: set_pcode_pos(back_pos)
    return [True]

    