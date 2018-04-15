import os, sys
from collections import defaultdict
from utils import *

word_vocab = defaultdict(int)
pos_vocab = set()
pos_vocab.add('<null>')
pos_vocab.add('<root>')
label_vocab = set()
label_vocab.add('<null>')


for i, sen in enumerate(read_conll(os.path.abspath(sys.argv[1]))):
    if is_projective([e.head for e in sen[1:]]):
        for e in sen:
        	word_vocab[e.form]+=1
        	pos_vocab.add(e.pos)
        	label_vocab.add(e.relation)


wv = dict()
wv['<unk>'] = 0
wv['<null>'] = 1
wv['<root>'] = 2

for w in word_vocab.keys():
	if (word_vocab[w]>1) and not (w in wv):
		wv[w] = len(wv)
		
pv = dict()
for p in pos_vocab:
	if not (p in pv):
		pv[p] = len(pv)


w_vocab_writer = codecs.open(os.path.abspath(sys.argv[2])+'.word','w')
for w in wv.keys():
	w_vocab_writer.write(w+' '+str(wv[w])+'\n')
w_vocab_writer.close()

p_vocab_writer = codecs.open(os.path.abspath(sys.argv[2])+'.pos','w')
for i, p in enumerate(pos_vocab):
	p_vocab_writer.write(p+' '+str(i)+'\n')
p_vocab_writer.close()

a_vocab_writer = codecs.open(os.path.abspath(sys.argv[2])+'.labels','w')
for i, d in enumerate(label_vocab):
	a_vocab_writer.write(d+' '+str(i)+'\n')
a_vocab_writer.close()

a_vocab_writer = codecs.open(os.path.abspath(sys.argv[2])+'.actions','w')
a_vocab_writer.write('SHIFT'+' 0' +'\n')
for i, d in enumerate(label_vocab):
	a_vocab_writer.write('LEFT-ARC:'+d+' '+str(i+1)+'\n')
for i, d in enumerate(label_vocab):
	a_vocab_writer.write('RIGHT-ARC:'+d+' '+str(i+1+len(label_vocab))+'\n')
	
a_vocab_writer.close()
