import re
import csv

#Data structure for syntax trees
#Each tree has a list of children, a parent tree, a lexical token
#A head (top of the tree) and a level (depth in the tree)
class Tree:
	def __init__(self, p, t, c, l, h):
		self.children = []
		self.parent = p
		self.token = t
		self.level = l
		if(h):
			self.head = self
		elif(self.parent == None):
			self.head = None
		else:
			self.head = self.parent.get_head()

	#Accessor and modifier methods
	def get_head(self):
		return self.head
	def get_parent(self):
		return self.parent
	def get_children(self):
		return self.children
	def get_level(self):
		return self.level
	def get_token(self):
		return self.token
	def set_head(self, t):
		self.head = t.get_head()
	def set_parent(self, t):
		self.parent = t

	#Inserts node to child list
	#Assigns that node's parent to the current node
	def add_child(self, t):
		self.children.append(t)
		t.set_parent(self)
		t.set_head(self)
		return t

	#Inserts smaller tree into larger tree at correct position
	def add(self, t):
		if(self.token == None):
			self.children = t.get_children()
			self.parent = t.get_parent()
			self.token = t.get_token()
			self.level = t.get_level()
			self.head = t.get_head()
			return True
		elif(t.get_level() == self.level):
			t.set_parent(self.parent) 
			t.set_head(self)
			self.parent.add_child(t)
			return True
		else:
			for i in range(len(self.children)-1,-1, -1):
				if(self.children[i].add(t)):
					return True
			
	#True if a leaf, false otherwise
	def leaf(self):
		if(len(self.children) == 0):
			return True
		else:
			return False
	
	#String representation of tree
	def to_string(self):
		s = "[" + self.token 
		for child in self.children:
			s += child.to_string()
		s += "]"
		return s

	#Returns list of adverb phrase nodes
	#And their parents, siblings, and children
	def find_adv(self):
		to_return = []
		if("ADVP" in self.token):
			p_token = self.parent.get_token()
			l_token = []
			for l in self.parent.get_children():
				l_token.append(l.get_token())
			c_token = []
			for child in self.children:
				c_token.append(child.get_token())
			to_return.append((self.token, p_token, l_token, c_token))
		for child in self.children:
			adv_child = child.find_adv()
			to_return = to_return + adv_child
		return to_return


#Parses Penn Treebank string into tree data structure
def parse(txt):
	lines = []
	for line in range(0, len(txt)):
		pos = get_pos(txt[line])
		lines.append(pos)
	sentence = Tree(None, None, [], None, None)		
	for i in range(0, len(lines)):
		tree = Tree(None, None, [], None, None)
		for j in range(0, len(lines[i])):
			if(j == 0):
				tree.add(Tree(None, lines[i][j][0], [], lines[i][j][1], True))
			else:
				tree = tree.add_child(Tree(None, lines[i][j][0], [], lines[i][j][1], False)) 
		tree = tree.get_head()
		sentence.add(tree)
	return sentence


#Parses all sentences in PTB corpus
def read():
	f = open('allwsj.parse', 'r')
	txt = f.readlines()
	lst = []
	sentences = []
	for line in txt:
		if("(" in line):
			lst.append(line)
		else:
			sentences.append(parse(lst))
			lst = []
	return sentences

#Gets lexical token from given line of PTB string
def get_token(line):
	search = re.search(" ([^\(]*?)(\))", line).group(1)
	return search

#Gets part of speech from given line of PTB string
def get_pos(line):
	to_return = []
	for pos in re.finditer('\(([A-Z-0-9,.;!\?`]+) ', line):
		to_return.append((pos.group(1), str(pos.start())))
	token = get_token(line)
	to_return.append((token, line.index(token)))
	return to_return


#Stores adverbs and corresponding parents, siblings, children
prev_level = {}
same_level = {}
next_level = {}

#Iteratures through all trees and calls find_adv
#Stores parent, sibling, and child nodes for each adverb
def find_adverbs(sents):
	for s in sents:
		adv_tuples = s.find_adv()
		if(len(adv_tuples) > 0):
			for adv_tuple in adv_tuples:
				if(adv_tuple[0] not in prev_level):
					prev_level[adv_tuple[0]] = []
				if(adv_tuple[0] not in same_level):
					same_level[adv_tuple[0]] = []
				if(adv_tuple[0] not in next_level):
					next_level[adv_tuple[0]] = []

				prev_level[adv_tuple[0]].append(adv_tuple[1])
				i = adv_tuple[2].index(adv_tuple[0])
				if(i-1 >= 0):
					same_level[adv_tuple[0]].append(adv_tuple[2][i-1])
				if(i + 1 < len(adv_tuple[2])):
					same_level[adv_tuple[0]].append(adv_tuple[2][i+1])
				next_level[adv_tuple[0]] += adv_tuple[3] 


#For each type of adverb, determines what percent of occurences of that adverb
#Occur with a given other type as the parent, sibling, or child
#Only types with >0.1 frequency recorded
def stats():
	csv_file_p = open('prevs.csv', 'wb')
	writer_p = csv.writer(csv_file_p)
	
	csv_file_s = open('sames.csv', 'wb')
	writer_s = csv.writer(csv_file_s)

	csv_file_n = open('nexts.csv', 'wb')
	writer_n = csv.writer(csv_file_n)

	for pos in prev_level:
	
		writer_p.writerow([])
		writer_s.writerow([])
		writer_n.writerow([])

		writer_p.writerow([pos])
		writer_s.writerow([pos])
		writer_n.writerow([pos])


		prevs = prev_level[pos]
		sames = same_level[pos]
		nexts = next_level[pos]

		d_prevs = {}
		d_sames = {}
		d_nexts = {}

		for i in prevs:
			if(i in d_prevs):
				d_prevs[i]+= 1
			else:
				d_prevs[i] = 1
		for i in sames:
			if(i in d_sames):
				d_sames[i]+= 1
			else:
				d_sames[i] = 1
		for i in nexts:
			if(i in d_nexts):
				d_nexts[i]+= 1
			else:
				d_nexts[i] = 1


		sum_prevs = sum(d_prevs.values())
		sum_sames = sum(d_sames.values())
		sum_nexts = sum(d_nexts.values())

		for i in d_prevs:
			d_prevs[i] = float(d_prevs[i])/float(sum_prevs)
		
		for i in d_sames: 
			d_sames[i] = float(d_sames[i])/float(sum_sames)

		for i in d_nexts:
			d_nexts[i] = float(d_nexts[i])/float(sum_nexts)


		for key, value in d_prevs.items():
			if(value >= 0.1):
				writer_p.writerow([key, value])

		for key, value in d_sames.items():
			if(value >= 0.1):
				writer_s.writerow([key, value])

		for key, value in d_nexts.items():
			if(value >= 0.1):
				writer_n.writerow([key, value])
		


find_adverbs(read())

stats()


	



