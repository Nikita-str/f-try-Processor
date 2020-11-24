#include "OS.h"

size_t get_size_of_file(FILE *f)
{
    long size = fseek(f, 0, SEEK_END);
    if (size)return 0;
    size = ftell(f);
    if (size < 0)return 0;
    rewind(f);
    return (size_t)size;
}
uint8_t *get_memory_from_file(const char *file_name, size_t *out_mem_size)
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
    *out_mem_size = mem_size;
    fclose(f);
    return mem;
}

OS_exe_header parse_header(const char *file_name)
{
    OS_exe_header bad_ret = (OS_exe_header){VER_ERR, 0};
    OS_exe_header ret = {0};
    FILE *f = fopen(file_name, "rb");
    if (!f) {
        return (OS_exe_header) {VER_WITHOUT_HEADER, 0};
    }
    
    fread(&ret.version, sizeof(ret.version), 1, f);
    if (ferror(f)) goto BAD_END;
    fread(&ret.entry_point, sizeof(ret.entry_point), 1, f);
    if (ferror(f)) goto BAD_END;
    fread(&ret.sizeof_program, sizeof(ret.sizeof_program), 1, f);
    if (ferror(f)) goto BAD_END;
    fread(&ret.len_of_entry_point_name, sizeof(ret.len_of_entry_point_name), 1, f);
    if (ferror(f)) goto BAD_END;

    char *entry_point_name = (char *)calloc(ret.len_of_entry_point_name+1, sizeof(*entry_point_name));
    if (!entry_point_name) {
        printf("error with memory allocate [BEFORE PROCCESSOR EXECUTION]\n");
        return bad_ret;
    }

    fread(entry_point_name, sizeof(*entry_point_name), ret.len_of_entry_point_name, f);
    entry_point_name[ret.len_of_entry_point_name] = '\0';
    if (ferror(f)) {
        free(entry_point_name);
        goto BAD_END;
    }

    fclose(f);
    return ret;
BAD_END:
    printf("error with read header file\n");
    return bad_ret;
}

bool os_load_program(Processor *proc, char *path)
{
    const static char header_extention[] = ".#OS_exe_header#";

    size_t path_len = strlen(path);
    char *last_point = path;

    for (char *c = path + path_len; c > path; c--) 
        if (c[0] == '.') {
            last_point = c;
            break;
        }

    size_t copy_from_path = (last_point == path ? path_len : last_point - path);
    size_t header_path_len = sizeof(header_extention) + copy_from_path;
    char *header_path = calloc(header_path_len, sizeof(*header_path));
    if (!header_path) {
        return false;
    }

    memcpy(header_path, path, copy_from_path);
    memcpy(header_path + copy_from_path, header_extention, sizeof(header_extention));

    OS_exe_header header = parse_header(header_path);
    if (header.version == VER_ERR) {
        printf("error with header [OS]\n");
        return false;
    }

    size_t mem_size;
    uint8_t *mem = get_memory_from_file(path, &mem_size);
    if (!mem) return false;
  
    //Processor *proc = processor_create(mem);
    processor_mem_map(proc, 0, mem, mem_size, true);

    os_headers[0] = header;
   
    return true;
}

void os_run_program(Processor *proc, uint32_t id)
{
    PROC_CMD_ERROR error = processor_execute(proc, os_headers[id].entry_point);
    while (error == IN_ERROR)error = processor_continue_execution(proc);
    processor_output_error_code(error);
    processor_free(proc, true);
}