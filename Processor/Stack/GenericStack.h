/****
{NOTE:0} 
  don't override NULL it's not funny at all cause its original definition depends on [compiler/<stddef.h> handler]
{NOTE:1}
  if something start with __ it mean: "not use it please". so ponder do you really want use it. 
  if something went wrong after use __%func_name% you deserve it.
{NOTE:2}
  i don't make flags for 1). CANARY_FS_USE_PTR and 2). NOT_REAL_EMPTY_STACK:
        1). as this flag is not recommended
        2). as this flag requires value
{NOTE:3}
  if you want correct auto working of log file then always define different GENERIC_STACK_POSTFIX
  if they are the same in different files, then some log can be lost (by cause reopen log file with its clearing)
  OR
  you may use macro GENERIC_STACK_LOG_FILE with the definition string of the corresponding file in it

{NR:0}
  macros
  CANARY_FS_USE_PTR : NOT RECOMEND ! by cause possibility reallocation dat struct
                        if you use it you should guarantee that there not be mem realloc of generic_stack(corresp. type)
                        OR 
                        use generic_stack_make_valid_canary(corresp. type) after struct mem reallocation
                    AND
                        use only 'new_generic_stack_ptr'
                        OR
                        call 'generic_stack_make_valid_canary' after 'new_generic_stack'

****/

//#define GS_WITH_ERROR_VALIDATE

#ifdef GENERIC_STACK_TYPE
//++++++++##########################[PARANOIC:UNDEFINE]###################

//q.v. {NOTE:0}
#ifndef NULL
#define NULL ((void *)0)
#endif

#undef if 
#undef for
#undef break
#undef while
#undef case
#undef return

//think, it better not undef, cause in Windows in std lib may be #define calloc
#undef realloc
#undef calloc

#undef size_t
#undef canary_t
#undef hash_t

#undef GENERIC_STACK_ENUM_VALIDATE

#undef GS_VALID
#undef GS_NOT_VALID_PTR
#undef GS_ERROR_SIZE
#undef GS_NOT_VALID_STRUCT
#undef GS_LEFT_CANARY_DELIBERATELY_NOT_VALID
#undef GS_RIGHT_CANARY_DELIBERATELY_NOT_VALID
#undef GS_LR_CANARY_DELIBERATELY_NOT_VALID
#undef GS_LEFT_CANARY_NOT_VALID
#undef GS_RIGHT_CANARY_NOT_VALID
#undef GS_LR_CANARY_NOT_VALID
#undef GS_LEFT_DATA_CANARY_DELIBERATELY_NOT_VALID
#undef GS_RIGHT_DATA_CANARY_DELIBERATELY_NOT_VALID
#undef GS_LR_DATA_CANARY_DELIBERATELY_NOT_VALID
#undef GS_LEFT_DATA_CANARY_NOT_VALID
#undef GS_RIGHT_DATA_CANARY_NOT_VALID
#undef GS_LR_DATA_CANARY_NOT_VALID
#undef GS_STRUCT_HASH_NOT_VALID
#undef GS_DATA_HASH_NOT_VALID
#undef GS_ALLOC_ERROR

//---------##########################[PARANOIC:UNDEFINE]###################


//+++++++##################[DEFINE MACRO]##########################
#ifdef GS_CONFIG
#include "GenericStackConfigEnum.h"

    #if (GS_CONFIG & GS_CF_WO_ACV) != 0
    #define WITHOUT_AUTO_CHECK_VALID
    //#else
    //#undef
    #endif

    #if (GS_CONFIG & GS_CF_CIP2) != 0
    #define CAPACITY_IS_POW2
    #endif

    #if (GS_CONFIG & GS_CF_CMP) != 0
    #define COMPARABLE
    #endif

    #if (GS_CONFIG & GS_CF_EDUMP) != 0
    #define ELEM_DUMPABLE
    #endif

    #if (GS_CONFIG & GS_CF_CAN_FS) != 0
    #define CANARY_FOR_STRUCT 
    #endif
    
    #if (GS_CONFIG & GS_CF_CAN_FD) != 0
    #define CANARY_FOR_DATA 
    #endif

    #if (GS_CONFIG & GS_CF_HS) != 0
    #define HASH_STRUCT 
    #endif
    
    #if (GS_CONFIG & GS_CF_HD) != 0
    #define HASH_DATA 
    #endif

    #if (GS_CONFIG & GS_CF_W_EV) != 0
    #define GS_WITH_ERROR_VALIDATE
    #endif
#endif

#ifdef NDEBUG  //?
#define WITHOUT_AUTO_CHECK_VALID
#define GS_WITHOUT_BREAK_STRUCT

#undef CANARY_FOR_STRUCT
#undef CANARY_FS_USE_PTR 
#undef CANARY_FOR_DATA
#undef CANARY_FD_USE_PTR
#undef HASH_STRUCT
#undef HASH_DATA
#undef ELEM_DUMPABLE 
#endif
//-------##################[DEFINE MACRO]##########################

#if defined(CANARY_FOR_STRUCT) || defined(CANARY_FOR_DATA)
#define LEFT_CANARY  0xCD9E5AB7E6DAB69AULL //last bit:0
#define RIGHT_CANARY 0xA96BAD6E7BA5E9DCULL //last bit:0
#define SPECIAL_BAD_CANARY 0x59351A1BADCA1497ULL //last bit:1
#endif

#ifndef GS_MAX_DUMP
#define GS_MAX_DUMP 20
#endif

//(*0+)
#define STR(X) #X
#define MACRO_TO_STR(MACRO) STR(MACRO)
//(*0-)

#ifdef GENERIC_STACK_POSTFIX
#define GLUE_SECRET3(A, B, C) A##B##_##C
#define GLUE_SECRET(A, B, C) GLUE_SECRET3(A, B, C) 
#define GLUE(A, B) GLUE_SECRET(A, B, GENERIC_STACK_POSTFIX) 
#define BACK_GLUE_SECRET3(A, B, C) A##_##B##C
#define BACK_GLUE_SECRET(A, B, C) BACK_GLUE_SECRET3(A, B, C) 
#define BACK_GLUE(A, B) BACK_GLUE_SECRET(A, GENERIC_STACK_POSTFIX, B) 
#else
#define GLUE_SECRET(A, B) A##B
#define GLUE(A, B) GLUE_SECRET(A, B) 
#define BACK_GLUE(A, B) GLUE_SECRET(A, B) 
#endif

#ifdef GENERIC_STACK_POSTFIX
#define GS_GET_TYPE_NAME() MACRO_TO_STR(GENERIC_STACK_TYPE)"_"MACRO_TO_STR(GENERIC_STACK_POSTFIX)
#else
#define GS_GET_TYPE_NAME() MACRO_TO_STR(GENERIC_STACK_TYPE)
#endif

#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <limits.h>
#include <stdbool.h>

//+++++###############################[struct define]######################################################
#define generic_stack(T) GLUE(generic_stack_, T)

