# Copyright (C) 2018, Vladimir Shapranov 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.


find_package(Boost REQUIRED
    COMPONENTS
        python3
)
find_package(PythonLibs 3 REQUIRED)

add_library(pythondecoderplugin 
    MODULE pydecoderplugin.cpp)

target_include_directories(pythondecoderplugin 
    PUBLIC 
    ${Boost_INCLUDE_DIRS} 
    ${PYTHON_INCLUDE_DIR}
)
target_link_libraries(pythondecoderplugin 
    qdlt 
    Qt5::Widgets 
    ${Boost_LIBRARIES} 
    ${PYTHON_LIBRARY}
)
install(TARGETS pythondecoderplugin DESTINATION deploy/plugins)
