import argparse
import io
import os
import pathlib
import sys

WIN_SEP = "\\"
EPOCH_AS_FILETIME = 11644473600  # seconds between windows and unix epoch
EPOCH_DELTA = EPOCH_AS_FILETIME * 1000 * 1000 * 10  # sec -> millisec -> microsec -> 100ns


def print_file(full_file, output, root, prefix, attrib):
    stat = os.stat(full_file)
    size = stat.st_size
    win_ctime = EPOCH_DELTA + int(stat.st_ctime_ns / 100)
    win_mtime = EPOCH_DELTA + int(stat.st_mtime_ns / 100)
    path = mkpath(full_file, root, prefix)
    output.write(f"\"{path}\",{size},{win_mtime},{win_ctime},{attrib}\n")


def mkpath(full_file, root, prefix):
    relpath = os.path.relpath(full_file, root)
    if prefix:
        return prefix + relpath
    else:
        return relpath


def walk_tree(path: pathlib.Path, output: io.TextIOWrapper, prefix: str):
    for (dirpath, dirnames, filenames) in os.walk(path):
        print_file(dirpath, output, path, prefix, 16)
        for file in filenames:
            full_file = path.joinpath(dirpath, file)
            print_file(full_file, output, path, prefix, 128)


def main():
    parser = argparse.ArgumentParser(description='Generate an Everything .efu file')
    parser.add_argument('--root', metavar='root', type=pathlib.Path, default='.',
                        help='the root directory to index. default = .')
    parser.add_argument('--output', metavar='output', type=argparse.FileType('w', encoding='UTF-8'),
                        help='output file. output goes to stdout if not specified.')
    parser.add_argument('--absolute', metavar='prefix', type=str, default=None,
                        help='use absolute paths, mapping the root here.')
    args = parser.parse_args()

    output = args.output if args.output else sys.stdout

    if args.absolute and not (args.absolute.endswith("\\") or args.absolute.endswith("/")):
        prefix = args.absolute + "\\"
    else:
        prefix = args.absolute

    output.write("Filename,Size,Date Modified,Date Created,Attributes\n")
    walk_tree(args.root, output, prefix)


if __name__ == '__main__':
    main()