#ifndef GENERIC_STACK_CANARY_TYPE_PSOTFIX_0xBc4feJ
#define GENERIC_STACK_CANARY_TYPE_PSOTFIX_0xBc4feJ
typedef unsigned long long canary_t;
typedef unsigned long long hash_t;
#endif

struct generic_stack(GENERIC_STACK_TYPE)
{
    #ifdef CANARY_FOR_STRUCT
    canary_t left_canary;
    //canary_t left_sweet_wine_from_some_islands; one of definitions of the word canary: "canary is a sweet wine from the Canary Islands, similar to Madeira."
    #endif
    #ifdef HASH_STRUCT
    hash_t hash;
    #endif

    size_t size;
    size_t capacity;
    GENERIC_STACK_TYPE *ptr;
 
    #ifdef CANARY_FOR_STRUCT
    canary_t right_canary;
    #endif
};

typedef struct generic_stack(GENERIC_STACK_TYPE) generic_stack(GENERIC_STACK_TYPE);
//-----###############################[struct define]######################################################

//+++++###############################[NOT STATIC FUNC]######################################################
#ifndef GENERIC_STACK_LOG_PSOTFIX_0xEF542EH4
#define GENERIC_STACK_LOG_PSOTFIX_0xEF542EH4

#if defined(GENERIC_STACK_LOG_FILE)
static const char *GS_LOG_FNAME = GENERIC_STACK_LOG_FILE;
#elif defined(GENERIC_STACK_POSTFIX)
static const char *GS_LOG_FNAME = "generic_stack_log_" MACRO_TO_STR(GENERIC_STACK_POSTFIX) ".log";
#else
//q.v. {NOTE:3}
static const char *GS_LOG_FNAME = "generic_stack_log.log";
#endif

static
FILE *generic_stack_log_fopen(const char *name)
{
    static bool CLEAR_LOG_FILE = false;
    if(CLEAR_LOG_FILE)return fopen(name, "a");
    CLEAR_LOG_FILE = true;
    return fopen(name, "w");
}

static 
size_t gs_get_suitable_capacity(size_t capacity)
{
    #ifdef CAPACITY_IS_POW2
    if (capacity == 0)return 0;
    size_t capacity_0 = capacity;
    size_t capacity_pow2 = 1;
    for (int i = 0; i < sizeof(capacity) * CHAR_BIT; i++) {
        if (!capacity) { break; }
        capacity >>= 1;
        capacity_pow2 <<= 1;
    }
    if (capacity_0 && (capacity_pow2 >> 1) == capacity_0) { capacity_pow2 >>= 1; }
    capacity = capacity_pow2;
    #endif
    return capacity;
}
#endif
//-----###############################[NOT STATIC FUNC]######################################################

//+++++###############################[HASHS:real static]#################################################
#if defined(HASH_STRUCT) || defined(HASH_DATA)

#if !defined(GENERIC_STACK_HASH_PSOTFIX_0xCFv54sC4dd)
#define GENERIC_STACK_HASH_PSOTFIX_0xCFv54sC4dd

static inline hash_t __gs_help_get_mem_hash(const char *ptr8byte, size_t index)
{
    const char *cptr = ptr8byte;
    const int SZ = 64; // min for hash_t(ULL) (sizeof(hash_t) * CHAR_BIT);
    const int GS_ONE_BYTE_MASK = 0xFF;

    const int GS_SP_MASK_1_0 = 0x73;
    const int GS_SP_MASK_1_1 = 0x8C;

    const int GS_HASH_MASK_0 = 0x9A;
    const int GS_HASH_MASK_3 = 0xD5;
    const int GS_HASH_MASK_6 = 0x5C;
    const int GS_HASH_MASK_2 = 0x33;
    const int GS_HASH_MASK_15 = 0xAA;
    const int GS_HASH_MASK_47 = 0x55;

    hash_t now = 0;
    //cptr[x] & cptr[y]  || cptr[x] | cptr[y] ?
    now ^= ((hash_t)((cptr[0] ^ GS_HASH_MASK_0) ^ (cptr[3] ^ GS_HASH_MASK_3))) << 5;
    now ^= ((hash_t)((cptr[6] ^ GS_HASH_MASK_6) ^ (cptr[2] ^ GS_HASH_MASK_2)));
    now ^= ((hash_t)((cptr[1] | cptr[5]) ^ GS_HASH_MASK_15)) << 18;
    now ^= ((hash_t)((cptr[4] | ((cptr[7] << 3) & GS_ONE_BYTE_MASK) | (cptr[7] >> 6)) ^ GS_HASH_MASK_47)) << 12;
    now ^= ((hash_t)((cptr[3] & GS_SP_MASK_1_0) | (cptr[6] & GS_SP_MASK_1_1))) << 24;

    now ^= ((hash_t)((cptr[2] ^ GS_HASH_MASK_3) ^ ((cptr[4] << 2) & GS_ONE_BYTE_MASK) ^ (cptr[4] >> 6))) << 39;
    now ^= ((hash_t)((cptr[1] & GS_HASH_MASK_15) ^ (cptr[7] & GS_HASH_MASK_0) ^ ((cptr[5] >> 3) | ((cptr[5] << 5) & GS_ONE_BYTE_MASK)))) << 43;
    now ^= ((hash_t)(cptr[0] ^ (cptr[7] << 5) ^ (cptr[7] >> 4) ^ (cptr[3] << 3) ^ (cptr[3] >> 2))) << 56;
    now ^= ((hash_t)(((cptr[5] << 2) & GS_ONE_BYTE_MASK) ^ GS_HASH_MASK_3 ^ (cptr[5] >> 4) ^ (cptr[2] >> 1))) << 49;

    now ^= ((hash_t)(((cptr[3] << 3) & GS_ONE_BYTE_MASK) ^ GS_HASH_MASK_6 ^ (cptr[3] >> 2) ^ cptr[1])) << 31;
    now ^= ((hash_t)(((cptr[4] << 3) & GS_ONE_BYTE_MASK) ^ (cptr[6] >> 2) ^ cptr[0])) << 36;

    size_t sh = index % SZ;
    now = ((now << sh) | (now >> (SZ - sh))); // ROL now, sh
    return now;
}

