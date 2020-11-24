#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include "processor.h"

#include "OS.h"

void press_any_key()
{
    printf("press any key(except for win/ctrl/power off/...) to end program\n");
    int x = getchar();
    if (x == '\n')x = getchar();
}

int main(int argc, char *argv[])
{
    if (argc == 1) {
        printf("please specify the path to the executable file as the first parameter\n");
        press_any_key();
        return 1;
    }

    //TODO:ADD file with hardware characteristics 
    enum {hardware_mem_size = 0x2000};
    uint8_t *mem = calloc(hardware_mem_size, sizeof(*mem));
    if (!mem) {
        press_any_key();
        return 1;
    }
    Processor *proc = processor_create(mem);

    if (!os_load_program(proc, argv[1])) {
        press_any_key();
        return 1;
    }

    os_run_program(proc, 0);

    press_any_key();
    return 0;
}