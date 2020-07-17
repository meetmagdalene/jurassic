cmake_minimum_required (VERSION 3.1)

project(Jurrasic
        VERSION 1.0
        LANGUAGES CXX
)
set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED True)

set(CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake)
set(SCRIPTS_DIR ${CMAKE_SOURCE_DIR}/scripts)

if (WIN32)
    set(CMAKE_MAKE_PROGRAM ninja)
else()
    set(CMAKE_MAKE_PROGRAM /usr/bin/ninja-1.8.2)
endif()

if (NOT TARGET_BUILD_TYPE)
    set(TARGET_BUILD_TYPE LOCAL)
endif()

add_custom_target(all-all)
add_subdirectory(product)