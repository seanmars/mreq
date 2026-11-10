"""Hidden tests. Usage: python cases.py <problem> <module_dir> <mode> [perf_index]

mode "correct": differential + edge tests, prints JSON {pass,total,fails}.
mode "perf": runs one perf case, prints JSON {ok, seconds}.
mode "nperf": prints the number of perf cases.
"""
import json
import random
import sys
import time

PROBLEMS = {}


def problem(name):
    def deco(cls):
        PROBLEMS[name] = cls
        return cls
    return deco


# ---------------------------------------------------------------- justify
def ref_justify(words, W):
    res, i, n = [], 0, len(words)
    while i < n:
        j, length = i, 0
        while j < n and length + len(words[j]) + (j - i) <= W:
            length += len(words[j])
            j += 1
        line, gaps = words[i:j], j - i - 1
        if j == n or gaps == 0:
            s = " ".join(line)
            s += " " * (W - len(s))
        else:
            q, r = divmod(W - length, gaps)
            s = "".join(w + " " * (q + (1 if k < r else 0)) for k, w in enumerate(line[:-1])) + line[-1]
        res.append(s)
        i = j
    return res


@problem("justify")
class Justify:
    module, attr = "text_justify", "full_justify"
    EDGE = [
        (["This", "is", "an", "example", "of", "text", "justification."], 16),
        (["What", "must", "be", "acknowledgment", "shall", "be"], 16),
        (["Science", "is", "what", "we", "understand", "well", "enough", "to", "explain", "to", "a", "computer.",
          "Art", "is", "everything", "else", "we", "do"], 20),
        (["a"], 1), (["a"], 5), (["abc"], 3), (["a", "b", "c", "d"], 1), (["a", "b"], 3),
        (["ab", "c", "d", "efgh"], 6), (["listen", "to", "many,", "speak", "to", "a", "few."], 6),
    ]

    @staticmethod
    def gen(rng):
        W = rng.randint(1, 40)
        alphabet = "abcdefghijXYZ.,!?-'0123"
        words = ["".join(rng.choice(alphabet) for _ in range(rng.randint(1, min(W, rng.choice([3, 8, W])))))
                 for _ in range(rng.randint(1, 60))]
        return (words, W)

    @staticmethod
    def call(fn, case):
        words, W = case
        return fn(list(words), W)

    @staticmethod
    def ref(case):
        return ref_justify(*case)

    @staticmethod
    def perf_cases():
        rng = random.Random(7)
        words = ["".join(rng.choice("abcdefgh") for _ in range(rng.randint(1, 12))) for _ in range(200_000)]
        return [((words, 80), 6.0)]


# ---------------------------------------------------------------- lfu
class RefLFU:
    def __init__(self, cap):
        self.cap, self.t, self.d = cap, 0, {}

    def get(self, k):
        if k not in self.d:
            return -1
        v, f, _ = self.d[k]
        self.t += 1
        self.d[k] = (v, f + 1, self.t)
        return v

    def put(self, k, v):
        if self.cap <= 0:
            return
        self.t += 1
        if k in self.d:
            _, f, _ = self.d[k]
            self.d[k] = (v, f + 1, self.t)
            return
        if len(self.d) >= self.cap:
            victim = min(self.d, key=lambda x: (self.d[x][1], self.d[x][2]))
            del self.d[victim]
        self.d[k] = (v, 1, self.t)


class FastLFU:
    """O(1) reference, used for perf expectations; cross-checked against RefLFU in selftest."""
    def __init__(self, cap):
        from collections import defaultdict, OrderedDict
        self.cap, self.kv, self.kf, self.fk, self.minf = cap, {}, {}, defaultdict(OrderedDict), 0

    def _touch(self, k):
        f = self.kf[k]
        del self.fk[f][k]
        if not self.fk[f]:
            del self.fk[f]
            if self.minf == f:
                self.minf += 1
        self.kf[k] = f + 1
        self.fk[f + 1][k] = None

    def get(self, k):
        if k not in self.kv:
            return -1
        self._touch(k)
        return self.kv[k]

    def put(self, k, v):
        if self.cap <= 0:
            return
        if k in self.kv:
            self.kv[k] = v
            self._touch(k)
            return
        if len(self.kv) >= self.cap:
            old, _ = self.fk[self.minf].popitem(last=False)
            if not self.fk[self.minf]:
                del self.fk[self.minf]
            del self.kv[old], self.kf[old]
        self.kv[k] = v
        self.kf[k] = 1
        self.fk[1][k] = None
        self.minf = 1