//MAYBE:(it makes sense to) make this function faster
static hash_t gs_get_mem_hash(const void *ptr, size_t mem_from, size_t mem_to)
{
    assert(ptr);
    assert(mem_from <= mem_to);
    if (mem_from == mem_to) return 0;

    hash_t ret = 0;

    size_t first_ind = mem_from / sizeof(hash_t);
    size_t last_ind = (mem_to-1) / sizeof(hash_t);

    const char *cptr = ptr;
    cptr += sizeof(ret) * first_ind;

    size_t sh_first = mem_from % sizeof(hash_t);
    if (true || sh_first) {
        char first_cptr[8] = {0,};
        size_t to = sizeof(hash_t);
        if (last_ind == first_ind)to = ((mem_to - 1) % sizeof(hash_t)) + 1;
        for (size_t i = sh_first; i < to; i++) {
            first_cptr[i] = cptr[i];
        }
        ret ^= __gs_help_get_mem_hash(first_cptr, first_ind);
        cptr += sizeof(ret);
    }

    for (size_t i = first_ind + 1; i < last_ind; i++) {
        ret = ret ^ __gs_help_get_mem_hash(cptr, i);
        cptr += sizeof(ret);
    }

    if (first_ind != last_ind) {
        size_t from = last_ind * sizeof(hash_t);
        assert(mem_to - from <= sizeof(hash_t));
        if (from != mem_to) {
            char last_cptr[8] = {0,};
            for (size_t i = from, n = 0; i < mem_to; i++, n++) {
                last_cptr[n] = cptr[n];
            }
            ret = ret ^ __gs_help_get_mem_hash(last_cptr, last_ind);
        }
    }
    return ret;
}

//yes, gs_mem_hash_delete and gs_mem_hash_add do exactly the same
static hash_t gs_mem_hash_delete(hash_t hash, const void *ptr, size_t delete_from, size_t delete_to)
{
    assert(ptr);
    assert(delete_from <= delete_to);
    if (delete_from == delete_to) return hash;
    if (delete_from % sizeof(hash_t)) {
        hash = gs_mem_hash_delete(hash, ptr, delete_from - (delete_from % sizeof(hash_t)), delete_to);
        delete_to = delete_from;
        delete_from = delete_from - (delete_from % sizeof(hash_t));
    }
    return hash ^ gs_get_mem_hash(ptr, delete_from, delete_to);
}

static hash_t gs_mem_hash_add(hash_t hash, const void *ptr, size_t add_from, size_t add_to)
{
    assert(ptr);
    assert(add_from <= add_to);
    if (add_from == add_to) return hash;
    if (add_from % sizeof(hash_t)) {
        hash = gs_mem_hash_delete(hash, ptr, add_from - (add_from % sizeof(hash_t)), add_from); //add_from & MAX_SIZE_T ^ (sizeof(hash_t)-1)
        add_from = add_from - (add_from % sizeof(hash_t));
    }
    return hash ^ gs_get_mem_hash(ptr, add_from, add_to);
}

static bool gs_mem_hash_is_valid(hash_t hash, const void *ptr, size_t mem_from, size_t mem_to)
{
    assert(ptr);
    assert(mem_from <= mem_to);

    return hash == gs_get_mem_hash(ptr, mem_from, mem_to);
}
#endif
#endif
//-----###############################[HASHS:real static]#################################################

//+++++###############################[FOR DATA CANARY]#################################################
#ifdef CANARY_FOR_DATA

#ifdef CANARY_FD_USE_PTR
#define __gs_get_left_data_canary(data_ptr) (LEFT_CANARY ^ (canary_t)(data_ptr))
#define __gs_get_right_data_canary(data_ptr) (RIGHT_CANARY ^ (canary_t)(data_ptr))
#else
#define __gs_get_left_data_canary(data_ptr) (LEFT_CANARY)
#define __gs_get_right_data_canary(data_ptr) (RIGHT_CANARY)
#endif

#endif

//-----###############################[FOR DATA CANARY]#################################################

//+++++###############################[IS_VALID]#################################################
#define generic_stack_is_valid(T) GLUE(generic_stack_is_valid_, T)
#define __generic_stack_valid_canary(T) GLUE(__generic_stack_valid_canary_, T)
#ifdef CANARY_FOR_DATA
#define __generic_stack_valid_data_canary(T) GLUE(__generic_stack_valid_data_canary_, T)
#endif
#if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
#define generic_stack_make_valid_canary(T) GLUE(generic_stack_make_valid_canary_, T)
#endif
#ifndef GS_ENUM_VALIDATE
#define GS_ENUM_VALIDATE
typedef enum GENERIC_STACK_ENUM_VALIDATE
{
    GS_VALID,
    GS_NOT_VALID_PTR,
    GS_ERROR_SIZE,
    GS_NOT_VALID_STRUCT,
    //canary:
    GS_LEFT_CANARY_DELIBERATELY_NOT_VALID,
    GS_RIGHT_CANARY_DELIBERATELY_NOT_VALID,
    GS_LR_CANARY_DELIBERATELY_NOT_VALID,
    GS_LEFT_CANARY_NOT_VALID,
    GS_RIGHT_CANARY_NOT_VALID,
    GS_LR_CANARY_NOT_VALID,
    //data canary:
    GS_LEFT_DATA_CANARY_DELIBERATELY_NOT_VALID,
    GS_RIGHT_DATA_CANARY_DELIBERATELY_NOT_VALID,
    GS_LR_DATA_CANARY_DELIBERATELY_NOT_VALID,
    GS_LEFT_DATA_CANARY_NOT_VALID,
    GS_RIGHT_DATA_CANARY_NOT_VALID,
    GS_LR_DATA_CANARY_NOT_VALID,
    //hash:
    GS_STRUCT_HASH_NOT_VALID,
    GS_DATA_HASH_NOT_VALID,
    //mem_error:
    GS_ALLOC_ERROR,
}GENERIC_STACK_ENUM_VALIDATE;
#endif
#ifdef GS_WITH_ERROR_VALIDATE
#define GS_LAST_PARAM , GENERIC_STACK_ENUM_VALIDATE *gs_error
#else
#define GS_LAST_PARAM  
#endif

//#pragma OwO real static next line
static
GENERIC_STACK_ENUM_VALIDATE __generic_stack_valid_canary(GENERIC_STACK_TYPE) (const generic_stack(GENERIC_STACK_TYPE) *self)
{
    //switch not can be turn into function by cause in statement 'case x:' x need be const      :|
    //and macro will only worsen readability 

    //not need if it real private     but it don't         :|
    if (!self) {
        return GS_NOT_VALID_STRUCT;
    }

    #ifdef CANARY_FOR_STRUCT
    int canary_valid = 0b11;

    //this is separate case cause it's suspicious:
    canary_valid ^= ((self->left_canary != SPECIAL_BAD_CANARY)) + ((self->right_canary != SPECIAL_BAD_CANARY) << 1);
    switch (canary_valid) {
    case 0b01:return GS_LEFT_CANARY_DELIBERATELY_NOT_VALID;
    case 0b10:return GS_RIGHT_CANARY_DELIBERATELY_NOT_VALID;
    case 0b11:return GS_LR_CANARY_DELIBERATELY_NOT_VALID;
    default:break;
    }

    canary_valid = 0b11;
    #ifdef CANARY_FS_USE_PTR
    canary_valid ^= ((self->left_canary ^ (canary_t)self) == LEFT_CANARY) + (((self->right_canary ^ (canary_t)self) == RIGHT_CANARY) << 1);
    #else
    canary_valid ^= ((self->left_canary == LEFT_CANARY)) + ((self->right_canary == RIGHT_CANARY) << 1);
    #endif
    switch (canary_valid) {
    case 0b01:return GS_LEFT_CANARY_NOT_VALID;
    case 0b10:return GS_RIGHT_CANARY_NOT_VALID;
    case 0b11:return GS_LR_CANARY_NOT_VALID;
    default:break;
    }
    #endif

    return GS_VALID;
}

