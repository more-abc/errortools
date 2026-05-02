@echo off
echo Building C extension for errortools...
python setup.py build_ext --inplace
echo Done! C speedup module compiled.
