import sys
import json
import re

split_line = re.compile('\s+|,|\.|=|"|\'')
word_set = set()
file_output = sys.argv[2]
with open(sys.argv[1], 'r') as f:
	for line in f.readlines():
		words = split_line.split(line.lower()[:-1])
		for word in words:
			if len(word) != 0 and  not word in word_set:
				word_set.add(word)
		print(len(word_set))

word_out = []
for word in word_set:
	word_out += [word]

with open(file_output, 'w') as f:
	json.dump(word_out, f)	
#print(word_set)