#ifdef CANARY_FOR_DATA
static
GENERIC_STACK_ENUM_VALIDATE __generic_stack_valid_data_canary(GENERIC_STACK_TYPE) (const generic_stack(GENERIC_STACK_TYPE) *self)
{
    //not need if it real private     but it don't         :|
    if (!self) {
        return GS_NOT_VALID_STRUCT;
    }

    int canary_valid = 0b11;

    #ifdef HASH_DATA
    canary_t left_canary = ((canary_t *)(((hash_t *)self->ptr) - 1))[-1];
    #else
    canary_t left_canary = ((canary_t *)self->ptr)[-1];
    #endif
    canary_t right_canary = ((canary_t *)(self->ptr + self->capacity))[0];

    //this is separate case cause it's suspicious:
    canary_valid ^= ((left_canary != SPECIAL_BAD_CANARY)) + ((right_canary != SPECIAL_BAD_CANARY) << 1);
    switch (canary_valid) {
    case 0b01:return GS_LEFT_DATA_CANARY_DELIBERATELY_NOT_VALID;
    case 0b10:return GS_RIGHT_DATA_CANARY_DELIBERATELY_NOT_VALID;
    case 0b11:return GS_LR_DATA_CANARY_DELIBERATELY_NOT_VALID;
    default:break;
    }
    canary_valid = 0b11;

    canary_valid ^= (left_canary == __gs_get_left_data_canary(self->ptr)) + ((right_canary == __gs_get_right_data_canary(self->ptr)) << 1);
    switch (canary_valid) {
    case 0b01:return GS_LEFT_DATA_CANARY_NOT_VALID;
    case 0b10:return GS_RIGHT_DATA_CANARY_NOT_VALID;
    case 0b11:return GS_LR_DATA_CANARY_NOT_VALID;
    default:break;
    }

    return GS_VALID;
}
#endif

static
GENERIC_STACK_ENUM_VALIDATE generic_stack_is_valid(GENERIC_STACK_TYPE) (const generic_stack(GENERIC_STACK_TYPE) *self)
{
    if (!self) {
        return GS_NOT_VALID_STRUCT;
    }

    bool is_empty_struct = (self->capacity == 0) && (self->size == 0) && (self->ptr == NULL);

    if (!is_empty_struct) {
        if (!self->ptr) {
            return GS_NOT_VALID_PTR;
        }
        if (self->capacity < self->size) {
            return GS_ERROR_SIZE;
        }
    }

    #ifdef CANARY_FOR_STRUCT
    GENERIC_STACK_ENUM_VALIDATE valid_canary = GS_VALID;
    valid_canary = __generic_stack_valid_canary(GENERIC_STACK_TYPE)(self);
    if (valid_canary != GS_VALID) return valid_canary;
    #endif
    if (!is_empty_struct) {
        #ifdef CANARY_FOR_DATA
        GENERIC_STACK_ENUM_VALIDATE valid_data_canary = GS_VALID;
        valid_data_canary = __generic_stack_valid_data_canary(GENERIC_STACK_TYPE)(self);
        if (valid_data_canary != GS_VALID) return valid_data_canary;
        #endif
    }

    #ifdef HASH_STRUCT
    if (!gs_mem_hash_is_valid(self->hash, &(self->size), 0, ((char *)&self->ptr) - ((char *)&self->size) + sizeof(self->ptr))) {
        return GS_STRUCT_HASH_NOT_VALID;
    }
    #endif 
    if (!is_empty_struct) {
        #ifdef HASH_DATA
        hash_t hash_data = ((hash_t *)self->ptr)[-1];
        if (!gs_mem_hash_is_valid(hash_data, self->ptr, 0, sizeof(*self->ptr) * self->size)) {
            return GS_DATA_HASH_NOT_VALID;
        }
        #endif
    }

    return GS_VALID;
}

#if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
static
void generic_stack_make_valid_canary(GENERIC_STACK_TYPE) (generic_stack(GENERIC_STACK_TYPE) *self)
{
    self->left_canary = LEFT_CANARY ^ (canary_t)self;
    self->right_canary = RIGHT_CANARY ^ (canary_t)self;
}
#endif

//-----###############################[IS_VALID]#################################################

//+++++###############################[DUMP/LOG]#################################################

#define generic_stack_dump(T) GLUE(generic_stack_dump_, T)

#define generic_stack_get_elem_dump(T) BACK_GLUE(T, _gs_elem_dump)
#define generic_stack_elem_dump(T) BACK_GLUE(T, _gs_elem_dump)

#define __GS_ONE_ELEM_DUMP(self, GS_TYPE, X_file, X_ind)       \
fprintf(X_file, "    [%u] {", X_ind);                          \
generic_stack_elem_dump(GS_TYPE)(X_file, self->ptr[X_ind]);    \
fprintf(X_file, "}\n");

