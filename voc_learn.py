import sys

transition_prob = dict()
emission_prob= dict()

tags = set()
words= set()
tagcounter = dict()
wordcounter = dict()


def preprocess(filename):

	f= open(filename,"r")

	tok_list =[]
	for line in f:
		#print(line)
		#line=line.split()
		tup=[]
		#print(line)
		line=line.strip()
		line=line.split(" ")
		for j in line:
			#print(j,end="")
			word,tag= j.rsplit("/",1)
			
			tup.append((word,tag))

		#print(tup)
		tok_list.append(tup)


	#calculate transition probabilities

	for sentence in tok_list:
		for tup in sentence:
			words.add(tup[0])
			tags.add(tup[1])

	#print(len(words))
	#print(len(tags))

	word_tag_cnt=0
	sent_cnt=0
	for sentence in tok_list:
		sent_cnt+=1
		isStart= True
		word=""
		tag= ""
		prev_tag=""
		for tup in sentence:

			word= tup[0]
			tag= tup[1]
			word_tag_cnt+=1
			wordtag_tup=(word,tag)
			if tag in tagcounter:
				tagcounter[tag]+=1
			else:
				tagcounter[tag]=1

			if word in emission_prob:
				if tag in emission_prob[word]:
					emission_prob[word][tag]+=1
				else:
					emission_prob[word][tag]=1
			else:
				emission_prob[word]=dict()
				emission_prob[word][tag]=1
			

			trans_tup=(prev_tag,tag)
			if isStart:
				starter_tup=(tag,'start')
				if starter_tup in transition_prob:
					transition_prob[starter_tup]+=1
				else:
					transition_prob[starter_tup]=1.0
				isStart=False
				
			else:
				if trans_tup in transition_prob:
					transition_prob[trans_tup]+=1
				else:
					transition_prob[trans_tup]=1
			prev_tag=tag


	#Emission probabilities calculation

	for word in emission_prob:
		for tag in emission_prob[word]:
			emission_prob[word][tag]/= tagcounter[tag]

	# Transition probabilities calculation
	for trans_tup in transition_prob:
		if trans_tup[1]=='start':
			transition_prob[trans_tup]/= sent_cnt
		else:
			transition_prob[trans_tup]/= tagcounter[trans_tup[0]]



def storeModel():

	f1= open("hmmmodel.txt", "w")
	f1.write("Emission probabilities: \n")
	for word in emission_prob:
		
		for tag in emission_prob[word]:
			f1.write(word+" | "+tag+ " : "+str(emission_prob[word][tag])+"\n")
			
	f1.write("Transition probabilities: \n")
	for trans_tup in transition_prob:
		f1.write(trans_tup[0]+" | "+trans_tup[1]+" : "+str(transition_prob[trans_tup])+"\n")

	f1.close()


if __name__=='__main__':
	preprocess(sys.argv[1])
	storeModel()

