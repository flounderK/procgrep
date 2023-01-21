# procgrep

```
A linux utility for searching process memory
usage: procgrep.py [-h] [-x HEXDUMP_FILE] [-b BINARY_FILE] [-p HEX_PATTERN]
                   [-s STRING_PATTERN] [-dr] [-px] [-a]
                   [-pxc PRINT_HEX_CONTEXT_SIZE] [--debug]
                   pid

A linux utility for finding the locations of byte patterns in a process'
memory. Must be run as root

positional arguments:
  pid                   process to search

optional arguments:
  -h, --help            show this help message and exit
  -x HEXDUMP_FILE, --hexdump-file HEXDUMP_FILE
                        path to a hexdump file
  -b BINARY_FILE, --binary-file BINARY_FILE
                        path to a binary file
  -p HEX_PATTERN, --hex-pattern HEX_PATTERN
                        pattern in hex. E.g. '00 11 22 33'
  -s STRING_PATTERN, --string-pattern STRING_PATTERN
                        pattern in a string. E.g. 'this string'
  -dr, --dump-region    dump the region's contents to a file
  -px, --print-hex      print the bytes near where a match was found
  -a, --all-matches     Find all matches, not just the first one
  -pxc PRINT_HEX_CONTEXT_SIZE, --print-hex-context-size PRINT_HEX_CONTEXT_SIZE
                        number of bytes before and after a match to print
  --debug               enable debug mode
```


## Examples
```
# ./procgrep.py 226257 -p '6469 3d30 303b 3336 3a2a 2e6d 6b61 3d30' -a -px
7ffc9692bf20: 3b33 363a 2a2e 6d34 613d 3030 3b33 363a ;36:*.m4a=00;36:
7ffc9692bf30: 2a2e 6d69 643d 3030 3b33 363a 2a2e 6d69 *.mid=00;36:*.mi
7ffc9692bf40: 6469 3d30 303b 3336 3a2a 2e6d 6b61 3d30 di=00;36:*.mka=0
7ffc9692bf50: 303b 3336 3a2a 2e6d 7033 3d30 303b 3336 0;36:*.mp3=00;36
7ffc9692bf60: 3a2a 2e6d 7063 3d30 303b 3336 3a2a 2e6f :*.mpc=00;36:*.o

0x7ffc9692bf40 : 7ffc9690b000-7ffc9692c000 rw-p 00000000 00:00 0                          [stack]
```


```
# ./procgrep.py 226257 -s 'ENV' -a -px -pxc 32
7ffc9692bfa0: 7573 3d30 303b 3336 3a2a 2e73 7078 3d30 us=00;36:*.spx=0
7ffc9692bfb0: 303b 3336 3a2a 2e78 7370 663d 3030 3b33 0;36:*.xspf=00;3
7ffc9692bfc0: 363a 0050 5945 4e56 5f53 4845 4c4c 3d7a 6:.PYENV_SHELL=z
7ffc9692bfd0: 7368 0050 5945 4e56 5f56 4952 5455 414c sh.PYENV_VIRTUAL
7ffc9692bfe0: 454e 565f 494e 4954 3d31 002f 7573 722f ENV_INIT=1./usr/

7ffc9692bfb0: 303b 3336 3a2a 2e78 7370 663d 3030 3b33 0;36:*.xspf=00;3
7ffc9692bfc0: 363a 0050 5945 4e56 5f53 4845 4c4c 3d7a 6:.PYENV_SHELL=z
7ffc9692bfd0: 7368 0050 5945 4e56 5f56 4952 5455 414c sh.PYENV_VIRTUAL
7ffc9692bfe0: 454e 565f 494e 4954 3d31 002f 7573 722f ENV_INIT=1./usr/
7ffc9692bff0: 6269 6e2f 6361 7400 0000 0000 0000 00   bin/cat........

7ffc9692bfc0: 363a 0050 5945 4e56 5f53 4845 4c4c 3d7a 6:.PYENV_SHELL=z
7ffc9692bfd0: 7368 0050 5945 4e56 5f56 4952 5455 414c sh.PYENV_VIRTUAL
7ffc9692bfe0: 454e 565f 494e 4954 3d31 002f 7573 722f ENV_INIT=1./usr/
7ffc9692bff0: 6269 6e2f 6361 7400 0000 0000 0000 00   bin/cat........

0x7ffc9692bfc5 : 7ffc9690b000-7ffc9692c000 rw-p 00000000 00:00 0                          [stack]
0x7ffc9692bfd5 : 7ffc9690b000-7ffc9692c000 rw-p 00000000 00:00 0                          [stack]
0x7ffc9692bfe0 : 7ffc9690b000-7ffc9692c000 rw-p 00000000 00:00 0                          [stack]
```
