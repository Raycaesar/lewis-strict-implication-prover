"""Small parser for exactly the human aliases frozen in ``language.yaml``."""

from __future__ import annotations

from dataclasses import dataclass

from lewis_prover.errors import FormulaParseError

from .formula import And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp


@dataclass(frozen=True, slots=True)
class _Token:
    kind: str
    text: str
    position: int


_SYMBOLS = (
    ("<=>", "EQUIV_S"),
    ("equiv_s", "EQUIV_S"),
    ("strictif", "STRICT_IMP"),
    ("<>", "POSS"),
    ("≡ₛ", "EQUIV_S"),
    ("⥽", "STRICT_IMP"),
    ("~", "NEG"),
    ("¬", "NEG"),
    ("∼", "NEG"),
    ("◇", "POSS"),
    ("&", "AND"),
    ("∧", "AND"),
    ("·", "AND"),
    ("|", "OR"),
    ("∨", "OR"),
    ("(", "LPAREN"),
    (")", "RPAREN"),
)
_WORD_OPERATORS = frozenset({"equiv_s", "strictif"})


def _identifier_start(char: str) -> bool:
    return char == "_" or char.isalpha()


def _identifier_continue(char: str) -> bool:
    return char == "_" or char.isalnum()


def _tokenize(text: str) -> tuple[_Token, ...]:
    if not isinstance(text, str):
        raise FormulaParseError("formula input must be text")
    tokens: list[_Token] = []
    index = 0
    while index < len(text):
        if text[index].isspace():
            index += 1
            continue

        matched = False
        for spelling, kind in _SYMBOLS:
            if not text.startswith(spelling, index):
                continue
            end = index + len(spelling)
            if spelling in _WORD_OPERATORS and end < len(text) and _identifier_continue(text[end]):
                continue
            tokens.append(_Token(kind, spelling, index))
            index = end
            matched = True
            break
        if matched:
            continue

        if _identifier_start(text[index]):
            end = index + 1
            while end < len(text) and _identifier_continue(text[end]):
                end += 1
            tokens.append(_Token("ATOM", text[index:end], index))
            index = end
            continue

        raise FormulaParseError(f"unsupported token {text[index]!r} at position {index}")

    tokens.append(_Token("EOF", "", len(text)))
    return tuple(tokens)


class _Parser:
    def __init__(self, text: str):
        self._tokens = _tokenize(text)
        self._index = 0

    @property
    def current(self) -> _Token:
        return self._tokens[self._index]

    def _take(self, kind: str) -> _Token | None:
        if self.current.kind != kind:
            return None
        token = self.current
        self._index += 1
        return token

    def parse(self) -> Formula:
        if self.current.kind == "EOF":
            raise FormulaParseError("formula input is empty")
        result = self._parse_equiv()
        if self.current.kind != "EOF":
            raise FormulaParseError(
                f"unexpected token {self.current.text!r} at position {self.current.position}"
            )
        return result

    def _parse_equiv(self) -> Formula:
        left = self._parse_strict_imp()
        if self._take("EQUIV_S") is None:
            return left
        right = self._parse_strict_imp()
        if self.current.kind == "EQUIV_S":
            raise FormulaParseError(
                f"equiv_s is non-associative; add parentheses at position {self.current.position}"
            )
        return EquivS(left, right)

    def _parse_strict_imp(self) -> Formula:
        left = self._parse_or()
        if self._take("STRICT_IMP") is None:
            return left
        return StrictImp(left, self._parse_strict_imp())

    def _parse_or(self) -> Formula:
        result = self._parse_and()
        while self._take("OR") is not None:
            result = Or(result, self._parse_and())
        return result

    def _parse_and(self) -> Formula:
        result = self._parse_unary()
        while self._take("AND") is not None:
            result = And(result, self._parse_unary())
        return result

    def _parse_unary(self) -> Formula:
        if self._take("NEG") is not None:
            return Neg(self._parse_unary())
        if self._take("POSS") is not None:
            return Poss(self._parse_unary())
        return self._parse_primary()

    def _parse_primary(self) -> Formula:
        atom = self._take("ATOM")
        if atom is not None:
            return Atom(atom.text)
        opening = self._take("LPAREN")
        if opening is not None:
            nested = self._parse_equiv()
            if self._take("RPAREN") is None:
                raise FormulaParseError(f"unclosed '(' at position {opening.position}")
            return nested
        token = self.current
        if token.kind == "EOF":
            raise FormulaParseError("unexpected end of formula")
        raise FormulaParseError(f"expected atom or '(' at position {token.position}; got {token.text!r}")


def parse_formula(text: str) -> Formula:
    """Parse supported project notation without expanding defined nodes."""

    return _Parser(text).parse()
