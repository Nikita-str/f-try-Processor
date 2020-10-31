regs_index = {}
fregs_index = {}

flag_reg_init = False
def reg_init():
    global flag_reg_init;
    if(flag_reg_init): return;
    flag_reg_init = True;
    
    global regs_idex;
    char_gen_reg = ['A', 'B', 'C', 'D']
    ind = 0
    for c in char_gen_reg:
        regs_index[c+'L'] = ind + 1;
        regs_index[c+'X'] = ind + 2;
        regs_index['E'+c+'X'] = ind + 3;
        regs_index['R'+c+'X'] = ind + 4;
        ind += 4;


    global fregs_idex;
    char_gen_reg = ['A', 'B', 'C', 'D']
    ind = 0;
    for c in char_gen_reg:
        fregs_index['F'+c+'X'] = ind + 1;
        ind+=1;
