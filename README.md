# Процессор  
В данном проекте: 
* Реализован синтаксис ассемблерно подобного языка и компилятор в машинный код для него. 
* Эмулируется выполнение данного машиного кода процессором. 
* Также создается маленький заголовочный файл для компилируемого кода.

## Ассемблер & процессор
В данный момент ассемблер включает в себя следующие секции: 
|   имя секции       |             информация о секции               |    статус реализации     |
|--------------------|-----------------------------------------------|--------------------------|
|        code        | содержит непосредственно машинные инструкции  |     неполная(прим.1)     |
|        vars        | содержит переменные и их начальные значения   |     неполная(прим.2)     |
|        var         | содержит единственное определение переменной  |     неполная(прим.3)     |
| run_time_gen_code  | содержит единственное определение переменной  |  запланированная(прим.4) |

###### прим.1: В процессоре все допустимые к текущему моменту команды реализованны. Неполнота заключается в паресере ассемблерного кода: слишком ограниченный парсер для выражений указывающих на область данных, анализируется лишь выражение содержащие не более одного сложения, одного умножения, одного (4 байтного)регистра и двух имен.  
###### прим.2: В прцессоре секций не существуют, все реализованные типы данных поддерживаются. На стадии парсинга асм. кода значение массивов пока-что должно быть записанно на одной строке.  
###### прим.3: Тоже что и в прим.2 + стоит добавить автоматическое добавление команды JUMP когда такая секция встречается после кода не заканчивающегося командой перехода или командой остановки выполнения.  
###### прим.4: Пока что компилятор запрещает явно переходить на секцию данных, однако можно записать указатель на данные в регистр и перейти по значению в регистре. В будущем планируется добавить в заголовочный файл данный(k-бит соответствующие n-байтам) обозначающие что можно делать с данной памятью: читать, писать, исполнять, тогда run_time_gen_code будет единственной секцией поддерживающей все три операции(т.е. нужной как раз для гененрирование кода во время исполнения). Разумеется стоит добавить возможность для ОС менять разрешения для памяти.  
###### прим.: Можно определять имена после их первого использования, однако в некоторых случаях на такое место будут вставленны лишнии команды PASS, т.к. изначально в таких случаях нельзя сказать сколько байт потребуется для команды. В данный момент, подстановка имен в указательные выражение в которых используются имена до их определения не работает, там не дописан код ://. 

### типы данных:
|   имена              | описание                                 | пример определения в секции var |
|----------------------|------------------------------------------|---------------------------------|
| INT1, BYTE           | 1 байтное целое число                    | x BYTE 5                        |
| INT2, WORD           | 2 байтное целое число                    | y inT2 404                      |
| INT4, INT            | 4 байтное целое число                    | z INT -8                        |
| INT8, LONG           | 8 байтное целое число                    | w LONG 0xFB0C_FFFF_FF           |
| DOUBLE, DOUBT, DO_UB | число с плавающей точкой двойной точности| dd DOUBT 12.34                  |
| CSTR                 | строка                                   | "w  rd   , ,, strng  \n"        |
| IARR1, BARR, BARK    | массив 1 байтных числе                   | arr_1 BARK 1, 2, 4, 8, 16       |
| IARR2, WARR, WAR     | массив 2 байтных числе                   | arr_2 WAR  1000, 2000, 9000     |
| IARR4, IARR, LIAR    | массив 4 байтных числе                   | arr_4 IARR4 4_4                 |
| IARR8, QARR, QUARK   | массив 8 байтных числе                   | arr_8 QARR 1234_5678, 90        |
| DARR, DARK           | массив чисел с плав. точкой              | dark DARK 1.2, 2.3, 3.4         |

### регистры: 
недоступные(явно) в ассемблерном коде: 
* RIP - регистр указывающей на текущую команду, используется неявно при любом переходе.   
* FLAGS - регистр хранящий в себе различные свойства предыдущей операции, используется неявно в командах условного перехода.  

Целочисленные регистры общего назначения:
* 8 байт: R[A|B|C|D]X;   R0 .. R15  
* 4 байт: E[A|B|C|D]X;   R0D .. R15D  
* 2 байт: [A|B|C|D]X;    R0W .. R15W  
* 1 байт: [A|B|C|D]H;    R0B .. R15B  

Регистры с плавающей точкой общего назначения: FAX, FBX, FCX, FDX, FR0 .. FR15

### имена функций:
###### прим.: в данный момент CALL и RET не реализованны.  
если строка начинается с '+', '-' или '!' то это функция, причем '!' - точка входа, может быть только одна в программе. '-' - локальная, если будет реализованна линковка, то такие функции не будут видны из других файлов, как следствие на такую функцию делается JUMP посредством разницы между текущей командой и местом определения функции. '+' - глобальная.  

### команды:
###### думаю, следует напомнить что из указательных выражений сейчас парсится только весьма ограниченное количество   

под указательным выражением(далее ув.) понимается выражение вида '[const * reg + name]' и подобные, означающие что процессор должен вычислить(если оно на самом деле не константное, т.е. если оно содержит регистр) значение этого выражения и прочитать определенные данные по этому адресу.  

под 'PPP'(POP x, POP y, PUSH x ACTION y) в таблице буду подразумевать действие со стэком когда мы перем первые два операнда со стэка делаем над ними действие данной команды и кладем значение обратно.  

под 'FFF' понимается тоже самое, но только со стэком чисел с плавающей точкой.   

