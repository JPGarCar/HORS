import math
import sys


totalnum = int(sys.argv[1])


firstnum = int(totalnum % 10)
secondnum = int(totalnum / 10)

genfirst = math.ceil((firstnum + 10) * 3)
gensecond = math.ceil((secondnum + 10) * 3)


print(str(gensecond) + "IMDB" + str(genfirst) + "XM")