Files=code.o OS.o processor.o in_sup.o
StackH=Stack/GenericStack.h Stack/GenericStackConfigEnum.h Stack/GenericStackSetEmptyConfig.h
all: proc.exe

proc.exe: $(Files)
	g++ -o $@ $(Files) -lm

code.o: code.c OS.o processor.o
	gcc -c code.c -o code.o -lm

processor.o: processor.c processor.h __processor_utility.h Auxiliary/generic_function.h $(StackH) opcodes.h
	gcc -c processor.c -o processor.o -lm

OS.o: OS.c OS.h processor.h
	gcc -c OS.c -o OS.o -lm

in_sup.o: Auxiliary/IN_support.cpp Auxiliary/IN_support.h
	g++ -c Auxiliary/IN_support.cpp -o in_sup.o -lm -lavcodec

.PHONY: all clean clean_o

clean_o:
	-rm $(Files)

clean:
	-rm $(Files)
	-rm proc.exe
