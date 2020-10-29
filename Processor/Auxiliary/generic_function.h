#pragma once
#include <math.h>
const double GENERIC_EPS = 1e-6;

inline _Bool DoubleEqualDouble(double d1, double d2) { return fabs(d1 - d2) < GENERIC_EPS; }
inline _Bool DoubleEqualZero(double d) { return DoubleEqualDouble(d, 0); }
inline _Bool DoubleAboveZero(double d) { return (d - GENERIC_EPS) > 0; }