static
void generic_stack_dump(GENERIC_STACK_TYPE)(const generic_stack(GENERIC_STACK_TYPE) *self, FILE *generic_stack_log_file, size_t max)
{
    if (!generic_stack_log_file) {
        generic_stack_log_file = generic_stack_log_fopen(GS_LOG_FNAME);
        if (!generic_stack_log_file) { return; }
    }
    fprintf(generic_stack_log_file, "  [%p] generic_stack(%s):\n", self, GS_GET_TYPE_NAME()); //MACRO_TO_STR(GENERIC_STACK_TYPE)
    if (!self) { goto GS_DUMP_CLOSE_RETURN; }
    fprintf(generic_stack_log_file, "    size:%u  capacity:%u  ptr:[%p]:\n", self->size, self->capacity, self->ptr);
    #ifdef CANARY_FOR_STRUCT
    GENERIC_STACK_ENUM_VALIDATE valid_canary = GS_VALID;
    valid_canary = __generic_stack_valid_canary(GENERIC_STACK_TYPE)(self);
    if (valid_canary != GS_VALID) {
        fprintf(generic_stack_log_file, "    [NOT VALID]:\n");
    }
    switch (valid_canary) {
    case GS_LEFT_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: only left canary deliberately not valid\n    it is suspicious\n");
        break;
    case GS_RIGHT_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: only right canary deliberately not valid\n    it is suspicious\n");
        break;
    case GS_LR_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: left and right canary deliberately not valid\n");
        break;
    case GS_LEFT_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: only left canary not valid => data may not be valid\n");
        break;
    case GS_RIGHT_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: only right canary not valid => data may not be valid\n");
        break;
    case GS_LR_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for struct: left and right canary not valid => data may not be valid\n");
        break;
    case GS_VALID:
        fprintf(generic_stack_log_file, "    [valid]:struct canaries\n");
        break;
    default:fprintf(generic_stack_log_file, "    for struct: something really strange happened\n    function %s not valid ! IMPORTANT\n", 
                                            MACRO_TO_STR(generic_stack_valid_canary(GENERIC_STACK_TYPE)));
    }
    #endif

    #ifdef HASH_STRUCT
    if (!gs_mem_hash_is_valid(self->hash, &(self->size), 0, ((char *)&self->ptr) - ((char *)&self->size) + sizeof(self->ptr))) {
        fprintf(generic_stack_log_file, "    [NOT VALID]:hash of struct\n");
    } else {
        fprintf(generic_stack_log_file, "    [valid]:hash of struct\n");
    }
    #endif

    size_t size = self->size;
    size_t capacity = self->capacity;
    bool valid_size = size <= capacity;
    if (!valid_size) {
        fprintf(generic_stack_log_file, "    capacity < size ! struct not valid\n");
        size = capacity;
    }

    fclose(generic_stack_log_file);
    generic_stack_log_file = generic_stack_log_fopen(GS_LOG_FNAME);

    if (!self->ptr) { goto GS_DUMP_CLOSE_RETURN; }
    #ifdef CANARY_FOR_DATA
    GENERIC_STACK_ENUM_VALIDATE valid_data_canary = GS_VALID;
    valid_data_canary = __generic_stack_valid_data_canary(GENERIC_STACK_TYPE)(self);
    if (valid_data_canary != GS_VALID) {
        fprintf(generic_stack_log_file, "    [NOT VALID]:\n");
    }
    switch (valid_data_canary) {
    case GS_LEFT_DATA_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: only left canary deliberately not valid\n    it is suspicious\n");
        break;
    case GS_RIGHT_DATA_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: only right canary deliberately not valid\n    it is suspicious\n");
        break;
    case GS_LR_DATA_CANARY_DELIBERATELY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: left and right canary deliberately not valid\n");
        break;
    case GS_LEFT_DATA_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: only left canary not valid => data may not be valid\n");
        break;
    case GS_RIGHT_DATA_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: only right canary not valid => data may not be valid\n");
        break;
    case GS_LR_DATA_CANARY_NOT_VALID:
        fprintf(generic_stack_log_file, "    for data: left and right canary not valid => data may not be valid\n");
        break;
    case GS_VALID: 
        fprintf(generic_stack_log_file, "    [valid]:data canaries\n");
        break;
    default:fprintf(generic_stack_log_file, "    for data: something really strange happened\n    function %s not valid ! IMPORTANT\n",
        MACRO_TO_STR(generic_stack_valid_canary(GENERIC_STACK_TYPE)));
    }
    #endif
    #ifdef HASH_DATA
    hash_t hash_data = ((hash_t *)self->ptr)[-1];
    if (!gs_mem_hash_is_valid(hash_data, self->ptr, 0, sizeof(*self->ptr) * self->size)) {
        fprintf(generic_stack_log_file, "    [NOT VALID]:hash of data\n");
    } else {
        fprintf(generic_stack_log_file, "    [valid]:hash of data\n");
    }
    #endif

    #ifdef ELEM_DUMPABLE
    fprintf(generic_stack_log_file, "    {\n");
    if (max != 0 && max < capacity + 2 && valid_size) {
        size_t to = max / 2;
        if (to > size) {
            to = size;
        }
        for (size_t ind = 0; ind < to; ind++) {
            __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, ind);
        }
        if (to * 2 < size) {
            fprintf(generic_stack_log_file, "    ...\n");
        }
        size_t from = size - to; //can overflow but it doesn't matter cause next if
        if (size < to) {
            from = to + 1;
        }
        for (size_t ind = from; ind < size; ind++) {
            __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, ind);
        }
        fprintf(generic_stack_log_file, "    ===============================================================================:stack.size\n");
        if (size + 1 < capacity) {
            __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, size + 1);
            if (size + 3 < capacity) {
                fprintf(generic_stack_log_file, "    ...\n");
            }
            if (size + 2 < capacity) {
                __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, capacity - 1);
            }
        }

    } else {
        for (size_t ind = 0; ind < size; ind++) {
            __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, ind);
        }
        fprintf(generic_stack_log_file, "    ===============================================================================:stack.size\n");
        for (size_t ind = size; ind < capacity; ind++) {
            __GS_ONE_ELEM_DUMP(self, GENERIC_STACK_TYPE, generic_stack_log_file, ind);
        }
    }
    fprintf(generic_stack_log_file, "    }\n");
    #else
    fprintf(generic_stack_log_file, "    no func for dump elem\n");
    #endif

GS_DUMP_CLOSE_RETURN:
    fprintf(generic_stack_log_file, "#####################################################################\n\n\n");
    fclose(generic_stack_log_file);
}

#define GENERIC_STACK_LOG(GS_TYPE, self, max, dop_print)                             \
{                                                                                    \
    FILE *generic_stack_log_file = generic_stack_log_fopen(GS_LOG_FNAME);            \
    if (generic_stack_log_file) {                                                    \
    if(dop_print[0] != '\0')fprintf(generic_stack_log_file, "%s\n", dop_print);      \
    fprintf(generic_stack_log_file, "%s: %s+%u:\n", __FILE__, __FUNCTION__, __LINE__);  \
    generic_stack_dump(GS_TYPE)(self, generic_stack_log_file, max);                  \
    }                                                                                \
}

#define __generic_stack_err_print(T) GLUE(__generic_stack_err_print, T)
static void __generic_stack_err_print(GENERIC_STACK_TYPE)(){fprintf(stderr, "error with: "GS_GET_TYPE_NAME() "\n");}

#ifdef GS_WITH_ERROR_VALIDATE
#define GENERIC_STACK_AUTO_VALIDATE(GS_TYPE, self, max, dop_print, type) \
if(!gs_error)return (type){0};                                           \
if ((*gs_error = generic_stack_is_valid(GS_TYPE)(self)) != GS_VALID) {   \
    GENERIC_STACK_LOG(GS_TYPE, self, max, dop_print);                    \
    __generic_stack_err_print(GENERIC_STACK_TYPE)();                     \
    return (type){0};                                                    \
}
#define GENERIC_STACK_AUTO_VALIDATE_VOIDF(GS_TYPE, self, max, dop_print) \
if(!gs_error)return;                                                     \
if ((*gs_error = generic_stack_is_valid(GS_TYPE)(self)) != GS_VALID) {   \
    GENERIC_STACK_LOG(GS_TYPE, self, max, dop_print);                    \
    __generic_stack_err_print(GENERIC_STACK_TYPE)();                     \
    return;                                                              \
}
//i want to write 'return;' instead 'return ret;' but someone told me that this is prohibited by the standard
#else
//there we dont use 'type':
#define GENERIC_STACK_AUTO_VALIDATE(GS_TYPE, self, max, dop_print, type)  \
if (generic_stack_is_valid(GS_TYPE)(self) != GS_VALID) {   \
GENERIC_STACK_LOG(GS_TYPE, self, max, dop_print);          \
__generic_stack_err_print(GENERIC_STACK_TYPE)();           \
assert(!"check log file");                                 \
exit(1);                                                   \
}
#define GENERIC_STACK_AUTO_VALIDATE_VOIDF(GS_TYPE, self, max, dop_print) GENERIC_STACK_AUTO_VALIDATE(GS_TYPE, self, max, dop_print, )
#endif

