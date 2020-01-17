#! /usr/bin/env python

import string
import re
import sys



file_header=open("HEADER","r")
file_predicates=open("PREDICATES","r")
header=[]
predicates=[]
while 1:
	in_line = file_header.readline()
	if in_line == "":
		break
	header.append(in_line)
file_header.close()

while 1:
	in_line = file_predicates.readline()
	if in_line == "":
		break
	if in_line.find("(") != -1:
		predicates.append(in_line)
file_predicates.close()

# read the number of operators, and start read corresponding files.
number_op = int(sys.argv[1])

name_operators=[]
parameters=[]
preconditions=[[] for x in xrange(number_op)]
effects=[[] for x in xrange(number_op)]

start=1
while start <= number_op:	
	file_operator=open("OP"+str(start),"r")
	in_line=file_operator.readline()
	name_operators.append(in_line)
	in_line=file_operator.readline()
	parameters.append(in_line)
	## added parameters and name of the operator. Now processing precond
	in_line=file_operator.readline()
	in_line=file_operator.readline()
	while 1:
		if in_line.startswith(":eff") == True:
			break
		preconditions[start-1].append(in_line)
		in_line=file_operator.readline()
	#preconditions.append(precond)
	## now processing effects
	while 1:
		in_line = file_operator.readline()
		if in_line == "":
			break
		if in_line.find("(") != -1:
			effects[start-1].append(in_line)	
	file_operator.close()
	start=start+1

## hey, we have everything. Now print out according to given parameters.

## first, predicates.

for i in header:
	print i

number_predicates=len(predicates)
stamp_pred=[]
number=1
while number < number_predicates+1:
	indice=1
	check="-prex"+str(number)
	while indice < len(sys.argv):
		if sys.argv[indice].find(check) != -1:
			stamp_pred.append(float(sys.argv[indice+1]))
			break
		indice=indice+1
	number=number+1

print "\n(:predicates"
for i in predicates:
	position=stamp_pred.index(min(stamp_pred))
	print predicates[position],
	stamp_pred[position]=10000.0
print ")"


## time for operators and their eff/ precond.
stamp_op=[]
stamp_prec=[]
stamp_eff=[]
to_stamp_op=[]
i=0
while i < len(name_operators):
	check="-op"+str(i+1)	
	indice=1
	while indice < len(sys.argv):
		if sys.argv[indice].find(check) != -1:
			stamp_op.append(float(sys.argv[indice+1]))
			break
		indice=indice+1
	stamp_prec=[]
	number=1
	while number <= len(preconditions[i]):
		check="-pred"+str(i+1)+str(number)
		indice=1
		while indice < len(sys.argv):
			if sys.argv[indice].find(check) != -1:
				stamp_prec.append(float(sys.argv[indice+1]))
				break
			indice=indice+1
		number=number+1
	stamp_eff=[]
	number=1
	while number <= len(effects[i]):
		check="-eff"+str(i+1)+str(number)
		indice=1
		while indice < len(sys.argv):
			if sys.argv[indice].find(check) != -1:
				stamp_eff.append(float(sys.argv[indice+1]))
				break
			indice=indice+1
		number=number+1
	real_op=name_operators[i]+parameters[i]+":precondition (and\n"
	for h in preconditions[i]:
		position=stamp_prec.index(min(stamp_prec))
		#real_op=real_op.join(preconditions[i][position])
		elemento=""
		elemento=preconditions[i][position]
		real_op=real_op+elemento
		stamp_prec[position]=10000.0
	real_op=real_op+")\n:effect (and\n"
	for h in effects[i]:
		position=stamp_eff.index(min(stamp_eff))
		#real_op=real_op.join(effects[i][position])
		elemento=""
		elemento=effects[i][position]
		real_op=real_op+elemento
		stamp_eff[position]=10000.0
	real_op=real_op+"))"
	to_stamp_op.append(real_op)
	i=i+1

for i in name_operators:
	position=stamp_op.index(min(stamp_op))
	print to_stamp_op[position]
	stamp_op[position]=10000.0
print ")"

