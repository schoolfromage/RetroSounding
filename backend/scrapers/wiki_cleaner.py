import re
from sys import argv

#Steven A
#THE "CORRECT" REGEX:
#([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"
#id ,"name",release_year,[developers],[publishers],"image",[src],[genres],[consoles],"description"

#please do not use this to overwrite the original csv before checking to make sure your changes are what you wanted

input = argv[1]
output = argv[2]
FileInput = open(input, 'r', encoding = "utf_16");
if not FileInput:
	print("error file not read")
outputLines = []
List = FileInput.readlines()
outputLines.append(List[0])
for line in List[1:]:
	match = re.match(r'([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"',line)
	if match:
		year = match.group(3)
		if year != 'n/a':
			outputLines.append(match.group(1)+','+'"'+match.group(2)+'"'+','+match.group(3)+','+'['+match.group(4)+']'+','+'['+match.group(5)+']'+','+'"'+match.group(6)+'"'+','+'['+match.group(7)+']'+','+'['+match.group(8)+']'+','+'['+match.group(9)+']'+','+'"'+match.group(10)+'"'+'\n')
	else:
		print("Error in match\n",line)
		break;
FileOutput = open(output, 'w', encoding = "utf_16");
FileOutput.writelines(outputLines)