#ifdef WITHOUT_AUTO_CHECK_VALID
#define __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, type)  
#define __GENERIC_STACK_AUTO_VALIDATE_AFTER(self, type)  
#define __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self)  
#define __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self)  
#else
#define __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, type) GENERIC_STACK_AUTO_VALIDATE(GENERIC_STACK_TYPE, self, GS_MAX_DUMP, "[BEFORE FUNCTION]:", type)
#define __GENERIC_STACK_AUTO_VALIDATE_AFTER(self, type) GENERIC_STACK_AUTO_VALIDATE(GENERIC_STACK_TYPE, self, GS_MAX_DUMP, "[AFTER FUNCTION]:", type)
#define __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self) GENERIC_STACK_AUTO_VALIDATE_VOIDF(GENERIC_STACK_TYPE, self, GS_MAX_DUMP, "[BEFORE FUNCTION]:")
#define __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self) GENERIC_STACK_AUTO_VALIDATE_VOIDF(GENERIC_STACK_TYPE, self, GS_MAX_DUMP, "[AFTER FUNCTION]:")
#endif
//-----###############################[DUMP/LOG]#################################################

//+++++###############################[NEW]######################################################

//++ define func name:

#if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
#define generic_stack_make_valid_canary(T) GLUE(generic_stack_make_valid_canary_, T)
static void generic_stack_make_valid_canary(GENERIC_STACK_TYPE) (generic_stack(GENERIC_STACK_TYPE) *self);
#endif
//--

#define new_generic_stack(T) GLUE(new_generic_stack_, T)
#define new_generic_stack_ptr(T) GLUE(new_generic_stack_ptr_, T)
#define __generic_stack_calloc(T) GLUE(__generic_stack_calloc_, T)
#define __generic_stack_realloc(T) GLUE(__generic_stack_realloc_, T)

#ifdef  GS_WITH_ERROR_VALIDATE
#define GS_ALLOC_EXIT()     \
*gs_error = GS_ALLOC_ERROR; \
return NULL;
#else
#define GS_ALLOC_EXIT() exit(1);
#endif

static
GENERIC_STACK_TYPE *__generic_stack_calloc(GENERIC_STACK_TYPE) (size_t capacity GS_LAST_PARAM)
{
    GENERIC_STACK_TYPE *ptr = NULL;
    if (capacity) {
        #ifdef CAPACITY_IS_POW2
        capacity = gs_get_suitable_capacity(capacity);
        #endif
        #if defined(CANARY_FOR_DATA) || defined(HASH_DATA)
        size_t add_size = 0;
        size_t minus_size = 0;
        #ifdef CANARY_FOR_DATA
        minus_size = sizeof(canary_t);
        add_size += sizeof(canary_t) * 2;
        #endif
        #ifdef HASH_DATA
        add_size += sizeof(hash_t);
        #endif
        size_t needable_byte = sizeof(GENERIC_STACK_TYPE) * capacity + add_size;
        void *data_ptr = calloc(1, needable_byte);
        if (!data_ptr) { GS_ALLOC_EXIT(); }

        ptr = (GENERIC_STACK_TYPE *)(((char *)data_ptr) + add_size - minus_size);
        #ifdef CANARY_FOR_DATA
        ((canary_t *)data_ptr)[0] = __gs_get_left_data_canary(ptr);
        ((canary_t *)(ptr + capacity))[0] = __gs_get_right_data_canary(ptr);
        #endif
        #else //defined(CANARY_FOR_DATA) || defined(HASH_DATA)
        ptr = calloc(capacity, sizeof(GENERIC_STACK_TYPE));
        if (!ptr) { GS_ALLOC_EXIT(); }
        #endif
    }
    return ptr;
}

#ifdef  GS_WITH_ERROR_VALIDATE
#define ___generic_stack_calloc(capacity, type)                  \
__generic_stack_calloc(GENERIC_STACK_TYPE)(capacity, gs_error);  \
if(*gs_error != GS_VALID)return (type){0};
#else
#define ___generic_stack_calloc(capacity, type) __generic_stack_calloc(GENERIC_STACK_TYPE)(capacity)
#endif

static
GENERIC_STACK_TYPE *__generic_stack_realloc(GENERIC_STACK_TYPE) (GENERIC_STACK_TYPE *ptr, size_t new_capacity GS_LAST_PARAM)
{
    //if (!ptr) return NULL;
    #ifdef CAPACITY_IS_POW2
    new_capacity = gs_get_suitable_capacity(new_capacity);
    #endif
    if (!ptr) {
        ptr = ___generic_stack_calloc(new_capacity, GENERIC_STACK_TYPE *);
        return ptr;
    }

    void *temp_ptr = NULL;

    size_t add_size = 0;
    size_t minus_size = 0;

    #ifdef CANARY_FOR_DATA
    add_size += sizeof(canary_t) * 2;
    minus_size += sizeof(canary_t);
    #endif
    #ifdef HASH_DATA
    add_size += sizeof(hash_t);
    minus_size += sizeof(hash_t);
    #endif

    size_t needable_byte = sizeof(GENERIC_STACK_TYPE) * new_capacity + add_size;
    void *realloc_ptr = ((char *)ptr) - minus_size;
    if (new_capacity == 0) {
        free(realloc_ptr);
        ptr = NULL;
        return ptr;
    }
    temp_ptr = realloc(realloc_ptr, needable_byte);
    if (!temp_ptr) {
        GS_ALLOC_EXIT();
    }

    ptr = (GENERIC_STACK_TYPE *)((char *)temp_ptr + minus_size);

    #ifdef CANARY_FOR_DATA
    ((canary_t *)temp_ptr)[0] = __gs_get_left_data_canary(ptr);
    ((canary_t *)(ptr + new_capacity))[0] = __gs_get_right_data_canary(ptr);
    #endif

    return ptr;
}
#ifdef  GS_WITH_ERROR_VALIDATE
#define ___generic_stack_realloc(ptr, capacity)                        \
__generic_stack_realloc(GENERIC_STACK_TYPE)(ptr, capacity, gs_error);  \
if(*gs_error != GS_VALID)return;
#else
#define ___generic_stack_realloc(ptr, capacity) __generic_stack_realloc(GENERIC_STACK_TYPE)(ptr, capacity)
#endif


#undef GS_ALLOC_EXIT()     

