cmake_minimum_required (VERSION 3.1)

project(Jurrasic
        VERSION 1.0.0.0
        LANGUAGES C CXX
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

set(MY_CACHE_VARIABLE TRUE CACHE BOOL "Testing out a cache bool var in CMake" FORCE)
set(MY_CACHE_VARIABLE2 "VALUE" CACHE STRING "Testing out a string cache var in CMake")

# Configure the Version of the Project Jurassic
configure_file(
    "${PROJECT_SOURCE_DIR}/include/version.h.in"
    "${PROJECT_SOURCE_DIR}/include/version.h"
)

add_custom_target(all-all)
add_subdirectory(product)
