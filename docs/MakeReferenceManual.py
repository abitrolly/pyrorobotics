import os, string

prefix = "docs/wiki"
fp = open("docs/reference.txt", "r")
line = fp.readline().strip()
while line:
    print line, "..."
    newLine = string.replace(line, ".", "_2e")
    os.system("python wikidoc.py %s > %s/%s" % (line, prefix, newLine))
    line = fp.readline().strip()