static
generic_stack(GENERIC_STACK_TYPE) new_generic_stack(GENERIC_STACK_TYPE) (size_t capacity GS_LAST_PARAM)
{
    #ifdef CAPACITY_IS_POW2
    capacity = gs_get_suitable_capacity(capacity);
    #endif
    generic_stack(GENERIC_STACK_TYPE) stack = {0,};

    stack.ptr = ___generic_stack_calloc(capacity, generic_stack(GENERIC_STACK_TYPE));

    #ifdef CANARY_FOR_STRUCT
    #ifdef CANARY_FS_USE_PTR //NOT RECOMEND ! by cause possibility reallocation dat struct q.v. {NR:0}
    stack.left_canary = LEFT_CANARY ^ (canary_t)&stack;
    stack.right_canary = RIGHT_CANARY ^ (canary_t)&stack;
    #else
    stack.left_canary = LEFT_CANARY;
    stack.right_canary = RIGHT_CANARY;
    #endif
    #endif

    if (capacity && !stack.ptr) {
        #ifdef  GS_WITH_ERROR_VALIDATE
        *gs_error = GS_ALLOC_ERROR;
        return (generic_stack(GENERIC_STACK_TYPE)) { 0 };
        #else
        exit(1);
        #endif
    }
    stack.capacity = capacity;

    #ifdef HASH_STRUCT
    stack.hash = gs_get_mem_hash(&(stack.size), 0, ((char *)&stack.ptr) - ((char *)&stack.size) + sizeof(stack.ptr)); // cast to (char *) is otional (it make warning from compiler)
    #endif

    generic_stack(GENERIC_STACK_TYPE) *self = &stack;
    __GENERIC_STACK_AUTO_VALIDATE_AFTER(self, generic_stack(GENERIC_STACK_TYPE));
    return stack;
}

#ifdef  GS_WITH_ERROR_VALIDATE
#define GS_NEW_CALL(capacity) new_generic_stack(GENERIC_STACK_TYPE)(capacity, gs_error)
#else
#define GS_NEW_CALL(capacity) new_generic_stack(GENERIC_STACK_TYPE)(capacity)
#endif

static
generic_stack(GENERIC_STACK_TYPE) *new_generic_stack_ptr(GENERIC_STACK_TYPE) (size_t capacity GS_LAST_PARAM)
{
    generic_stack(GENERIC_STACK_TYPE) *self = calloc(1, sizeof(*self));
    *self = GS_NEW_CALL(capacity);
    #ifdef GS_WITH_ERROR_VALIDATE
    if (*gs_error != GS_VALID) {
        return self;
    }
    #endif
    #if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
    generic_stack_make_valid_canary(GENERIC_STACK_TYPE)(self);
    #endif
    return self;
}

#define new_empty_generic_stack(T) GLUE(new_empty_generic_stack_, T)

static generic_stack(GENERIC_STACK_TYPE)
#ifdef  GS_WITH_ERROR_VALIDATE
new_empty_generic_stack(GENERIC_STACK_TYPE) (GENERIC_STACK_ENUM_VALIDATE *gs_error)
#else
new_empty_generic_stack(GENERIC_STACK_TYPE) ()
#endif
{
    enum
    {
        DEFAULT_CAPACITY =
        #ifdef NOT_REAL_EMPTY_STACK
        NOT_REAL_EMPTY_STACK
        #else
        0x0
        #endif
    };
    return GS_NEW_CALL(DEFAULT_CAPACITY);
}
#undef GS_NEW_CALL
//-----###############################[NEW]######################################################

//+++++###############################[FREE]#####################################################
#define free_generic_stack(T) GLUE(free_generic_stack_, T)

static
void free_generic_stack(GENERIC_STACK_TYPE) (generic_stack(GENERIC_STACK_TYPE) *self GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self);
    size_t minus_size = 0;
    #ifdef CANARY_FOR_DATA
    minus_size += sizeof(canary_t);
    #endif
    #ifdef HASH_DATA
    minus_size += sizeof(hash_t);
    #endif
    free(((char *)self->ptr) - minus_size);

    #ifndef GS_WITHOUT_BREAK_STRUCT
    self->size = ~0 ^ 0xA35;
    self->capacity = 0x55;
    self->ptr = NULL;
    #ifdef CANARY_FOR_STRUCT
    self->left_canary = SPECIAL_BAD_CANARY;
    self->right_canary = SPECIAL_BAD_CANARY;
    #endif
    #endif // !GS_WITHOUT_BREAK_STRUCT
}
//-----###############################[FREE]#####################################################

//+++++###############################[PUSH&POP]#################################################
#define generic_stack_push(T) GLUE(generic_stack_push_, T)

static
void generic_stack_push(GENERIC_STACK_TYPE) (generic_stack(GENERIC_STACK_TYPE) *self, GENERIC_STACK_TYPE elem GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self);

    if (self->size == self->capacity) {

        size_t new_capacity = self->capacity ? self->capacity * 2 : 1;
        self->ptr = ___generic_stack_realloc(self->ptr, new_capacity);

        self->capacity = new_capacity;
    }
    self->ptr[self->size++] = elem;

    #ifdef HASH_DATA
    hash_t hash = ((hash_t *)self->ptr)[-1];
    ((hash_t *)self->ptr)[-1] = gs_mem_hash_add(hash, self->ptr, sizeof(*self->ptr) * (self->size - 1), sizeof(*self->ptr) * self->size);
    #endif

    #ifdef HASH_STRUCT
    self->hash = gs_get_mem_hash(&(self->size), 0, ((char *)&self->ptr) - ((char *)&self->size) + sizeof(self->ptr));
    #endif
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self);
}

#ifdef  GS_WITH_ERROR_VALIDATE
#define GS_ELEM_EXIT()                            \
*gs_error = GS_ERROR_SIZE;                        \
return (GENERIC_STACK_TYPE) { 0 };                
#else
#define GS_ELEM_EXIT() exit(1);
#endif

#define generic_stack_pop(T) GLUE(generic_stack_pop_, T)

static
GENERIC_STACK_TYPE generic_stack_pop(GENERIC_STACK_TYPE) (generic_stack(GENERIC_STACK_TYPE) *self GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, GENERIC_STACK_TYPE);
    if (self->size == 0) {
        GS_ELEM_EXIT();
    } 
    #ifdef HASH_STRUCT
        self->hash = gs_mem_hash_delete(self->hash, &(self->size), 0, sizeof(self->size));
    #endif
    #ifdef HASH_DATA
    hash_t hash = ((hash_t *)self->ptr)[-1];
    ((hash_t *)self->ptr)[-1] = gs_mem_hash_delete(hash, self->ptr, sizeof(*self->ptr) * (self->size - 1), sizeof(*self->ptr) * self->size);
    #endif
    GENERIC_STACK_TYPE ret = self->ptr[--self->size];
    #ifdef HASH_STRUCT
    self->hash = gs_mem_hash_add(self->hash, &(self->size), 0, sizeof(self->size));
    #endif
    __GENERIC_STACK_AUTO_VALIDATE_AFTER(self, GENERIC_STACK_TYPE);
    return ret;
}
//-----###############################[PUSH&POP]#################################################

