#include <stdio.h>
// #include "esp_attr.h"

// --- Padding Definitions ---

#if defined(RODATA_PADDING) && (RODATA_PADDING > 0)
__attribute__((section(".rodata")))
__attribute__((used))
const unsigned char qio_rodata_padding[RODATA_PADDING] = {
    [0 ... RODATA_PADDING-1] = 0x00
};
#endif

// Placing in IRAM to nudge code segments
#if defined(IRAM_PADDING) && (IRAM_PADDING > 0)
__attribute__((section(".iram1.text")))
__attribute__((used))
const unsigned char qio_code_padding[IRAM_PADDING] = {
    [0 ... IRAM_PADDING-1] = 0x90 // NOP
};
#endif

// 3. IROM Padding (Code in Flash) - THIS MOVES SEGMENT 5
#if defined(IROM_PADDING) && (IROM_PADDING > 0)
__attribute__((section(".flash.text")))
__attribute__((used))
const unsigned char qio_irom_padding[IROM_PADDING] = {
    [0 ... IROM_PADDING-1] = 0x90 // NOP
};
#endif

// RTC memory padding (affects RTC segment)
#if defined(RTC_PADDING) && (RTC_PADDING > 0)
__attribute__((section(".rtc.data")))
__attribute__((used))
const unsigned char qio_rtc_padding[RTC_PADDING] = {
    [0 ... RTC_PADDING-1] = 0x00
};
#endif

// --- Helper Function ---
// to be called in esp_app_main.c to ensure the paddings are linked
// otherwise linker flags must be set in CMakeLists.txt

/*
void qio_print_padding_info(void) {
    // RODATA Information
#if defined(RODATA_PADDING) && (RODATA_PADDING > 0)
    printf("QIO RODATA Padding: Addr: %p, Len: %zu\n", 
            (void*)qio_rodata_padding, sizeof(qio_rodata_padding));
#else
    // printf("QIO RODATA Padding: Disabled (Not set)\n");
#endif

    // IRAM Information
#if defined(IRAM_PADDING) && (IRAM_PADDING > 0)
    printf("QIO CODE   Padding: Addr: %p, Len: %zu\n", 
            (void*)qio_code_padding, sizeof(qio_code_padding));
#else
    // printf("QIO IRAM   Padding: Disabled (Not set)\n");
#endif

#if defined(IROM_PADDING) && (IROM_PADDING > 0)
    printf("QIO IROM   Padding: Addr: %p, Len: %zu\n", 
            (void*)qio_irom_padding, sizeof(qio_irom_padding));
#else
    // printf("QIO IROM   Padding: Disabled (Not set)\n");
#endif

    // RTC Information
#if defined(RTC_PADDING) && (RTC_PADDING > 0)
    printf("QIO RTC    Padding: Addr: %p, Len: %zu\n", 
            (void*)qio_rtc_padding, sizeof(qio_rtc_padding));
#else
    // printf("QIO RTC    Padding: Disabled (Not set)\n");
#endif
}
*/