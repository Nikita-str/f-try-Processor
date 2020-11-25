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
    uint32_t version;
    uint32_t entry_point;
    uint32_t sizeof_program;
    uint32_t len_of_entry_point_name;
    char *entry_point_name;
}OS_exe_header;

extern OS_exe_header os_headers[1];

extern bool os_load_program(Processor *proc, char *path);
extern void os_run_program(Processor *proc, uint32_t id);


