#!/usr/bin/env python3
import re
import argparse
import logging
import subprocess
import string
import os


description = """
A linux utility for finding the locations of byte patterns in a process'
memory. Must be run as root
"""

log = logging.getLogger("procgrep")
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(levelname)-7s | %(asctime)-23s | %(message)s'))
log.addHandler(handler)
log.setLevel(logging.WARNING)

PROC_PID_MAPS_REXP = re.compile(r'([a-f0-9]+)-([a-f0-9]+)\s+([rwxps-]{4})')


def bnot(n, numbits=64):
    return (1 << numbits)-1-n


def align(val, align_to, numbits=64):
    return val & bnot(align_to - 1, numbits)


def align_up(val, align_to, numbits=64):
    aligned = align(val, align_to, numbits)
    if aligned < val:
        aligned += align_to
    return aligned


def batch(it, sz):
    length = len(it)
    for i in range(0, length, sz):
        yield it[i:i+sz]


def printhex(bytevals, start=0, bytegroupsize=2):
    row_incr = 16
    printable = string.printable[:-5].encode()
    unprintable_char = ord('.')

    fmt = "%%0%dx: " % (len(hex(len(bytevals))) - 2)
    for ind, rowbytes in enumerate(batch(bytevals, row_incr)):
        line = fmt % (start + row_incr*ind)
        bytes_section = " ".join([i.hex() for i in batch(rowbytes, bytegroupsize)])
        bytes_section_size = (((2*bytegroupsize)+1)*(row_incr // bytegroupsize))-1
        line += bytes_section.ljust(bytes_section_size, ' ')
        textrepr = bytes([i if i in printable else unprintable_char for i in rowbytes]).decode()
        line += " " + textrepr
        print(line)


def find_in_pid(pid, pattern, dump_region=False, all_matches=False,
                print_hex=False, print_hex_context_size=32):
    with open(f"/proc/{pid}/maps", "r") as f:
        maps = f.read().splitlines()

    pattern_length = len(pattern)
    pattern_rexp = re.compile(re.escape(pattern),
                              re.MULTILINE | re.DOTALL)
    memfd = open(f"/proc/{pid}/mem", "rb")
    match_info = []

    for line in maps:
        m = re.search(PROC_PID_MAPS_REXP, line)
        startstr, endstr, permstr = m.groups()
        if not permstr.startswith("r"):
            continue
        region_start = int(startstr, 16)
        region_end = int(endstr, 16)
        memfd.seek(region_start)
        do_region_dump = False
        log.debug("searching '%s'" % line)
        try:
            search_mem = memfd.read(region_end - region_start)
        except OSError:
            log.debug("Got an OSError, likely just the 'vvar' region")
            continue
        for pattern_match in re.finditer(pattern_rexp, search_mem):
            offset = pattern_match.start()
            match_address = region_start + offset
            match_info.append((match_address, line))
            if dump_region is True:
                do_region_dump = True

            if print_hex is True:
                maybe_low_offset = align(offset - print_hex_context_size, 16)
                low = maybe_low_offset if maybe_low_offset >= 0 else 0
                maybe_high_offset = align_up(offset + pattern_length + print_hex_context_size, 16)
                high = maybe_high_offset if maybe_high_offset < len(search_mem) else -1
                printhex(search_mem[low:high], region_start+low)
                print()

            if all_matches is False:
                break
        # only dump region one time per match
        if do_region_dump is True:
            dump_filename = f"{pid}.{startstr}-{endstr}.dump"
            with open(dump_filename, "wb") as f:
                f.write(search_mem)

    memfd.close()
    return match_info


def cli():
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("pid", type=int, help="process to search")
    parser.add_argument("-x", "--hexdump-file",
                        help="path to a hexdump file")
    parser.add_argument("-b", "--binary-file",
                        help="path to a binary file")
    parser.add_argument("-p", "--hex-pattern",
                        help="pattern in hex. E.g. '00 11 22 33'")
    parser.add_argument("-s", "--string-pattern",
                        help="pattern in a string. E.g. 'this string'")
    parser.add_argument("-dr", "--dump-region", action="store_true",
                        default=False,
                        help="dump the region's contents to a file")
    parser.add_argument("-px", "--print-hex", action="store_true",
                        default=False,
                        help="print the bytes near where a match was found")
    parser.add_argument("-a", "--all-matches", action="store_true",
                        default=False,
                        help="Find all matches, not just the first one")
    parser.add_argument("-pxc", "--print-hex-context-size", type=int,
                        default=32,
                        help="number of bytes before and after a match to print")
    parser.add_argument("--debug", action="store_true",
                        default=False,
                        help="enable debug mode")
    args = parser.parse_args()

    if args.debug:
        log.setLevel(logging.DEBUG)

    pattern = None
    if args.hexdump_file:
        p = subprocess.Popen(f"xxd -r {args.hexdump_file}",
                             shell=True, stdout=subprocess.PIPE)
        pattern = p.stdout.read()
        p.terminate()
    elif args.binary_file:
        with open(args.binary_file, "rb") as f:
            pattern = f.read()
    elif args.hex_pattern:
        pattern = bytes.fromhex(args.hex_pattern)
    elif args.string_pattern:
        pattern = args.string_pattern.encode()
    else:
        raise Exception("Must specify a pattern")

    matches = find_in_pid(args.pid, pattern,
                          args.dump_region,
                          args.all_matches,
                          args.print_hex,
                          args.print_hex_context_size)

    for m in matches:
        print("%#x : %s" % (m))


if __name__ == "__main__":
    cli()