#### таблица сокращенных операндов:
|сокращение             | соответствующий операнд является            |
|-----------------------|---------------------------------------------|
| REG;   R              | целочисленным регистром общ. назначения     | 
| FREG; FR              | регистром с плав. точкой общ. назначения    | 
| VALUE; V              | числом, типа зависящего от других операндов | 
| CSTR                  | строкой                                     | 
| CONST_PTR; CPTR       | ув. не зависящем от регистров               | 
| NOT_CONST_PTR; NCPTR  | ув. зависящем от регистров                  |

возможные операнды обозначаются как Z_Y, где Z - сокращение пераого операнда, Y - второго. Если стоит одно сокращение значит операнд один.  


| команда  |   действие                                               | возможные операнды                                                 |
|----------|----------------------------------------------------------|--------------------------------------------------------------------|
| PUSH     | если имеет окончание Q то кладет на стэк число 8байтное, \_F - с плав. точкой, иначе 4байтное или зависит от регистра | REG, FREG              |
| POP      | снимает со стэка  4байтное число, не имеет постфикса Q, остальное как у PUSH | REG, FREG                           |
| ADD      | складывает в первый операнд значение второго                              | PPP, FFF, R_V, R_R, FR_V, FR_FR, R_CPTR, R_NCPTR, FR_CPTR, FR_NCPTR|
| SUB      | вычитает из 1-ого оп. 2-ой и записывает значение в 1-ый                   | PPP, FFF, R_V, R_R, FR_V, FR_FR, R_CPTR, R_NCPTR, FR_CPTR, FR_NCPTR|
| MUL      | умножает в 1-ый оп. на 2-ой и записывает значение в 1-ый                  | PPP, FFF, R_V, R_R, FR_V, FR_FR, R_CPTR, R_NCPTR, FR_CPTR, FR_NCPTR|
| DIV      | делит значение 1-ого оп. на значение 2-ого и записывает результат в 1-ый  | PPP, FFF, R_V, R_R, FR_V, FR_FR, R_CPTR, R_NCPTR, FR_CPTR, FR_NCPTR|
| MOV      | изменяет значение первого операнда на значение второго | R_V, R_R, R_FR, FR_V, FR_R, FR_FR, [F]R_[N]CPTR,  [N]CPTR_[F]R  |
| INC      | увеличивает значение регистра на 1   | REG |
| DEC      | уменьшает значение регистра на 1     | REG |
| OUT      | выводит значение операнда на stdout  | REG, FREG, CSTR, CPTR на CSTR |
| IN       | считывает значение регистра с stdin  | REG, FREG|
| HLT      | останавливает выполнение программы   |          |
| PASS     | ничего не делает, занимает 1 байт (прим. 5)   |          |
| CMP      | сравнивает значение операндов, меняет соотв. образом регистр флагов  | REG_VAL, REG_REG, FREG_VAL, FREG_FREG |
| JUMP     | устанавливает следующую команду согласно операнду | REG (4 байтный), а также имя метки или функции|   

также есть следующие команды условного перехода операнды у них теже что и у JUMP'а: 
| команда |  когда осуществляется переход                                                            |
|---------|------------------------------------------------------------------------------------------|
| JZ, JE  | в предыдущей команде изменяющей значение, операнд стал равен 0, или в CMP значения равны |  
|JNZ, JNE | обратный случай к JZ/JE |
|   JOF   | в предыдущей команде произошло переполнение |
|JAZ, JAZZ| значение операнда в предыдущей команде стало больше 0 |
|  JAEZ   | значение операнда в предыдущей команде стало больше или равно 0 |
|  JLZ    | значение операнда в предыдущей команде стало меньше 0 |
|  JLEZ   | значение операнда в предыдущей команде стало меньше или равно 0 |

## Заголовочный файл:
в данный момент, компилятор генерирует файл для псевдо-ОС (см. Processor/OS.h) сейчас он имеет следующую структуру:
|поле              |байты| 
|------------------|-----|
|version           | 4   |
|byte_entry_point  | 4   |
|len_of_program    | 4   |
|x = len_of_entry_point_name  | 4   |
|entry_point_name  | x   |

также это можно использовать для линковки, покрайней мере в текущей версии есть точка входа, добавить имена с глобальной видимостью - не проблема, т.к. они уже все сохранены на время компиляции.  

сейчас используется только поле version и byte_entry_point для определения места где начинать. (если заголовочного файла нет, то предпологается что это старая версия - точка входа в начале файла).


## Сборка:
#### компилятор(py):  
ASMtoProcCode_py/compile_tests.cmd - для компиляции тестовых программ из ASMtoProcCode_py/tests/ в ASMtoProcCode_py/pcodes/  
ASMtoProcCode_py/error_test.cmd - для примера не завиршаемых компиляций из-за ошибок из ASMtoProcCode_py/tests/ в ASMtoProcCode_py/pcodes/  
В случае если это не работает на Linux или если у вас другая версия питона, попрбуйте ввести в терминале:  
python[ver] asm_to_proc_code.py tests/test_[n_test].txt pcodes/[n_test].#pcode#  
python[ver] asm_to_proc_code.py tests/error_[n_err].txt pcodes/not_compile.#pcode#  
например: python3 asm_to_proc_code.py tests/test_6.txt pcodes/6.#pcode#  
ну или выбирете другие имена и дериктории.  
#### процессор(C):    
Если у вас есть VisualStudio то просто оздайте проект и добавьте все заголовочные файлы и файлы с исходным кодом в соответствующие директории.   
Если у вас linux то в папке есть makefile запустите его, должно скомпилироваться.

## Входные параметры:  
Для процессора путь к файлу .#pcode#, если при его компиляции был сгенерирован .#OS_exe_header# файл, то оставьте его рядом с файлом .#pcode# т.к. если точка входа находится не в начале программы, программа начнет выполняться не с того места, что является ошибкой.    


