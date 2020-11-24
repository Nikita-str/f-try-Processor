#include "processor.h"
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

typedef enum HeaderVersions
{
    VER_WITHOUT_HEADER = -1,
    VER_1 = 1,
    VER_ERR = 0,
}HeaderVersions;

typedef struct OS_exe_header
{
    HeaderVersions version;
    proc_ptr_t entry_point;
    proc_ptr_t sizeof_program;
    size_t len_of_entry_point_name;
    char *entry_point_name;
}OS_exe_header;

//extern size_t get_size_of_file(FILE *f);
//extern uint8_t *get_memory_from_file(const char *file_name, size_t *out_mem_size);

OS_exe_header os_headers[1];

extern bool os_load_program(Processor *proc, char *path);
extern void os_run_program(Processor *proc, uint32_t id);


