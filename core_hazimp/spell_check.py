# -*- coding: utf-8 -*-

"""
Spell checking based on http://norvig.com/spell-correct.html

"""

import collections

ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


def edits1(word):  # pylint: disable=C0111
    """ Build a set of the word with various changes
    """

    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b) > 1]
    replaces = [a + c + b[1:] for a, b in splits for c in ALPHABET if b]
    inserts = [a + c + b for a, b in splits for c in ALPHABET]
    return set(deletes + transposes + replaces + inserts)


def train(features):
    """
    Builds the nwords data structure.

    """
    model = collections.defaultdict(lambda: 1)
    for f in features:
        model[f] += 1
    return model


class SpellCheck(object):
    """
    Given a base set of works, check the spelling of a new work and
    suggest what base word was meant.

    """
    def __init__(self, base_words):
        """
        :param word_list: The list of known words.
        """
        self.nwords = train(base_words)
        self.base_words = base_words

    def known_edits2(self, word):  # pylint: disable=C0111
        return set(e2 for e1 in edits1(word) for e2 in edits1(e1)
                   if e2 in self.nwords)

    def known(self, words):  # pylint: disable=C0111
        return set(w for w in words if w in self.nwords)

    def correct(self, word):
        """
        If the word is known 'word' is returned.
        If the word is unknow, by 1 or 2 modifications from known words,
            The known word is returned
        Otherwise the unknown word is returned.

        :param word: The word that might have a typo.
        :returns: ??
        """
        candidates = self.known([word]) or self.known(edits1(word)) or \
            self.known_edits2(word) or [word]
        return max(candidates, key=self.nwords.get)
