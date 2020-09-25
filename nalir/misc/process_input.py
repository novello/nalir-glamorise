import sys

file = sys.argv[1]
new_file = sys.argv[2]
lines = []
all_lines = []

with open(file, 'r') as f:
	all_lines = f.readlines()
	print(len(all_lines))
	idx = 0 
	i = 0
	
	while idx < len(all_lines):
		i = len(lines)
		#print(all_lines[idx])
		lines += [all_lines[idx].split('\n')[0]]
		count_fields = len(lines[i].split('|'))
		
		while count_fields != 5:
			idx += 1
			lines[i] +=  ' ' + all_lines[idx].split('\n')[0]
 			count_fields = len(lines[i].split('|'))

		#i+=1
		idx+=1

with open(new_file, 'w') as f:
	for line in lines:
		f.write(line + '\n')
