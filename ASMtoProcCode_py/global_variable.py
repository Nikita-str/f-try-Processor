
# + + + GLOBAL VAR + + + ##################################################################
parse_info = {#'with_section' : False,
              'version' : 0,
              'sections':[], 'loc_names':[], 'glob_names':[],
              'labels':[], 'loc_funcs':[], 'glob_funcs':[],
              'entry_point':None}

expected_names = [] # if name was used before definition: then  expected_names+=[name]

line = None;
ind_line = 0;
asm_file = None;
pcode_file = None;
# - - - GLOBAL VAR - - - ##################################################################

def get_pcode_pos():
    global pcode_file
    return pcode_file.tell()
