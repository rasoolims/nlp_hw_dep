from collections import defaultdict
import re, codecs


class DependencyToken:
    def __init__(self, id, form, lemma, pos, cpos, feats=None, parent_id=None, relation=None, deps=None, misc=None):
        self.id = id
        self.form = form
        self.norm = normalize(form)
        self.cpos = cpos
        self.pos = pos
        self.head = parent_id
        self.relation = relation

        self.lemma = lemma
        self.feats = feats
        self.deps = deps
        self.misc = misc

    def __str__(self):
        values = [str(self.id), self.form, self.lemma, self.cpos, self.pos, self.feats,
                  str(self.head), self.relation, self.deps, self.misc]
        return u'\t'.join([u'_' if v is None else v for v in values])


def traverse(rev_head, h, visited):
    if rev_head.has_key(h):
        for d in rev_head[h]:
            if d in visited:
                return True
            visited.append(d)
            traverse(rev_head, d, visited)
    return False


def is_projective(heads):
    '''
    Decides if the set of heads for tree is projective.
    :param heads:
    :return: True if projective, else False.
    '''
    rev_head = defaultdict(list)
    for dep1 in range(1, len(heads) + 1):
        head1 = heads[dep1 - 1]
        if head1 >= 0:
            rev_head[head1].append(dep1)

    visited = list()
    if traverse(rev_head, 0, visited):
        return False
    if len(visited) < len(heads):
        return False

    root_n = 0
    for dep1 in range(1, len(heads) + 1):
        head1 = heads[dep1 - 1]

        if rev_head.has_key(dep1):
            for d2 in rev_head[dep1]:
                if (d2 < head1 < dep1) or (d2 > head1 > dep1) and head1 > 0:
                    return False

        if head1 == 0:
            root_n += 1
        for dep2 in range(1, len(heads) + 1):
            head2 = heads[dep2 - 1]
            if head1 == -1 or head2 == -1:
                continue
            if dep1 > head1 != head2:
                if dep2 > dep1 > head2 > head1:
                    return False
                if head2 > dep1 > dep2 > head1:
                    return False
            if dep1 < head1 != head2:
                if dep2 > head1 > head2 > dep1:
                    return False
                if head2 > head1 > dep2 > dep1:
                    return False
    if root_n != 1:
        return False
    return True


def read_conll(fh, test=False):
    '''
    This function reads a CoNLL file and returns a list of @ConllEntry objects.
    :param fh: file
    :return: a list of @ConllEntry objects
    '''
    root = DependencyToken(0, '*root*', '*root*', 'ROOT-POS', 'ROOT-CPOS', '_', -1, 'rroot', '_', '_')
    tokens = [root]
    for line in codecs.open(fh, 'r', encoding='UTF-8'):
        tok = line.strip().split('\t')
        if not tok or line.strip() == '':
            if len(tokens) > 1: yield tokens
            tokens = [root]
        else:
            if line[0] == '#' or '-' in tok[0] or '.' in tok[0]:
                tokens.append(line.strip())
            else:
                tokens.append(DependencyToken(int(tok[0]), tok[1], tok[2], tok[3], tok[4], tok[5],
                                             -1 if test else int(tok[6]) if tok[6] != '_' else -1,'_'  if test else tok[7], tok[8], tok[9]))
    if len(tokens) > 1:
        yield tokens


def write_conll(fn, conll_gen):
    '''
    Writes a conll file
    :param fn: output path.
    :param conll_gen: Generator for conll file (a list of @ConllEntry objects).
    :return:
    '''
    with codecs.open(fn, 'w', encoding='utf-8') as fh:
        for sentence in conll_gen:
            for entry in sentence[1:]:
                fh.write(str(entry) + u'\n')
            fh.write('\n')


def eval(gold, predicted):
    '''
    Evaluates the output vs. gold.
    :param gold: Gold Conll file.
    :param predicted: Predicted Conll file.
    :return: Unlabeled attachment accuracy (UAS), labeled attachment accuracy (LAS).
    '''
    correct_deps, correct_l, all_deps = 0, 0, 0
    r2 = open(predicted, 'r')
    for l1 in open(gold, 'r'):
        s1 = l1.strip().split('\t')
        s2 = r2.readline().strip().split('\t')
        if len(s1) > 6:
            if not is_punc(s2[3]):
                all_deps += 1
                if s1[6] == s2[6]:
                    correct_deps += 1
                    if s1[7] == s2[7]:
                        correct_l += 1
    return 100 * float(correct_deps) / all_deps, 100 * float(correct_l) / all_deps


numberRegex = re.compile("[0-9]+|[0-9]+\\.[0-9]+|[0-9]+[0-9,]+");


def normalize(word):
    return 'NUM' if numberRegex.match(word) else word.lower()


def is_punc(pos):
    return pos == '.' or pos == 'PUNC' or pos == 'PUNCT' or \
           pos == "#" or pos == "''" or pos == "(" or \
           pos == "[" or pos == "]" or pos == "{" or pos == "}" or \
           pos == "\"" or pos == "," or pos == "." or pos == ":" or \
           pos == "``" or pos == "-LRB-" or pos == "-RRB-" or pos == "-LSB-" or \
           pos == "-RSB-" or pos == "-LCB-" or pos == "-RCB-" or pos == '"' or pos == ')'
