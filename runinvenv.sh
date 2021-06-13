#!/bin/bash
export ARVADOS_API_HOST=cborg.cbrc.kaust.edu.sa
export ARVADOS_API_TOKEN=3ryr1r7cf7jrr1o79mn9h0oh7w0p5kfdmm5mqnd7v09w0jve4a

VENV=$1
if [ -z $VENV ]; then
    echo "usage: runinenv [virtualenv_path] CMDS"
    exit 1
fi
. ${VENV}/bin/activate
shift 1
echo "Executing $@ in ${VENV}"
exec "$@"
deactivate
