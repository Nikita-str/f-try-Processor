#define _CRT_SECURE_NO_WARNINGS
#include <stdio.h>
#include "processor.h";


size_t get_size_of_file(FILE *f)
{
    long size = fseek(f, 0, SEEK_END);
    if (size)return 0;
    size = ftell(f);
    if (size < 0)return 0;
    rewind(f);
    return (size_t)size;
}

uint8_t *get_memory_from_file(const char *file_name)
{

    FILE *f = fopen(file_name, "rb");
    if (!f) {
        printf("error with read of file\n");
        return NULL;
    }
    size_t mem_size = get_size_of_file(f);
    if (!mem_size) {
        printf("error with read of file\n");
        return NULL;
    }
    uint8_t *mem = (uint8_t *)calloc(mem_size, sizeof(*mem));
    if (!mem) {
        printf("error with memory [BEFORE PROCCESSOR EXECUTION]\n");
        return NULL;
    }

    fread(mem, sizeof(*mem), mem_size, f);
    if (ferror(f)) {
        printf("error with read of file\n");
        free(mem);
        return NULL;
    }
    fclose(f);
    return mem;
}

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
    uint8_t *mem = get_memory_from_file(argv[1]);
    if (!mem) {
        press_any_key();
        return 1;
    }
    Processor *proc = processor_create(mem);
    PROC_CMD_ERROR error = processor_execute(proc, 0);
    while (error == IN_ERROR)error = processor_continue_execution(proc);
    processor_output_error_code(error);
    processor_free(proc, true);

    press_any_key();
    return 0;
}