@problem("lfu")
class LFU:
    module, attr = "lfu_cache", "LFUCache"
    EDGE = [
        (2, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("put", 3, 3), ("get", 2), ("get", 3), ("put", 4, 4),
             ("get", 1), ("get", 3), ("get", 4)]),
        (1, [("put", 1, 1), ("put", 2, 2), ("get", 1), ("get", 2)]),
        (2, [("put", 1, 1), ("put", 1, 10), ("put", 2, 2), ("put", 3, 3), ("get", 1), ("get", 2), ("get", 3)]),
        (3, [("put", 1, 1), ("put", 2, 2), ("put", 3, 3), ("get", 4), ("put", 4, 4), ("get", 1), ("get", 4)]),
    ]

    @staticmethod
    def gen(rng):
        cap = rng.randint(1, 5)
        ops = []
        for _ in range(rng.randint(1, 60)):
            k = rng.randint(0, 8)
            ops.append(("get", k) if rng.random() < 0.45 else ("put", k, rng.randint(0, 100)))
        return (cap, ops)

    @staticmethod
    def run(obj, ops):
        out = []
        for op in ops:
            out.append(obj.get(op[1]) if op[0] == "get" else obj.put(op[1], op[2]))
        return out

    @classmethod
    def call(cls, C, case):
        return cls.run(C(case[0]), case[1])

    @classmethod
    def ref(cls, case):
        impl = RefLFU if len(case[1]) <= 1000 else FastLFU
        return cls.run(impl(case[0]), case[1])

    @staticmethod
    def perf_cases():
        rng = random.Random(11)
        mixed = (10_000, [("get", rng.randint(0, 20_000)) if rng.random() < 0.5 else
                          ("put", rng.randint(0, 20_000), 1) for _ in range(200_000)])
        evict = (50_000, [("put", k, k) for k in range(250_000)])
        return [(mixed, 6.0), (evict, 6.0)]


# ---------------------------------------------------------------- regex
def ref_match(s, p):
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[m][n] = True
    for i in range(m, -1, -1):
        for j in range(n - 1, -1, -1):
            first = i < m and p[j] in (s[i], ".")
            if j + 1 < n and p[j + 1] == "*":
                dp[i][j] = dp[i][j + 2] or (first and dp[i + 1][j])
            else:
                dp[i][j] = first and dp[i + 1][j + 1]
    return dp[0][0]


@problem("regex")
class Regex:
    module, attr = "regex_match", "is_match"
    EDGE = [("aa", "a"), ("aa", "a*"), ("ab", ".*"), ("aab", "c*a*b"), ("mississippi", "mis*is*p*."),
            ("", ""), ("", "a*"), ("", "."), ("a", ""), ("ab", ".*c"), ("aaa", "a*a"), ("aaa", "ab*a*c*a"),
            ("a", "ab*"), ("bbbba", ".*a*a"), ("", "c*c*"), ("abcd", "d*"), ("aasdfasdfasdfasdfas", "aasdf.*asdf.*asdf.*asdf.*s")]

    @staticmethod
    def gen(rng):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 12)))
        p = "".join(rng.choice(["a", "b", ".", "a*", "b*", ".*"]) for _ in range(rng.randint(0, 8)))
        return (s, p)

    @staticmethod
    def call(fn, case):
        return bool(fn(*case))

    @staticmethod
    def ref(case):
        return ref_match(*case)

    @staticmethod
    def perf_cases():
        return [(("a" * 30, "a*" * 15 + "b"), 2.0),
                (("a" * 29 + "b", "a*a*a*a*a*a*a*a*a*a*a*a*a*c"), 2.0),
                (("ab" * 15, ".*.*.*.*.*.*.*.*.*.*.*.*.*c"), 2.0),
                (("a" * 30, ".*a*.*a*.*a*.*a*.*a*.*a*.*b"), 2.0)]


