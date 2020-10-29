#include "IN_support.h"

/// <summary>read double from stdin</summary>
/// <returns>if no error return IN_NO_ERROR</returns>
int IN_read_double(double *value)
{
    double x = 0;
    if (std::cin >> x) {
        *value = x;
        return IN_sup_NO_ERROR;
    }
    return IN_sup_ERROR;
}

/// <summary>read int64_t from stdin</summary>
/// <returns>if no error return IN_NO_ERROR</returns>
int IN_read_int64(int64_t *value)
{
    int64_t x = 0;
    if (std::cin >> x) {
        *value = x;
        return IN_sup_NO_ERROR;
    }
    return IN_sup_ERROR;
}