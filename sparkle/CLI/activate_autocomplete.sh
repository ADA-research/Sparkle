# man page for "complete": https://manpages.ubuntu.com/manpages/noble/en/man7/bash-builtins.7.html
#/usr/bin/env bash
_sparkle_target() {
    local cur prev opts
    # Retrieving the current typed argument
    cur="${COMP_WORDS[COMP_CWORD]}"
    # Retrieving the previous typed argument ("-m" for example)
    prev="${COMP_WORDS[COMP_CWORD - 1]}"

    # Preparing an array to store available list for completions
    # COMREPLY will be checked to suggest the list
    COMPREPLY=()

    # Here, we only handle the case of "-m"
    # we want to leave the autocomplete of the standard usage to the default,
    # so COMREPLY stays an empty array and we fallback through "-o default"
    if [[ "$prev" != "sparkle" ]]; then
        return 0
    fi

    # Package path is the path of this file's dir
    PACKAGE_PATH=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

    # Otherwise, first we retrieve all paths of folder and .py files inside the <your_package> package,
    # we keep only the package related section, remove the .py extension and convert their separators into dots
    opts=$(find $PACKAGE_PATH -maxdepth 1 -name "[a-zA-Z]*.py" | sed "s|$PACKAGE_PATH/||" | sed "s|\.py||")

    # Then we store the whole list by invoking "compgen" and filling COMREPLY with its output content.
    # To mimick standard bash autocompletions we truncate autocomplete to the next folder (identified by dots)
    COMPREPLY=($(compgen -W "$opts" -- "$cur"))
}

# nospace disables printing of a space at the end of autocomplete,
# it allows to chain the autocomplete but:
# - removes the indication on end of chain that only one match was found.
# - removes the addition of the trailing / for standard python completion on folders
# -o default makes sure that default behaviour of bash is used when our script returns 0
complete -F _sparkle_target -o default sparkle