# ---------------------------------------------------------------- tagval
def _name_ok(name):
    return 1 <= len(name) <= 9 and all("A" <= c <= "Z" for c in name)


def ref_valid(code):
    stack, i, n = [], 0, len(code)
    while i < n:
        if i > 0 and not stack:
            return False
        if code.startswith("<![CDATA[", i):
            if not stack:
                return False
            j = code.find("]]>", i + 9)
            if j < 0:
                return False
            i = j + 3
        elif code.startswith("</", i):
            j = code.find(">", i + 2)
            if j < 0:
                return False
            name = code[i + 2:j]
            if not _name_ok(name) or not stack or stack[-1] != name:
                return False
            stack.pop()
            i = j + 1
        elif code.startswith("<", i):
            j = code.find(">", i + 1)
            if j < 0:
                return False
            name = code[i + 1:j]
            if not _name_ok(name):
                return False
            stack.append(name)
            i = j + 1
        else:
            if not stack:
                return False
            i += 1
    return not stack


TAG_EDGE = [
    ("<DIV>This is the first line <![CDATA[<div>]]></DIV>", True),
    ("<DIV>>>  ![cdata[]] <![CDATA[<div>]>]]>]]>>]</DIV>", True),
    ("<A>  <B> </A>   </B>", False),
    ("<DIV>  div tag is not closed  <DIV>", False),
    ("<DIV>  unmatched <  </DIV>", False),
    ("<DIV> closed tags with invalid tag name  <b>123</b> </DIV>", False),
    ("<DIV> unmatched tags with invalid tag name  </1234567890> and <CDATA[[]]>  </DIV>", False),
    ("<DIV>  unmatched start tag <B>  and unmatched end tag </C>  </DIV>", False),
    ("<A></A><B></B>", False), ("<A><![CDATA[</A>]]></A>", True), ("<![CDATA[wahaha]]]><![CDATA[]> wahaha]]>", False),
    ("<A></A>", True), ("<A>", False), ("<>", False), ("<A></A>>", False), ("a", False), ("<![CDATA[ABC]]>", False),
    ("<AAAAAAAAA></AAAAAAAAA>", True), ("<AAAAAAAAAA></AAAAAAAAAA>", False), ("<A<B>></A<B>>", False),
    ("<A><B></B></A>", True), ("<A><![CDATA[<B>]]></A>", True), ("<A><![CDATA[]]></A>", True),
    ("<A>></A>", True), ("<A><</A>", False), ("<A></A >", False), ("<A>abc</A>", True), ("<A><B>x</B>y</A>", True),
    ("<A><![CDATA[</A>]]>", False), ("<A></B></A>", False), ("< A></ A>", False), ("<A><>x</></A>", False),
]


@problem("tagval")
class TagVal:
    module, attr = "tag_validator", "is_valid"
    EDGE = [c for c, _ in TAG_EDGE]

    @staticmethod
    def _tree(rng, depth):
        name = rng.choice(["A", "B", "DIV", "AAAAAAAAA", "AAAAAAAAAA", "a", "A1", ""]) if rng.random() < 0.12 else \
            rng.choice(["A", "B", "DIV", "XYZ"])
        parts = []
        for _ in range(rng.randint(0, 3)):
            r = rng.random()
            if r < 0.35 and depth < 4:
                parts.append(TagVal._tree(rng, depth + 1))
            elif r < 0.6:
                parts.append("<![CDATA[" + "".join(rng.choice("ab<>/]![") for _ in range(rng.randint(0, 6))) + "]]>")
            else:
                parts.append("".join(rng.choice("ab >]!/[") for _ in range(rng.randint(0, 5))))
        return f"<{name}>" + "".join(parts) + f"</{name}>"

    @staticmethod
    def gen(rng):
        code = TagVal._tree(rng, 0)
        for _ in range(rng.choice([0, 0, 1, 2])):
            k = rng.randrange(len(code) + 1)
            r = rng.random()
            if r < 0.4 and code:
                code = code[:k] + code[k + 1:]
            elif r < 0.8:
                code = code[:k] + rng.choice("<>/![]CDATAa") + code[k:]
            else:
                code = code + rng.choice(["<A></A>", "x", "<![CDATA[]]>"])
        return code or "a"

    @staticmethod
    def call(fn, case):
        return bool(fn(case))

    @staticmethod
    def ref(case):
        return ref_valid(case)

    @staticmethod
    def perf_cases():
        return [("<A>" + "<B>x</B>" * 20_000 + "</A>", 3.0)]


