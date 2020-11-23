def get_variable_type(variable_type):
    initial_type = variable_type
    var_type = variable_type.upper()
    if(var_type == 'BYTE'):var_type = 'INT1'
    if(var_type == 'WORD'):var_type = 'INT2'
    if(var_type == 'INT'):var_type = 'INT4'
    if(var_type == 'LONG'):var_type = 'INT8'

    if(var_type in ['DOUBT', 'DO_UB', 'DOUBLE']):var_type = 'DOUB'
        
    if(var_type == 'DARK'):var_type = 'DARR'

    if(var_type in ['BARK', 'BARR']):var_type = 'IARR1'
    if(var_type in ['WAR' , 'WARR']):var_type = 'IARR2'
    if(var_type in ['LIAR', 'IARR']):var_type = 'IARR4'
    if(var_type in ['QUARK','QARR']):var_type = 'IARR8'
    return (initial_type, var_type)


SCALAR_VAR_TYPES = ['INT1', 'INT2', 'INT4', 'INT8']+['DOUB']+['CSTR']
ARRAY_VAR_TYPES = ['IARR1', 'IARR2','IARR4', 'IARR8']+['DARR']

ALL_VAR_TYPES = SCALAR_VAR_TYPES+ARRAY_VAR_TYPES
ALL_VALID_VAR_TYPE_NAMES = ALL_VAR_TYPES + \
    ['BYTE', 'WORD', 'INT', 'LONG'] + ['DOUBT', 'DO_UB', 'DOUBLE'] + \
    ['DARK']+['BARK', 'BARR']+['WAR' , 'WARR']+ \
    ['LIAR', 'IARR']+['QUARK','QARR']

def sizeof_variable_type(var_type):
    if(len(var_type) == 4 and var_type[0:3] == 'INT'):return int(var_type[3:])
    if(var_type == 'DOUB'):return 8
    #MAYBE:ADD ARRAY ... OR NO(не очень то уж и орно на самом деле)
    return None

NAME_TYPE__VAR  = 1
NAME_TYPE__FUNC = 2
NAME_TYPE__LABEL = 3
