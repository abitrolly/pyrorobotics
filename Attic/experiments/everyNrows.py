# Gets every N rows of standard input
# cat file | python everyNrows.py 5

import sys

N = int(sys.argv[1])
line = sys.stdin.readline()
lineCount = 1
while line:
    if lineCount % N == 0:
        print line,
    line = sys.stdin.readline()
    lineCount += 1
