
# + + + GLOBAL VAR + + + ##################################################################
parse_info = {#'with_section' : False,
              'version' : 0,
              'sections':[], 'loc_vars':[], 'glob_vars':[],
              'labels':[], 'loc_funcs':[], 'glob_funcs':[],
              'entry_point':None}

expected_names = {} # if name was used before definition: then  expected_names+=[name]
expected_ptr_expression = {}

line = None
ind_line = 0
asm_file = None
pcode_file = None
# - - - GLOBAL VAR - - - ##################################################################
