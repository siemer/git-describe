#!/usr/bin/python3
# coding: utf-8

# git describe --exact-match 
# git name-rev  # command not so flexible...
# git rev-parse  # name → sha1 or HEAD → branch name
# git symbolic-ref  # reads HEAD, but not tags

# add the visible value

import sys

from enum import Enum
from itertools import zip_longest
from subprocess import check_output

RepoState = Enum('RepoState', 'conflict recorded different missing')

SHA1_LENGTH = 9

class BitArray(list):
    def append(self, value):
        list.append(self, bool(value))

    def append_hex(self, string):
        self._append(string, 4, lambda x: int(x, 16))

    def append_base64(self, string):
        self._append(string, 6, lambda x: self._b64_map.index(x))

    _b64_map = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
              'abcdefghijklmnopqrstuvwxyz' \
              '01234567890' '#%'
              # # % + =

    def _append(self, string, nr_of_bits, char_to_int):
        for char in string:
            count = 0
            for bit in '{:0{}b}'.format(char_to_int(char), nr_of_bits):
                count += 1
                self.append(True if bit == '1' else False)
            assert count == nr_of_bits

    def _chunks(self, nr_of_bits):
        demux = []
        for nr in range(nr_of_bits):
            demux.append(self[nr::nr_of_bits])
        for chunk in zip_longest(*demux, fillvalue=False):
            chunk = map(str, map(int, chunk))
            chunk = int(''.join(chunk), 2)
            yield chunk

    def _to_str(self, nr_of_bits, int_to_char):
        accu = ''
        for chunk in self._chunks(nr_of_bits):
            accu += int_to_char(chunk)
        return accu

    def base64(self):
        return self._to_str(6, lambda x: self._b64_map[x])

    def hex(self):
        return self._to_str(4, lambda x: '{:x}'.format(x))

def submodules():
    '''iterates over submodules in order, returning tuples of state, sha1 and path)'''
    for line in check_output(['git', 'submodule']).splitlines():
        line = line.split()
        sha1 = line[0].decode('ascii')
        path = line[1]
        if len(sha1) == 41:
            state, sha1 = sha1[0], sha1[1:]
            if state == '+':
                state = RepoState.different
            elif state == '-':
                state = RepoState.missing
            elif state == 'U':
                state = RepoState.conflict
            else:
                raise SystemError()
        elif len(sha1) == 40:
            state = RepoState.recorded
        else:
            raise SystemError()
        yield state, sha1, path

def description_bits():
    submodule_names = []
    bits = BitArray()
    for state, sha1, path in submodules():
        submodule_names.append(path)
        assert state not in (RepoState.missing, RepoState.conflict)
        if state == RepoState.recorded:
            bits.append(False)
        elif state == RepoState.different:
            bits.append(True)  # sha1 follows later
            bits.append(False)  # no extension(s)
            bits.append_hex(sha1[:SHA1_LENGTH])
    assert submodule_names == sorted(submodule_names)
    return bits

def parse_base64(value):
    b = BitArray()
    b.append_base64(value)
    for state, sha1, path in submodules():
        path = path.decode('ascii')
        if b.pop(0):
            assert not b.pop(0)  # I can’t handle extensions
            print('{}: {}'.format(path, b.hex()[:SHA1_LENGTH]))
            del b[:SHA1_LENGTH * 4]
        else:
            print('{}: no changes'.format(path))
    assert not any(b)
    print('{} leftover bits'.format(len(b)))

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        parse_base64(sys.argv[1])
    else:
        print(description_bits().base64())