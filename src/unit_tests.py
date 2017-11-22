import unittest
from utils import DependencyToken
from configuration import Configuration


class Tests(unittest.TestCase):
    def test_features(self):
        sen = [DependencyToken(i, '-', '-', '-', '-') for i in range(11)]
        sen[1].head = 5
        sen[2].head = 3
        sen[3].head = 5
        sen[4].head = 5
        sen[5].head = 0
        sen[6].head = 5
        sen[7].head = 8
        sen[8].head = 5
        sen[9].head = 8
        sen[10].head = 5
        conf = Configuration(sen)
        i = 0
        while not conf.is_terminal_state():
            act, l = conf.next_gold_action()
            label = (act + ':' + l) if l else act
            feats = conf.feature_ids()
            if i==8:
                assert feats[-2] == 2
                assert feats[8] == 3
            if i==11:
                assert feats[10] == 6
            conf.do(act, l)
            i+=1
        assert conf.lm[5] == 1
        assert conf.lm2[5] == 3
        assert conf.rm[5] == 10
        assert conf.rm2[5] == 8

