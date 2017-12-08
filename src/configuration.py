import numpy as np


class Configuration:
    def __init__(self, entries):
        self.stack = [0]
        self.entries = entries
        self.buffer = [e.id for e in entries[1:]]
        self.arcs = [(-1, '') for _ in entries]
        self.lm = [-1 for _ in entries]  # left-most modifier
        self.rm = [-1 for _ in entries]  # right-most modifier
        self.lm2 = [-1 for _ in entries]  # 2nd left-most modifier
        self.rm2 = [-1 for _ in entries]  # 2nd right-most modifier

    def next_gold_action(self):
        if len(self.stack) < 2:
            assert len(self.buffer)>0
            return 'SHIFT', None
        else:
            s0 = self.stack[-1] if len(self.stack) > 0 else None
            s1 = self.stack[-2] if len(self.stack) > 1 else None

            if s0 == self.entries[s1].head:
                return 'LEFT-ARC', self.entries[s1].relation
            elif s1 == self.entries[s0].head:
                valence_complete = True
                for j in self.buffer:
                    if self.entries[j].head == s0:
                        valence_complete = False
                        break
                if valence_complete:
                    return 'RIGHT-ARC', self.entries[s0].relation
                else:
                    assert len(self.buffer) > 0
                    return 'SHIFT', None
            else:
                assert len(self.buffer) > 0
                return 'SHIFT', None

    def do(self, action, label=''):
        if action == 'SHIFT':
            self.stack.append(self.buffer.pop(0))
        elif action == 'RIGHT-ARC':
            if self.rm[self.stack[-2]] != -1:
                self.rm2[self.stack[-2]] = self.rm[self.stack[-2]]
            self.rm[self.stack[-2]] = self.stack[-1]
            self.arcs[self.stack[-1]] = self.stack[-2], label
            self.stack.pop(-1)
        elif action == 'LEFT-ARC':
            if self.lm[self.stack[-1]] == -1 or self.lm[self.stack[-1]] > self.stack[-2]:
                if self.lm[self.stack[-1]] != -1:
                    self.lm2[self.stack[-1]] = self.lm[self.stack[-1]]
                self.lm[self.stack[-1]] = self.stack[-2]
            self.arcs[self.stack[-2]] = self.stack[-1], label
            self.stack.pop(-2)

    def doable_actions(self):
        actions = set()
        if len(self.buffer) > 0:
            actions.add('SHIFT')
        if len(self.stack) >= 2:
            actions.add('RIGHT-ARC')
        if len(self.stack) >= 2 and self.stack[-2] != 0:
            actions.add('LEFT-ARC')
        return actions

    def is_terminal_state(self):
        return len(self.stack) == 1 and len(self.buffer) == 0

    def feature_ids(self):
        s0 = self.stack[-1] if len(self.stack) > 0 else None
        s1 = self.stack[-2] if len(self.stack) > 1 else None
        s2 = self.stack[-3] if len(self.stack) > 2 else None
        s3 = self.stack[-4] if len(self.stack) > 3 else None
        b0 = self.buffer[0] if len(self.buffer) > 0 else None
        b1 = self.buffer[1] if len(self.buffer) > 1 else None
        b2 = self.buffer[2] if len(self.buffer) > 2 else None
        b3 = self.buffer[3] if len(self.buffer) > 3 else None
        s0l = self.lm[s0] if s0 and self.lm[s0] > -1 else None
        s1l = self.lm[s1] if s1 and self.lm[s1] > -1 else None
        s0r = self.rm[s0] if s0 and self.rm[s0] > -1 else None
        s1r = self.rm[s1] if s1 and self.rm[s1] > -1 else None
        s0l2 = self.lm2[s0] if s0 and self.lm2[s0] > -1 else None
        s1l2 = self.lm2[s1] if s1 and self.lm2[s1] > -1 else None
        s0r2 = self.rm2[s0] if s0 and self.rm2[s0] > -1 else None
        s1r2 = self.rm2[s1] if s1 and self.rm2[s1] > -1 else None
        s0r1r1 = self.rm[s0r] if s0r and self.rm[s0r]>-1 else None
        s1r1r1 = self.rm[s1r] if s1r and self.rm[s1r]>-1 else None
        s0l1l1 = self.lm[s0l] if s0l and self.lm[s0l] > -1 else None
        s1l1l1 = self.lm[s1l] if s1l and self.lm[s1l] > -1 else None
        return [s0,s1,s2,s3,b0,b1,b2,b3,s0l,s1l,s0r,s1r,s0l2,s1l2,s0r2,s1r2,s0r1r1,s1r1r1,s0l1l1,s1l1l1]

    def features(self):
        feats = self.feature_ids()
        word_feats, pos_feats, label_feats = [], [], []
        for i,f in enumerate(feats):
            word_feats.append(self.entries[f].form) if f is not None else word_feats.append('<null>')
            pos_feats.append(self.entries[f].pos) if f is not None else pos_feats.append('<null>')
            if i>=8:
                label_feats.append(self.arcs[f][1]) if f and self.arcs[f][0]!=-1 is not None else label_feats.append('<null>')
        return word_feats, pos_feats, label_feats

    def preprocess_score(self, scores, rlabel):
        '''
        With respect to possible actions
        :param scores:
        :return:
        '''
        da = self.doable_actions()
        can_shift = True if 'SHIFT' in da else False
        can_left_arc = True if 'LEFT-ARC' in da else False
        can_right_arc = True if 'RIGHT-ARC' in da else False
        for i in range(len(scores)):
            if not can_shift and rlabel[i] == 'SHIFT':
                scores[i] = -float('inf')
            elif not can_left_arc and rlabel[i].startswith('LEFT-ARC'):
                scores[i] = -float('inf')
            elif not can_right_arc and rlabel[i].startswith('RIGHT-ARC'):
                scores[i] = -float('inf')

    @staticmethod
    def parse(sen, rlabel, score_fn):
        conf = Configuration(sen)
        while not conf.is_terminal_state():
            wf, pf, lf = conf.features()
            scores = score_fn(wf + pf + lf)
            conf.preprocess_score(scores, rlabel)
            best_act = np.argmax(scores)
            act, label = 'SHIFT', ''
            if rlabel[best_act] != 'SHIFT':
                act, label = rlabel[best_act].split(':')
            conf.do(act, label)
        return conf
