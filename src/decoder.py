from configuration import *
from utils import *
import sys


class Decoder:
    def __init__(self, score_fn, rindex):
        self.fn = score_fn
        self.map = rindex

    def parse(self, f, of):
        outputs = []
        for k, sen in enumerate(read_conll(f)):
            conf = Configuration.parse(sen, self.map, self.fn)
            for i, arc in enumerate(conf.arcs[1:]):
               sen[i + 1].head, sen[i+1].relation = arc[0], arc[1]
            outputs.append(sen)
            if (k + 1) % 100 == 0:
                sys.stdout.write(str(k + 1) + '...')
        sys.stdout.write('\n')
        write_conll(of, outputs)
