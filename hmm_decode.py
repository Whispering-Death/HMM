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
outerTransitions = dict()

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
	outerTransitions = pickle.load(f1)
	#print(transition_prob)
	#print(emission_prob)
	#print(tagcounter)
	#print(vocabsize)

	for tag in tagcounter:
		tagSet.add(tag)
	

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
	
	totalTags=0

	for tag in tagcounter:
		totalTags+= tagcounter[tag]
	
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
				emission_prob[words[i]]= dict()
				unknown=True				
				for tag in tagSet:
					emission_prob_value = tagcounter[tag]
					emission_prob[words[i]][tag]= emission_prob_value

			if i==0:

				for tag in emission_prob[words[i]]:

					if tag not in outerTransitions:
						outerTransitions[tag]=1
					if (tag,'start') not in transition_prob:
						transition_prob[(tag,'start')]= 10e-15
						#transition_prob_value = 10e-15



					if(tag,'start') in transition_prob:

						if transition_prob[(tag,'start')]< 1:
							transition_prob_value=10e-15
						else:
							transition_prob_value= float(transition_prob[(tag,'start')]/outerTransitions[tag])
						#transition_prob_value= float((transition_prob[(tag,'start')]+1)/ (tagcounter[tag]+nlines))

						#print(transition_prob_value)
						if unknown:
							emission_prob_value = float(emission_prob[words[i]][tag]/totalTags)
						else:
							emission_prob_value= float(emission_prob[words[i]][tag]/tagcounter[tag])
						v[(i,tag)]= math.log(transition_prob_value,10) + math.log(emission_prob_value,10)

					
					
					

			else:

				
				for tag in emission_prob[words[i]]:
					#print(tag)
					#v[(i,tag)]=0
					curprob= -float("inf")
					newprob= 0
					#backpointer[(i,tag)]=""

					for prev_tag in emission_prob[words[i-1]]:

						if prev_tag not in outerTransitions:
							outerTransitions[prev_tag]=1
						if unknown:
							emission_prob_value = float(emission_prob[words[i]][tag]/totalTags)
						else:
							emission_prob_value= float(emission_prob[words[i]][tag]/tagcounter[tag])

						if (prev_tag, tag) not in transition_prob:
							transition_prob[(prev_tag, tag)]= 10e-15
							transition_prob_value= 10e-15
						
						else:
							if transition_prob[(prev_tag, tag)]< 1:
								transition_prob_value= 10e-15
							else:
								transition_prob_value= float(transition_prob[(prev_tag,tag)]/outerTransitions[prev_tag])


						temp = v[(i-1,prev_tag)]+ math.log(transition_prob_value,10)+ math.log(emission_prob_value,10)

						if temp>curprob:
							curprob=temp
							backpointer[(i,tag)]= prev_tag

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
	calculate_accuracy("en_dev_tagged.txt")
	



