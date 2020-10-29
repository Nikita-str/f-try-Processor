#pragma once
#ifdef __cplusplus
#include <iostream>
#include <cstdint>
#else
#include <stdint.h>
#endif

enum
{
    IN_sup_NO_ERROR = 0,
    IN_sup_ERROR = 1,
};

#ifdef __cplusplus
extern "C" {
#endif
extern int IN_read_double(double *value);
#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
extern "C" {
#endif
extern int IN_read_int64(int64_t *value);
#ifdef __cplusplus
}
#endif
