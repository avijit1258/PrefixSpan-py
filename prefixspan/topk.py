#! /usr/bin/env python3

from .localtyping import *

from heapq import heappush, heappushpop

from .prefixspan import PrefixSpan
from .scan import scan
from .closed import isclosed, canprune

def PrefixSpan_topk(
        self, k, closed=False,
        key=None, bound=None,
        filter=None
    ):
    # type: (PrefixSpan, int, bool, Union[None, Key], Union[None, Key], Union[None, Filter]) -> Results
    def canpass(sup):
        # type: (int) -> bool
        return len(self._results) == k and sup <= self._results[0][0]


    def verify(patt, matches):
        # type: (Pattern, Matches) -> None
        sup = key(patt, matches)
        if canpass(sup):
            return

        if (not closed or isclosed(self._db, patt, matches)) and (filter is None or filter(patt, matches)):
            (heappush if len(self._results) < k else heappushpop)(self._results, (sup, patt))


    def topk_rec(patt, matches):
        # type: (Pattern, Matches) -> None
        if len(patt) >= self.minlen:
            verify(patt, matches)

            if len(patt) == self.maxlen:
                return

        for newitem, newmatches in sorted(
                scan(self._db, matches).items(),
                key=lambda x: key(patt + [x[0]], x[1]),
                reverse=True
            ):
            newpatt = patt + [newitem]

            if canpass(bound(newpatt, newmatches)):
                break
            if closed and canprune(self._db, newpatt, newmatches):
                continue

            topk_rec(newpatt, newmatches)


    if key is None:
        key = bound = PrefixSpan.defaultkey

    # Sort by support in reverse, then by pattern.
    return sorted(self._mine(topk_rec), key=lambda x: (-x[0], x[1]))