import os, sys
from utils import *
from configuration import Configuration

writer = codecs.open(os.path.abspath(sys.argv[2]), 'w', encoding='utf-8')
for i, sen in enumerate(read_conll(os.path.abspath(sys.argv[1]))):
    if is_projective([e.head for e in sen[1:]]):
        conf = Configuration(sen)
        while not conf.is_terminal_state():
            act, l = conf.next_gold_action()
            label = (act + ':' + l) if l else act
            wf, pf,lf = conf.features()
            writer.write(' '.join(wf) + ' ' + ' '.join(pf)  + ' ' + ' '.join(lf)+ ' ' + label + '\n')
            conf.do(act, l)
    if (i+1) % 100 == 0: sys.stdout.write(str(i+1) + '...')
writer.close()
print 'done!'
