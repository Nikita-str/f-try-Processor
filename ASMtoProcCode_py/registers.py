regs_index = {}
fregs_index = {}

def reg_init():
    if reg_init.flag_reg_init: return
    reg_init.flag_reg_init = True
    
    global regs_index
    char_gen_reg = ['A', 'B', 'C', 'D']
    ind = 0
    for c in char_gen_reg:
        regs_index[c+'L'] = ind + 1
        regs_index[c+'X'] = ind + 2
        regs_index['E'+c+'X'] = ind + 3
        regs_index['R'+c+'X'] = ind + 4
        ind += 4
    for i in range(0,16):
        c = str(i)
        regs_index['R'+c+'B'] = ind + 1
        regs_index['R'+c+'W'] = ind + 2
        regs_index['R'+c+'D'] = ind + 3
        regs_index['R'+c] = ind + 4
        ind += 4        


    global fregs_index
    char_gen_reg = ['A', 'B', 'C', 'D']
    ind = 0
    for c in char_gen_reg:
        fregs_index['F'+c+'X'] = ind + 1
        ind+=1
    for i in range(0,16):
        c = str(i)
        fregs_index['FR'+c] = ind + 1
        ind+=1

reg_init.flag_reg_init = False