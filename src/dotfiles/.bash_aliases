# User specific aliases and functions

alias ls='ls --color=auto --group-directories-first -F'
alias ll='ls -Alh'
alias la='ls -A'

alias cdtemp='cd $(mktemp -d) && pwd'

# User specific environment and startup programs

if [ -d "${HOME}/.bashrc.d" ]; then
    for _rcfile in "${HOME}/.bashrc.d/*"; do
        . "${_rcfile}"
    done
fi
