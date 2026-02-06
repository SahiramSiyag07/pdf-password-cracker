import itertools
import string

with open('large_wordlist.txt', 'w') as f:
    for p in itertools.product(string.ascii_lowercase, repeat=5):
        f.write(''.join(p) + '\n')
