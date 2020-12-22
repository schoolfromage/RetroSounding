import re
from sys import argv

#Steven A
#THE "CORRECT" REGEX:
#([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"
#id ,"name",release_year,[developers],[publishers],"image",[src],[genres],[consoles],"description"

#this program merges entries based of GID

#please do not use this to overwrite the original csv before checking to make sure your changes are what you wanted

input1 = argv[1]
input2 = argv[2]
output = argv[3]
FileInput1 = open(input1, 'r', encoding = "utf_16");
FileInput2 = open(input2, 'r', encoding = "utf_16");

if not FileInput1:
	print("error file 1 not read")
if not FileInput2:
	print("error file 2 not read")

outputLines = []
List1 = FileInput1.readlines()
List2 = FileInput2.readlines()
outputLines.append(List1[0])
FileData = {}
for line in List2[1:]:
	match = re.match(r'([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"',line)
	FileData[match.group(1)]=match
	print(match.group(2))#print the name
print("")
for line in List1[1:]:
	match = re.match(r'([^,]*),"(.*)",([^,]*),\[(.*)\],\[(.*)\],"(.*)",\[(.*)\],\[(.*)\],\[(.*)\],"(.*)"',line)
	if match:
		GID=match.group(1)
		name=match.group(2)
		year = match.group(3)
		devs = match.group(4)
		pubs = match.group(5)
		img = match.group(6)
		src = match.group(7)
		genres=match.group(8).replace("'","")
		console=match.group(9)
		desc=match.group(10)
		print(name)
		print("is updated?",(GID in FileData))
		if GID in FileData:
			if img=="n/a":
				img = FileData[GID].group(6)#take the image from the other csv
			if FileData[GID].group(7)!="n/a":
				src += ","+FileData[GID].group(7)
				src.replace("n/a,","").replace("n/a","")
			if FileData[GID].group(8)!="n/a":
				if FileData[GID].group(8) not in genres:#the genres may not be unique, so check first
					genres+=","+FileData[GID].group(8)
					genres.replace("n/a,","").replace("n/a","")
			if desc =="n/a":
				desc = FileData[GID].group(10)
		outputLines.append(GID+','+'"'+name+'"'+','+year+','+'['+devs+']'+','+'['+pubs+']'+','+'"'+img+'"'+','+'['+src+']'+','+'['+genres+']'+','+'['+console+']'+','+'"'+desc+'"'+'\n')
	else:
		print("Error in match\n",line)
		break;
FileInput1.close()
FileInput2.close()
FileOutput = open(output, 'w', encoding = "utf_16");
FileOutput.writelines(outputLines)
