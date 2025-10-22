#!/bin/bash -eux

pathmunge () {
    # If the path is a compat symlink, do nothing.
    [ -h "$1" ] && return

    case ":${PATH}:" in
        *:"$1":*)
            ;;
        *)
            if [ "${2-}" = "after" ] ; then
                PATH=$PATH:$1
            else
                PATH=$1:$PATH
            fi
    esac
}

pathmunge ~/.cargo/bin
pathmunge ~/.local/bin

unset -f pathmunge

"$(dirname "${0}")/apt.sh"
"$(dirname "${0}")/binary.sh"
"$(dirname "${0}")/uv_tool.sh"
# "$(dirname "${0}")/source.sh"
"$(dirname "${0}")/image.sh"
