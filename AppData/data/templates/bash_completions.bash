#!/bin/bash

# It would have been impossible to create this without the following post on Stack Exchange!!!
# https://unix.stackexchange.com/a/55622

_have {executable_name} &&
_decide_nospace_{current_date}(){
    if [[ ${1} == "--"*"=" ]] ; then
        compopt -o nospace
    fi
} &&
__movies_db_app_{current_date}(){
    local cur prev cmd
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Completion of commands and "first level options.
    if [[ $COMP_CWORD == 1 ]]; then
        COMPREPLY=( $(compgen -W "movies server generate -h --help --version" -- "${cur}") )
        return 0
    fi

    # Completion of options and sub-commands.
    cmd="${COMP_WORDS[1]}"

    case $cmd in
    "movies")
        COMPREPLY=( $(compgen -W "scan base_data detailed_data --debug" -- "${cur}") )
        ;;
    "server")
        COMPREPLY=( $(compgen -W "start stop restart --host= --port=" -- "${cur}") )
        _decide_nospace_{current_date} ${COMPREPLY[0]}
        ;;
    "generate")
        COMPREPLY=( $(compgen -W "system_executable" -- "${cur}") )
        ;;
    esac
} &&
complete -F __movies_db_app_{current_date} {executable_name}
