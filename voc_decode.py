import sys
import math
transition_prob = dict()
emission_prob= dict()

predictedList=[]
actualList= [] 

tagSet=set()



def readfile():
	model="hmmmodel.txt"
	f1 = open(model,"r")
	emission= False
	for line in f1:
		if line.startswith("Emission probabilities"):
			emission= True
		elif line.startswith("Transition probabilities"):
			emission= False
		else:
			#print(line.strip().replace(" ",""))
			text= line.strip().replace(" ","").rsplit(":",1)
			#print(text)
			prob= text[1]
			if not emission:
				states= text[0].split("|")
				trans_tup=(states[0],states[1])
				transition_prob[trans_tup]= float(prob)
				
			else:
				wordtag= text[0].split("|")
				word= wordtag[0]
				tag = wordtag[1]
				tagSet.add(tag)
				if word in emission_prob:
					emission_prob[word][tag]=float(prob)
				else:
					emission_prob[word]=dict()
					emission_prob[word][tag]=float(prob)

	f1.close()				
	#print(emission_prob)
	return 


def write(filename,predictedList):

	index=0
	f3= open(filename,"r")
	f4= open("hmmoutput.txt","w")
	for line in f3:
		words=line.strip().replace("\n","").split(" ")
		for i in range(len(words)):

			if i==len(words)-1:
				f4.write(words[i]+"/"+predictedList[index]+"\n")
			else:
				f4.write(words[i]+"/"+predictedList[index]+" ")

			index+=1



def viterbi(file):

	f2 = open(file,"r")
	global predictedList
	for line in f2:
		words=line.strip().replace("\n","").split(" ")
		backpointer = dict()
		v= dict()
		
		for i in range(len(words)):
			
			if words[i] not in emission_prob:
				emission_prob[words[i]]= dict()
				for tag in tagSet:
					emission_prob[words[i]][tag]=10e-15

			if i==0:

				for tag in emission_prob[words[i]]:
					
					if(tag,'start') in transition_prob:
						v[(i,tag)]= math.log(transition_prob[(tag,'start')],10) + math.log(emission_prob[words[i]][tag],10)

					else:
						v[(i,tag)]= 10e-15


					
					

			else:
				
				for tag in emission_prob[words[i]]:
					
					curprob= -float("inf")
					newprob= 0
				
					for prev_tag in emission_prob[words[i-1]]:

						if (prev_tag,tag) not in transition_prob:
							transition_prob[(prev_tag,tag)]= 10e-15
						
						if (i-1,prev_tag) in v and (prev_tag,tag) in transition_prob:
							
							newprob = v[(i-1,prev_tag)]+ math.log(transition_prob[(prev_tag, tag)],10)+ math.log(emission_prob[words[i]][tag],10)
							


						if newprob!=0 and newprob > curprob:
							
							curprob=newprob
							backpointer[(i,tag)]=prev_tag

						newprob=0

					v[(i,tag)]=curprob

					
		sz = len(words)-1
		maxValue= -float("inf")
		bestTag=""
		
		for  tag in emission_prob[words[sz]]:
			#print(tag)
			if (sz,tag) in v:
				if v[(sz,tag)]> maxValue:
					maxValue = v[(sz,tag)]
					bestTag= tag
		predictedTags= [bestTag]
		
		while sz>0:
			predictedTags.append(backpointer[(sz,bestTag)])
			bestTag= backpointer[(sz,bestTag)]
			#print(bestTag)
			sz-=1

		if predictedList!=[]:
			predictedList.extend((predictedTags[::-1]))

		else:
			predictedList=predictedTags[::-1]
			#print(predictedList)
	f2.close()
	write(file,predictedList)
		


		
if __name__=='__main__':
	readfile()
	viterbi(sys.argv[1])
	