//+++++#################################[CHANGE CAPACITY]##########################################
#define generic_stack_set_capacity(T) GLUE(generic_stack_set_capacity_, T)
#define generic_stack_squeeze_capacity(T) GLUE(generic_stack_squeeze_capacity_, T)

static 
void  generic_stack_set_capacity(GENERIC_STACK_TYPE)(generic_stack(GENERIC_STACK_TYPE) *self, size_t new_capacity GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self);
    self->ptr = ___generic_stack_realloc(self->ptr, new_capacity);
    if (new_capacity < self->size)self->size = new_capacity;
    new_capacity = gs_get_suitable_capacity(new_capacity);
    self->capacity = new_capacity;
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self);
}

static
void  generic_stack_squeeze_capacity(GENERIC_STACK_TYPE)(generic_stack(GENERIC_STACK_TYPE) *self GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self);
    self->ptr = ___generic_stack_realloc(self->ptr, self->size);
    self->capacity = gs_get_suitable_capacity(self->size);
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self);
}
//-----#################################[CHANGE CAPACITY]##########################################


//+++++###############################[TOP]#################################################
#define generic_stack_top(T) GLUE(generic_stack_top_, T)

static
GENERIC_STACK_TYPE generic_stack_top(GENERIC_STACK_TYPE) (const generic_stack(GENERIC_STACK_TYPE) *self GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, GENERIC_STACK_TYPE);
    if (self->size == 0) {
        GS_ELEM_EXIT();
    }
    return self->ptr[self->size];
}
//-----###############################[TOP]#################################################

//+++++###############################[EMPTY]#################################################
#define generic_stack_empty(T) GLUE(generic_stack_empty_, T)

static bool generic_stack_empty(GENERIC_STACK_TYPE) 
(const generic_stack(GENERIC_STACK_TYPE) *self GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, bool);
    return self->size == 0;
}
//-----###############################[EMPTY]#################################################

//+++++###############################[SWAP]#################################################
#define generic_stack_swap(T) GLUE(generic_stack_swap_, T)

static void generic_stack_swap(GENERIC_STACK_TYPE) 
(generic_stack(GENERIC_STACK_TYPE) *self, generic_stack(GENERIC_STACK_TYPE) *other GS_LAST_PARAM)
{
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(self);
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_BEFORE(other);

    if (self == other) {
        return;
    }

    size_t size = self->size;
    size_t capacity = self->capacity;
    GENERIC_STACK_TYPE *ptr = self->ptr;
    #if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
    canary_t left_canary = self->left_canary;
    canary_t right_canary = self->right_canary;
    #endif
    #ifdef HASH_DATA
    hash_t hash_data = ((hash_t *)self->ptr)[-1];
    #endif

    self->size = other->size;
    self->capacity = other->capacity;
    self->ptr = other->ptr;
    #if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
    self->left_canary = other->left_canary;
    self->right_canary = other->right_canary;
    #endif
    #ifdef HASH_DATA
    ((hash_t *)self->ptr)[-1] = ((hash_t *)other->ptr)[-1];
    #endif

    other->size = size;
    other->capacity = capacity;
    other->ptr = ptr;
    #if defined(CANARY_FOR_STRUCT) && defined(CANARY_FS_USE_PTR)
    other->left_canary = left_canary;
    other->right_canary = right_canary;
    #endif
    #ifdef HASH_DATA
    ((hash_t *)other->ptr)[-1] = hash_data;
    #endif

    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(other);
    __GENERIC_STACK_AUTO_VALIDATE_VOIDF_AFTER(self);
}
//-----###############################[SWAP]#################################################

//+++++###############################[COMPARE]##############################################
#ifdef COMPARABLE
//typedef int (*comparator)(GENERIC_STACK_TYPE a, GENERIC_STACK_TYPE b); //commented by cause compiler worning

#define generic_stack_get_comparator(T) BACK_GLUE(T, _gs_comparator)

#define generic_stack_compare(T) GLUE(generic_stack_compare_, T)

#define GS_COMPARE_PARAMS \
    (const generic_stack(GENERIC_STACK_TYPE) *self, const generic_stack(GENERIC_STACK_TYPE) *other GS_LAST_PARAM)

#ifdef GS_WITH_ERROR_VALIDATE
#define GS_CMP_CALL_PARAM (self, other, gs_error)
#else
#define GS_CMP_CALL_PARAM (self, other)
#endif

static int generic_stack_compare(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{
    __GENERIC_STACK_AUTO_VALIDATE_BEFORE(self, int);
    __GENERIC_STACK_AUTO_VALIDATE_BEFORE(other, int);
    
    if (self == other) {
        return 0;
    }

    size_t to = (self->size <= other->size) ? self->size : other->size;
    for (size_t i = 0; i < to; i++) {
        int x = generic_stack_get_comparator(GENERIC_STACK_TYPE)(self->ptr[i], other->ptr[i]);
        if (!x) return x;
    }

    if (self->size == other->size) {
        return 0;
    } else
    if (self->size < other->size) {
        return 1;
    } else {
        return -1;
    }

}

#define generic_stack_equal(T) GLUE(generic_stack_equal_, T)
static bool generic_stack_equal(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{ return generic_stack_compare(GENERIC_STACK_TYPE) GS_CMP_CALL_PARAM == 0; }


#define generic_stack_not_equal(T) GLUE(generic_stack_not_equal_, T)
static bool generic_stack_not_equal(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{return generic_stack_compare(GENERIC_STACK_TYPE)GS_CMP_CALL_PARAM != 0;}


#define generic_stack_less(T) GLUE(generic_stack_less_, T)
static bool generic_stack_less(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{return generic_stack_compare(GENERIC_STACK_TYPE) GS_CMP_CALL_PARAM < 0;}


#define generic_stack_less_eq(T) GLUE(generic_stack_less_eq_, T)
static bool generic_stack_less_eq(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{return generic_stack_compare(GENERIC_STACK_TYPE) GS_CMP_CALL_PARAM <= 0;}


#define generic_stack_more(T) GLUE(generic_stack_more_, T)
static bool  generic_stack_more(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{return generic_stack_compare(GENERIC_STACK_TYPE) GS_CMP_CALL_PARAM > 0;}


#define generic_stack_more_eq(T) GLUE(generic_stack_more_eq_, T)
static bool  generic_stack_more_eq(GENERIC_STACK_TYPE) GS_COMPARE_PARAMS
{return generic_stack_compare(GENERIC_STACK_TYPE) GS_CMP_CALL_PARAM >= 0;}

#endif
//-----###############################[COMPARE]##############################################

//+++++################################[UNDEFS]#############################################
#undef GS_COMPARE_PARAMS
#undef GS_CMP_CALL_PARAM

#ifdef CANARY_FOR_STRUCT
#undef LEFT_CANARY  
#undef RIGHT_CANARY
#endif

#ifdef CANARY_FD_USE_PTR
#undef __gs_get_left_data_canary
#undef __gs_get_right_data_canary
#endif
//-----################################[UNDEFS]#############################################

#endif