# ---------------------------------------------------------------- shared
def catch(f):
    """Return the result, or the exception type name; ValueError is an expected answer."""
    try:
        return f()
    except Exception as e:
        return type(e).__name__


# ---------------------------------------------------------------- checkout
from fractions import Fraction
import math


def ref_checkout(items, coupon=None):
    if coupon not in (None, "SAVE100", "OFF10"):
        raise ValueError("coupon")
    qty, price, cat = {}, {}, {}
    for it in items:
        if it["qty"] < 0 or it["price"] < 0:
            raise ValueError("negative")
        qty[it["sku"]] = qty.get(it["sku"], 0) + it["qty"]
        price[it["sku"]], cat[it["sku"]] = it["price"], it["category"]
    if sum(qty.values()) == 0:
        return 0
    sub = Fraction(0)
    for sku, n in qty.items():
        p = price[sku]
        if cat[sku] == "drink":
            sub += p * (n - n // 2) + Fraction(6, 10) * p * (n // 2)
        else:
            sub += p * n
    if coupon == "SAVE100" and sub >= 1000:
        sub -= 100
    if coupon == "OFF10":
        sub *= Fraction(9, 10)
    ship = 0 if sub >= 499 else 60
    return math.floor(sub + ship + Fraction(1, 2))


def _it(sku, price, qty, cat="food"):
    return {"sku": sku, "name": sku.upper(), "price": price, "qty": qty, "category": cat}


@problem("checkout")
class Checkout:
    module, attr = "checkout", "total"
    LABELED = True
    EDGE = [
        ("second-item same sku only", ([_it("tea", 100, 1, "drink"), _it("cola", 100, 1, "drink")], None)),
        ("second-item floor(n/2)", ([_it("tea", 100, 3, "drink")], None)),
        ("second-item merge same sku", ([_it("tea", 100, 1, "drink"), _it("tea", 100, 1, "drink")], None)),
        ("second-item non-drink", ([_it("cake", 100, 2)], None)),
        ("round half up once", ([_it("x", 25, 1)], "OFF10")),
        ("round half up once", ([_it("tea", 15, 1, "drink"), _it("x", 5, 1)], "OFF10")),
        ("round once not per step", ([_it("tea", 5, 2, "drink"), _it("milk", 5, 2, "drink"), _it("x", 1, 1)], "OFF10")),
        ("SAVE100 threshold after item discount", ([_it("tea", 600, 2, "drink")], "SAVE100")),
        ("SAVE100 inclusive 1000", ([_it("x", 1000, 1)], "SAVE100")),
        ("SAVE100 below threshold no error", ([_it("x", 999, 1)], "SAVE100")),
        ("OFF10 after item discount", ([_it("tea", 100, 2, "drink")], "OFF10")),
        ("coupon not on shipping", ([_it("x", 100, 1)], "OFF10")),
        ("free shipping after coupon", ([_it("x", 550, 1)], "OFF10")),
        ("free shipping inclusive 499", ([_it("x", 499, 1)], None)),
        ("free shipping exact not rounded", ([_it("x", 554, 1)], "OFF10")),
        ("empty cart", ([], None)),
        ("all qty zero", ([_it("x", 100, 0)], None)),
        ("unknown coupon ValueError", ([_it("x", 100, 1)], "BOGUS")),
        ("coupon case-sensitive", ([_it("x", 100, 1)], "off10")),
        ("negative qty ValueError", ([_it("x", 100, -1)], None)),
        ("negative price ValueError", ([_it("x", -5, 1)], None)),
        ("qty zero ignored", ([_it("x", 100, 0), _it("y", 600, 1)], None)),
    ]

    @staticmethod
    def gen(rng):
        skus = {f"s{i}": (rng.choice([5, 15, 25, 35, 45, 99, 120, 250, 333, 499, 550]),
                          rng.choice(["drink", "drink", "food", "book"])) for i in range(6)}
        items = []
        for _ in range(rng.randint(0, 5)):
            s = rng.choice(list(skus))
            items.append(_it(s, skus[s][0], rng.randint(0, 5), skus[s][1]))
        return (items, rng.choice([None, None, "SAVE100", "OFF10"]))

    @staticmethod
    def call(fn, case):
        import copy
        items, coupon = copy.deepcopy(case)
        return catch(lambda: fn(items, coupon) if coupon is not None else fn(items))

    @staticmethod
    def ref(case):
        return catch(lambda: ref_checkout(*case))

    @staticmethod
    def perf_cases():
        return []


# ---------------------------------------------------------------- sla
from datetime import datetime as _dt, date as _date, time as _time, timedelta as _td

WINDOWS = [(9, 12), (13, 18)]


def ref_due(created, hours, holidays=frozenset()):
    if hours < 0:
        raise ValueError("negative")
    remaining = _td(hours=hours)
    t = created
    while True:
        d = t.date()
        if d.weekday() < 5 and d not in holidays:
            for s, e in WINDOWS:
                ws, we = _dt.combine(d, _time(s)), _dt.combine(d, _time(e))
                if t < we:
                    start = max(t, ws)
                    avail = we - start
                    if remaining <= avail:
                        return start + remaining
                    remaining -= avail
                    t = we
        t = _dt.combine(d + _td(days=1), _time(0))


D = _dt  # 2026-11-09 is a Monday


@problem("sla")
class Sla:
    module, attr = "sla", "due_at"
    LABELED = True
    HOL = frozenset({_date(2026, 11, 11)})
    EDGE = [
        ("inside window simple", (D(2026, 11, 9, 10, 0), 1, frozenset())),
        ("lunch skipped", (D(2026, 11, 9, 11, 0), 2, frozenset())),
        ("ends exactly 18:00", (D(2026, 11, 9, 17, 0), 1, frozenset())),
        ("ends exactly 12:00", (D(2026, 11, 9, 11, 0), 1, frozenset())),
        ("created after hours", (D(2026, 11, 9, 19, 30), 1, frozenset())),
        ("created before hours", (D(2026, 11, 9, 7, 0), 1, frozenset())),
        ("created during lunch", (D(2026, 11, 9, 12, 30), 1, frozenset())),
        ("created exactly 12:00", (D(2026, 11, 9, 12, 0), 1, frozenset())),
        ("created exactly 18:00", (D(2026, 11, 9, 18, 0), 1, frozenset())),
        ("weekend skipped", (D(2026, 11, 13, 17, 0), 2, frozenset())),
        ("created on weekend", (D(2026, 11, 14, 10, 0), 1, frozenset())),
        ("holiday skipped", (D(2026, 11, 10, 17, 0), 2, HOL)),
        ("created on holiday", (D(2026, 11, 11, 10, 0), 1, HOL)),
        ("zero hours inside", (D(2026, 11, 9, 10, 15), 0, frozenset())),
        ("zero hours outside", (D(2026, 11, 9, 20, 0), 0, frozenset())),
        ("zero hours at 12:00", (D(2026, 11, 9, 12, 0), 0, frozenset())),
        ("fractional hours", (D(2026, 11, 9, 11, 0), 1.5, frozenset())),
        ("seconds kept", (D(2026, 11, 9, 10, 0, 37), 1, frozenset())),
        ("multi-day span", (D(2026, 11, 9, 9, 0), 24, frozenset())),
        ("negative ValueError", (D(2026, 11, 9, 10, 0), -1, frozenset())),
        ("default holidays", (D(2026, 11, 9, 17, 30), 1, None)),
    ]

    @staticmethod
    def gen(rng):
        base = D(2026, 11, 2)
        created = base + _td(days=rng.randint(0, 20), minutes=rng.randrange(0, 24 * 60, rng.choice([1, 15, 30, 60])))
        hours = rng.choice([0, 0.25, 0.5, 1, 1.5, 2, 3, 4, 5, 8, 9, 16, 40]) if rng.random() < 0.8 else rng.randint(1, 60) / 4
        hol = frozenset(_date(2026, 11, d) for d in rng.sample(range(2, 30), rng.choice([0, 0, 1, 3])))
        return (created, hours, hol)

    @staticmethod
    def call(fn, case):
        c, h, hol = case
        return catch(lambda: fn(c, h) if hol is None else fn(c, h, set(hol)))

    @staticmethod
    def ref(case):
        c, h, hol = case
        return catch(lambda: ref_due(c, h, hol or frozenset()))

    @staticmethod
    def perf_cases():
        return []


# ---------------------------------------------------------------- booking
class RefBook:
    def __init__(self):
        self.next, self.active = 1, {}

    def book(self, room, start, end):
        if start >= end or start < 0 or end > 1440:
            raise ValueError("range")
        for r, s, e in self.active.values():
            if r == room and s < end and start < e:
                return None
        i = self.next
        self.next += 1
        self.active[i] = (room, start, end)
        return i

    def cancel(self, i):
        return self.active.pop(i, None) is not None

    def free_slots(self, room, a, b):
        if a >= b:
            raise ValueError("range")
        busy = sorted((max(s, a), min(e, b)) for r, s, e in self.active.values() if r == room and s < b and e > a)
        out, cur = [], a
        for s, e in busy:
            if s > cur:
                out.append((cur, s))
            cur = max(cur, e)
        if cur < b:
            out.append((cur, b))
        return out


@problem("booking")
class Booking:
    module, attr = "booking", "BookingBook"
    LABELED = True
    EDGE = [
        ("back-to-back allowed", [("book", "A", 540, 600), ("book", "A", 600, 660)]),
        ("overlap returns None", [("book", "A", 540, 600), ("book", "A", 570, 630)]),
        ("contained overlap None", [("book", "A", 540, 700), ("book", "A", 560, 600)]),
        ("rooms independent", [("book", "A", 540, 600), ("book", "B", 540, 600)]),
        ("room case-sensitive", [("book", "A", 540, 600), ("book", "a", 540, 600)]),
        ("start>=end ValueError", [("book", "A", 600, 600)]),
        ("start<0 ValueError", [("book", "A", -10, 60)]),
        ("end>1440 ValueError", [("book", "A", 1400, 1441)]),
        ("full day ok", [("book", "A", 0, 1440)]),
        ("ids start at 1 shared", [("book", "A", 0, 10), ("book", "B", 0, 10), ("book", "C", 0, 10)]),
        ("failed booking no id", [("book", "A", 0, 10), ("book", "A", 5, 15), ("book", "A", 10, 20)]),
        ("ids not reused", [("book", "A", 0, 10), ("cancel", 1), ("book", "A", 0, 10)]),
        ("cancel twice False", [("book", "A", 0, 10), ("cancel", 1), ("cancel", 1)]),
        ("cancel unknown False", [("cancel", 99)]),
        ("cancel frees slot", [("book", "A", 0, 10), ("cancel", 1), ("book", "A", 5, 15)]),
        ("free empty room", [("free", "Z", 540, 1080)]),
        ("free sorted gaps", [("book", "A", 700, 760), ("book", "A", 540, 600), ("free", "A", 480, 1080)]),
        ("free no zero-length", [("book", "A", 540, 600), ("book", "A", 600, 660), ("free", "A", 540, 720)]),
        ("free clip", [("book", "A", 500, 600), ("book", "A", 1000, 1100), ("free", "A", 540, 1080)]),
        ("free fully booked", [("book", "A", 0, 1440), ("free", "A", 540, 1080)]),
        ("free after cancel", [("book", "A", 540, 600), ("cancel", 1), ("free", "A", 540, 600)]),
        ("free bad range ValueError", [("free", "A", 600, 600)]),
    ]

    @staticmethod
    def gen(rng):
        ops = []
        for _ in range(rng.randint(1, 25)):
            r = rng.random()
            room = rng.choice(["A", "B"])
            if r < 0.55:
                s = rng.randrange(0, 1440, 30) if rng.random() < 0.95 else rng.choice([-30, 1440])
                e = s + rng.choice([0, 30, 60, 90, 120]) if rng.random() < 0.95 else s - 30
                ops.append(("book", room, s, e))
            elif r < 0.75:
                ops.append(("cancel", rng.randint(0, 8)))
            else:
                a = rng.randrange(0, 1440, 60)
                # stay inside one day: the intent card says nothing about ranges past 1440
                ops.append(("free", room, a, min(a + rng.choice([0, 60, 240, 600]), 1440)))
        return ops

    @staticmethod
    def run(obj, ops):
        out = []
        for op in ops:
            if op[0] == "book":
                out.append(catch(lambda: obj.book(op[1], op[2], op[3])))
            elif op[0] == "cancel":
                out.append(catch(lambda: obj.cancel(op[1])))
            else:
                out.append(catch(lambda: [tuple(x) for x in obj.free_slots(op[1], op[2], op[3])]))
        return out

    @classmethod
    def call(cls, C, case):
        return cls.run(C(), case)

    @classmethod
    def ref(cls, case):
        return cls.run(RefBook(), case)

    @staticmethod
    def perf_cases():
        return []


def load(P, module_dir):
    sys.path.insert(0, module_dir)
    mod = __import__(P.module)
    return getattr(mod, P.attr)


def main():
    pname, module_dir, mode = sys.argv[1:4]
    P = PROBLEMS[pname]
    if pname == "tagval":
        for code, want in TAG_EDGE:
            assert ref_valid(code) == want, code
    if mode == "nperf":
        print(json.dumps({"n": len(P.perf_cases())}))
        return
    fn = load(P, module_dir)
    if mode == "perf":
        case, limit = P.perf_cases()[int(sys.argv[4])]
        t = time.perf_counter()
        try:
            got = P.call(fn, case)
        except Exception as e:
            print(json.dumps({"ok": False, "seconds": time.perf_counter() - t, "error": repr(e)[:200]}))
            return
        sec = time.perf_counter() - t
        ok = got == P.ref(case)
        print(json.dumps({"ok": ok and sec <= limit, "seconds": round(sec, 3), "correct": ok}))
        return
    rng = random.Random(20261109)
    edges = P.EDGE if getattr(P, "LABELED", False) else [("edge", c) for c in P.EDGE]
    cases = [("edge", lab, c) for lab, c in edges] + [("random", None, P.gen(rng)) for _ in range(3000)]
    res = {"edge": [0, 0], "random": [0, 0], "rules": {}, "fails": []}
    for kind, lab, case in cases:
        res[kind][1] += 1
        if lab:
            res["rules"].setdefault(lab, [0, 0])[1] += 1
        try:
            got = P.call(fn, case)
            want = P.ref(case)
            if got == want:
                res[kind][0] += 1
                if lab:
                    res["rules"][lab][0] += 1
            elif len(res["fails"]) < 8:
                res["fails"].append({"case": repr(case)[:300], "got": repr(got)[:200], "want": repr(want)[:200]})
        except Exception as e:
            if len(res["fails"]) < 5:
                res["fails"].append({"case": repr(case)[:300], "error": repr(e)[:200]})
    print(json.dumps(res))


if __name__ == "__main__":
    main()
