import sys
import math
import pickle
transition_prob = dict()
emission_prob= dict()

predictedList=[]
actualList= [] 
tagcounter= dict()
tagSet=set()
vocabsize=0

nlines=0

def calculate_accuracy(file):
	f3 = open(file,"r")
	for line in f3:
		tagList=[]
		#print(line)
		line=line.strip()
		line=line.split(" ")
		for j in line:
			#print(j,end="")
			word,tag= j.rsplit("/",1)
			actualList.append(tag)

	#print(len(actualList))
	#print(len(predictedList))
	pos=0.0
	for x,y in zip(actualList, predictedList):
		if x==y:
			pos+=1
	print(pos/len(actualList))
	f3.close()


	

def readfile():
	model="model.pickle"
	f1 = open(model,"rb")

	global emission_prob,transition_prob,tagcounter,vocabsize, tagSet,nlines
	transition_prob = pickle.load(f1)
	emission_prob= pickle.load(f1)
	tagcounter = pickle.load(f1)
	vocabsize = pickle.load(f1)
	nlines = pickle.load(f1)
	#print(transition_prob)
	#print(emission_prob)
	#print(tagcounter)
	#print(vocabsize)

	for tag in tagcounter:
		tagSet.add(tag)
	'''
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
	'''

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
	global emission_prob,transition_prob,tagcounter,vocabsize,predictedList,tagSet,nlines
	#print(tagSet)
	#print(emission_prob)
	totalTags=0

	for tag in tagcounter:
		totalTags+= tagcounter[tag]
	#print(totalTags)

	for line in f2:
		#print(line)
		words=line.strip().replace("\n","").split(" ")
		#print(words)
		backpointer = dict()
		v= dict()
		#print(words)
		for i in range(len(words)):
			
			transition_prob_value =0.0
			emission_prob_value= 0.0
			unknown = False
			if words[i] not in emission_prob:
				unknown=True
				emission_prob[words[i]]= dict()

				
				for tag in tagSet:
					emission_prob_value = tagcounter[tag]
					emission_prob[words[i]][tag]= emission_prob_value
					#added
					transition_prob[(tag,'start')]=0
				#print(emission_prob[words[i]])

			if i==0:

				for tag in emission_prob[words[i]]:
					#print(words[i])
					#print(tag)
					#print(transition_prob[(tag,'start')])
					#v[(i,tag)]=0
					#print("Current tag: ",tag)


					if(tag,'start') in transition_prob:
						transition_prob_value= float((transition_prob[(tag,'start')]+1)/ (totalTags))
						#transition_prob_value= float((transition_prob[(tag,'start')]+1)/ (tagcounter[tag]+nlines))

						#print(transition_prob_value)
						if unknown:
							emission_prob_value = float(emission_prob[words[i]][tag]/totalTags)
						else:
							emission_prob_value= float(emission_prob[words[i]][tag]/tagcounter[tag])
						v[(i,tag)]= math.log(transition_prob_value,10) + math.log(emission_prob_value,10)

					else:
						transition_prob_value= float(1/(totalTags))
						v[(i,tag)]=  math.log(transition_prob_value,10)


					
					

			else:

				
				
				for tag in emission_prob[words[i]]:
					#print(tag)
					#v[(i,tag)]=0
					curprob= -float("inf")
					newprob= 0
					#backpointer[(i,tag)]=""

					for prev_tag in emission_prob[words[i-1]]:

						

						if (prev_tag,tag) not in transition_prob:
							transition_prob[(prev_tag,tag)]= 0
						
						if (i-1,prev_tag) in v and (prev_tag,tag) in transition_prob:
							transition_prob_value= float((transition_prob[(prev_tag,tag)]+1)/ (tagcounter[prev_tag]+vocabsize))
							#transition_prob_value= float((transition_prob[(prev_tag,tag)])/ (tagcounter[prev_tag]))
							if unknown:
								emission_prob_value = float(emission_prob[words[i]][tag]/totalTags)
							else:
								emission_prob_value= float(emission_prob[words[i]][tag]/tagcounter[tag])
							newprob = v[(i-1,prev_tag)]+ math.log(transition_prob_value,10)+ math.log(emission_prob_value,10)
							#print(newprob)
						
						

						if newprob!=0 and newprob > curprob:
							#print("yes")
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
	#calculate_accuracy("en_dev_tagged.txt")




