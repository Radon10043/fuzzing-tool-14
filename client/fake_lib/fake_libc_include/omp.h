#include "_fake_defines.h"
#include "_fake_typedefs.h"

typedef struct omp_lock_t {
    void * _lk;
} omp_lock_t;