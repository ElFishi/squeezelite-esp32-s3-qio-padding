# qio_padding.cmake
#   use in CMakeLists.txt with 
#   include(qio_padding.cmake)

# 1. Define Padding Macros
if(DEFINED RODATA_PADDING)
    add_definitions(-DRODATA_PADDING=${RODATA_PADDING})
endif()

if(DEFINED IRAM_PADDING)
    add_definitions(-DIRAM_PADDING=${IRAM_PADDING})
endif()

if(DEFINED IROM_PADDING)
    add_definitions(-DIROM_PADDING=${IROM_PADDING})
endif()

if(DEFINED RTC_PADDING)
    add_definitions(-DRTC_PADDING=${RTC_PADDING})
endif()

# 2. Build Linker Flags (Forces compiler to not strip the padding symbols)
set(PADDING_LINK_FLAGS "")
if(DEFINED RODATA_PADDING AND RODATA_PADDING GREATER 0)
    list(APPEND PADDING_LINK_FLAGS "-Wl,--undefined=qio_rodata_padding")
endif()
if(DEFINED IRAM_PADDING AND IRAM_PADDING GREATER 0)
    list(APPEND PADDING_LINK_FLAGS "-Wl,--undefined=qio_code_padding")
endif()
if(DEFINED IROM_PADDING AND IROM_PADDING GREATER 0)
    list(APPEND PADDING_LINK_FLAGS "-Wl,--undefined=qio_irom_padding")
endif()
if(DEFINED RTC_PADDING AND RTC_PADDING GREATER 0)
    list(APPEND PADDING_LINK_FLAGS "-Wl,--undefined=qio_rtc_padding")
endif()

