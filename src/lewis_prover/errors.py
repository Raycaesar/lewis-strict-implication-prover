"""Public failure types for trusted-kernel initialization."""


class FrozenSpecError(RuntimeError):
    """The frozen M0 specification could not be trusted or loaded."""


class FrozenSpecStatusError(FrozenSpecError):
    """A specification component is not marked as frozen M0."""


class FrozenSpecVersionError(FrozenSpecError):
    """A specification component has an unexpected frozen version."""


class FrozenSpecFingerprintError(FrozenSpecError):
    """A certified schema or definition fingerprint does not match."""


class FrozenSpecIntegrityError(FrozenSpecError):
    """A complete M0 input file differs from the administrative freeze blob."""


class FrozenContractError(FrozenSpecError):
    """The canonical certificate contract or its lock does not match."""


class FrozenSpecBasisError(FrozenSpecError):
    """A frozen system or normalized basis has changed."""


class FrozenSpecFormatError(FrozenSpecError):
    """A frozen YAML document is missing, malformed, or ambiguous."""


class FormulaError(ValueError):
    """Base class for invalid object formulas or formula operations."""


class FormulaAstError(FormulaError):
    """A canonical JSON-compatible formula AST is malformed."""


class FormulaParseError(FormulaError):
    """Human surface notation cannot be parsed as an object formula."""


class FormulaPrintError(FormulaError):
    """A formula cannot be represented by the supported surface notation."""


class FormulaErasureError(FormulaError):
    """Diagnostic definition erasure failed against the frozen registry."""


class CertificateError(ValueError):
    """Base error for certificate input; never evidence of theorem validity."""


class CertificateDocumentError(CertificateError):
    """The serialized document violates the frozen strict JSON profile."""


class CertificateEncodingError(CertificateDocumentError):
    """The document has invalid UTF-8 or a forbidden leading BOM."""


class DuplicateCertificateKeyError(CertificateDocumentError):
    """An object repeats a member name after JSON escape decoding."""


class NonstandardJsonConstantError(CertificateDocumentError):
    """The document contains NaN, Infinity, or -Infinity."""


class CertificateTopLevelTypeError(CertificateDocumentError):
    """The document is not a JSON object."""


class CertificateStringError(CertificateDocumentError):
    """A decoded string contains a Unicode surrogate code point."""


class CertificateValueTypeError(CertificateDocumentError):
    """A decoded value is outside objects, arrays, and strings."""


class CertificateStructureError(CertificateError):
    """A decoded document violates the closed structural certificate model."""

    def __init__(self, reason: str, *, node_id: str | None = None, kind: str | None = None):
        self.reason = reason
        self.node_id = node_id
        self.kind = kind
        super().__init__(reason)


class CertificateFieldError(CertificateStructureError):
    """A proof, node, or justification has missing or unknown fields."""


class CertificateIdentifierError(CertificateStructureError):
    """An identifier or reference is not a nonempty string."""


class CertificateBasisError(CertificateStructureError):
    """A certificate does not name one exact frozen system/basis pair."""


class CertificateFormulaError(CertificateStructureError):
    """A certificate goal, conclusion, or substitution contains an invalid formula."""


class CertificateValidationError(CertificateError):
    """Deterministic whole-proof failure; inspect fields, not message wording.

    ``code`` identifies the validation category. ``detail_code`` preserves a
    node check's finer reason, and ``related_ids`` records graph witnesses.
    """

    def __init__(
        self, code: str, reason: str, *, node_id: str | None = None,
        kind: str | None = None, detail_code: str | None = None,
        related_ids: tuple[str, ...] = (),
    ):
        self.code = code
        self.reason = reason
        self.node_id = node_id
        self.kind = kind
        self.detail_code = detail_code
        self.related_ids = tuple(related_ids)
        context = f" node {node_id!r}" if node_id is not None else ""
        context += f" [{kind}]" if kind is not None else ""
        super().__init__(f"{code}{context}: {reason}")


class StructuralTransformError(FormulaError):
    """A structural operation cannot be applied to the supplied surface data."""


class SchemaInstantiationError(StructuralTransformError):
    """A registered schema or its exact substitution domain is invalid."""


class SchemaMatchError(StructuralTransformError):
    """A surface formula does not match a registered schema consistently."""


class AtomSubstitutionError(StructuralTransformError):
    """An Sa map is not a nonempty subset of the source's object atoms."""


class OccurrencePathError(StructuralTransformError):
    """A path fails the frozen grammar or cannot select a surface subtree."""


class DefinitionConversionError(StructuralTransformError):
    """One selected occurrence does not match a registered definition side."""


class NodeCheckError(CertificateError):
    """A node was not accepted, with stable node/kind/reason diagnostics."""

    def __init__(self, node_id: str, kind: str, code: str, reason: str):
        self.node_id = node_id
        self.kind = kind
        self.code = code
        self.reason = reason
        super().__init__(f"node {node_id!r} [{kind}] {code}: {reason}")
