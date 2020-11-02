{...} - множество;  
[A|...|Z] - обязательно что-то одно из A...Z;  
[|A|...|Z] - либо пусто либо что-то одно из A..Z;  
s[A|...|Z] - A...Z соотв. чему-то исходя из контекста  
(A|...|Z)? - ничего или (не) любая конечная последовательность из A..Z  
(A|...|Z)?x - ничего или последовательность из A|..|Z длины не более x  

REG[|1|2] = {[E|R][A|B|C|D]X, [A|B|C|D][L,X], R[0|1|...|14|15][|B|W|D]} - регистры общего назначения  
FREG[|1|2] = {FAX, FBX, FCX, FDX, FR[0|1|..|14|15]} - регистры общего назначения с плавающей точкой(double)  
VAL = [0x[0|..|9|A|..|F]|_)?[0|..|9|A|..|F]|([0|..|9]|[_])?[0|...|9]] - иначе говоря число(0, 42, 0xFF_FF, 1_000 ...)  
FVAL = [VAL|VAL.VAL] - число с плав. точкой  
STR = "(A|...|Z|a|...|z|\n|0|...|9|(|+|...|*|)|%)?255" - в общем строка, но из '\?' символов парсится только '\n'  

PPP(op) := x=POP; y=POP; PUSH (op)
Z(A,B) := A 

прим!: стэка 2: для чисел с плав. точкой и для обычных чисел

CMD A B : A - элемент из множества A, B - элемент из множества B  

у нас есть следующие CMD:
- PUSH: '>///<' := заносит в соотв. стэк  
[PUSH|PUSHD|PUSH_4] VAL : '>///<' число(4 байта)  
[PUSHQ|PUSH_8] VAL : '>///<' число(8 байта)  
PUSH REG : '>///<' регистр общего назначения 
PUSH FVAL : '>///<' число с плав. точкой  
PUSH_F [VAL|FVAL] : '>///<' число с плав. точкой  
PUSH FREG : '>///<' регистр с плав. точкой общего назначения  

- POP: '・ー・' := убирает со стэека число; 'OwO' := и заносит его в соотв. регистр
[POP|POP_4|POPD] : '・ー・' (4 байта)  
POP_F : '・ー・' с плав. точкой  
POP REG : '・ー・' 'OwO'(int32)  
POP FREG : '・ー・' 'OwO'(double)  

- q = [ADD|SUB|MUL|DIV]:  
q := POP(x s[+|-|..|/] y)  
q_F := POP_F(x s[+|-|..|/] y)  
q REG VAL : REG = REG s[+|-|..|/] VAL  
q REG1 REG2  : REG1 = REG1 s[+|-|..|/] REG2  
q FREG FVAL : FREG = FREG s[+|-|..|/] FVAL  
q FREG1 FREG2 : FREG1 = FREG1 s[+|-|..|/] FREG2  

- MOV:
MOV REG VAL : REG = VAL  
MOV FREG [|F]VAL : FREG = s[|F]VAL  
MOV REG1 REG2 : REG1 = REG2  
MOV FREG1 FREG2 : FREG1 = FREG2  
MOV REG FREG : REG = (int)FREG  
MOV FREG REG : FREG = REG  

- JUMP:реализован в процессоре, не реализован в {asm->pcode}  

- INC REG : REG = REG + 1
- DEC REG : REG = REG - 1

- OUT:  
OUT REG : output value of REG  
OUT FREG : output value of FREG  
OUT STR : output STR

- IN:
IN REG : waiting for input value(VAL) for REG  
IN FREG : waiting for input value(FVAL) for FREG  

- HLT : stop execution  
