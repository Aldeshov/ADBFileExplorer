source ./venv/bin/activate
app=$(pwd)/src/app
src=$(pwd)/src
root=$(pwd)
path=$app:$src:$root
export PYTHONUNBUFFERED=1
export PYTHONPATH=$path:$PYTHONPATH
python ./src/app
