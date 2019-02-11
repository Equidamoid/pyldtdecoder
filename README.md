### Writing dlt-viewer plugins in python

#### Installation:
 - Dependencies: in addition to dependencies of dlt-viewer you'll need python-dev and boost::python.
 - Clone this repository to the "plugin" directory of dlt-viewer sources: `(cd plugin; git clone ...)`
 - Add `add_subdirectory(dltviewerplugin)` to `plugin/CMakeLists.txt`: `echo "add_subdirectory(dltviewerplugin)" > plugin/CMakeLists.txt`
 - Build dlt-viewer: `mkdir build; cd build; cmake .. -DCMAKE_INSTALL_PREFIX=$(cd ..; pwd)/prefix; make -j6 install`

#### Usage: 
 - Write your plugin (`pydltdecoder.py` has some examples) 
