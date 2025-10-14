#!/bin/bash
echo Testing script execution...
source /opt/mayan-edms/bin/activate
echo Virtual environment activated
python3 -c import django
echo Django imported successfully
python3 manage.py migrate converter_pipeline_extension
echo Extension enable command executed
echo Script completed!
