#! python3.7
import sys
import re
from collections import Counter

sys.stdout.write("hello from Python %s\n" % (sys.version))
input("Press Enter to continue...")

composerStats = Counter()

with open('./scorelib.txt', 'r', encoding="utf-8") as file:
  for line in file:
    composerLine = re.match( r'^Composer: (.*)', line)
    if composerLine:
      names = re.split("; ?", composerLine.group(1))
      for name in names:
        name = re.sub(r'[(].*[)]', '', name).strip()
        if name:
          composerStats[name] += 1 
          print("name: ", name.encode(sys.stdout.encoding, errors='replace'))

for k, v in composerStats.items():
  print("{0}: {1}".format(k.encode(sys.stdout.encoding, errors='replace'), v))