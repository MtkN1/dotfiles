# User specific aliases and functions

alias ls='ls --color=auto --group-directories-first -F'
alias ll='ls -Alh'
alias la='ls -A'

cdtemp() {
    local dir
    if dir=$(mktemp -d); then
        cd "$dir"
        pwd
    else
        return "$?"
    fi
}

cdvtemp() {
    local dir
    if dir=$(mktemp -d -p /var/tmp); then
        cd "$dir"
        pwd
    else
        return "$?"
    fi
}

# User specific environment and startup programs

if [ -d "${HOME}/.bashrc.d" ]; then
    for _rcfile in ${HOME}/.bashrc.d/*; do
        . "${_rcfile}"
    done
fi
