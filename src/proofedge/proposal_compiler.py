"""Compile model-ranked migration risks into citable executable test specifications."""

from __future__ import annotations

import ast
import re
from dataclasses import asdict, dataclass
from typing import Any

from proofedge.contracts import extract_contracts
from proofedge.engines import validate_plan_document
from proofedge.security import FileRecord, RepositorySnapshot

_SENSITIVE_LITERAL = re.compile(
    r"(gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,}|AKIA[0-9A-Z]{16}|"
    r"hf_[A-Za-z0-9]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|"
    r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions|"
    r"reveal\s+(?:the\s+)?(?:system|developer)\s+(?:prompt|message))",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class _Candidate:
    candidate_id: str
    score: int
    proposal: dict[str, Any]
    match_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PlanCompilation:
    document: dict[str, Any]
    mode: str
    candidates_total: int
    raw_proposals_total: int
    model_aligned_candidates: int
    selections: tuple[dict[str, Any], ...]

    def metadata(self) -> dict[str, Any]:
        return {key: value for key, value in asdict(self).items() if key != "document"}


def _line_containing(record: FileRecord, terms: list[str], fallback: int) -> int:
    for index, line in enumerate(record.text.splitlines(), start=1):
        if any(term and term in line for term in terms):
            return index
    return fallback


def _plain(value: str, maximum: int) -> str:
    cleaned = "".join(
        " " if ord(character) < 32 or ord(character) == 127 else character for character in value
    ).strip()
    return (cleaned or "change")[:maximum]


def _response_codes(signature: str) -> tuple[str, ...]:
    if not signature.startswith("responses="):
        return ()
    return tuple(code for code in signature.removeprefix("responses=").split(",") if code)


def _http_candidates(source: RepositorySnapshot, target: RepositorySnapshot) -> list[_Candidate]:
    source_contracts = {
        contract.key: contract for contract in extract_contracts(source) if contract.kind == "http"
    }
    target_contracts = {
        contract.key: contract for contract in extract_contracts(target) if contract.kind == "http"
    }
    candidates: list[_Candidate] = []
    for key, source_contract in source_contracts.items():
        target_contract = target_contracts.get(key)
        if target_contract is None or source_contract.signature == target_contract.signature:
            continue
        if len(source_contract.path) > 300:
            continue
        source_codes = _response_codes(source_contract.signature)
        target_codes = _response_codes(target_contract.signature)
        changed_codes = sorted(set(source_codes) ^ set(target_codes))
        source_record = source.by_path[source_contract.path]
        line = _line_containing(source_record, changed_codes, source_contract.line)
        purpose = _plain(
            f"Compare source {source_contract.name} {source_contract.signature} with target "
            f"{target_contract.name} {target_contract.signature}",
            300,
        )
        inputs = [_plain(source_contract.name, 160)]
        if source_contract.name.split(" ", 1)[0] in {"POST", "PUT", "PATCH"}:
            inputs.append("valid request body")
        candidates.append(
            _Candidate(
                candidate_id=f"http:{source_contract.name.casefold()}",
                score=100,
                proposal={
                    "name": _plain(f"Investigate {source_contract.name} response contract", 100),
                    "purpose": purpose,
                    "repository": "source",
                    "path": source_contract.path,
                    "line": line,
                    "inputs": inputs,
                    "expected_relation": "investigate",
                    "priority": "high",
                },
                match_terms=tuple(
                    dict.fromkeys(
                        [
                            *re.findall(r"[a-z0-9_/.-]+", source_contract.name.casefold()),
                            *changed_codes,
                        ]
                    )
                ),
            )
        )
    return candidates


def _python_functions(snapshot: RepositorySnapshot) -> dict[tuple[str, str], ast.FunctionDef]:
    functions: dict[tuple[str, str], ast.FunctionDef] = {}
    for record in snapshot.files:
        if record.is_test or not record.path.casefold().endswith(".py"):
            continue
        try:
            tree = ast.parse(record.text, filename=record.path)
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef)
            ) and not node.name.startswith("_"):
                functions[(record.path, node.name)] = node
    return functions


def _argument_names(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    return [
        argument.arg
        for argument in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
    ]


def _literal(node: ast.AST) -> str:
    if isinstance(node, ast.Constant):
        value = str(node.value)
        return "[REDACTED_UNTRUSTED_LITERAL]" if _SENSITIVE_LITERAL.search(value) else value[:120]
    try:
        value = ast.unparse(node)[:120]
        return "[REDACTED_UNTRUSTED_LITERAL]" if _SENSITIVE_LITERAL.search(value) else value
    except (AttributeError, ValueError):
        return "boundary-value"


def _call_inputs(
    snapshot: RepositorySnapshot,
    function_name: str,
    argument_names: list[str],
    preferred_arguments: set[str] | None = None,
) -> list[str]:
    preferred_arguments = preferred_arguments or set()
    choices: list[tuple[int, list[str]]] = []
    for record in snapshot.files:
        if not record.is_test or not record.path.casefold().endswith(".py"):
            continue
        try:
            tree = ast.parse(record.text, filename=record.path)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            called_name = (
                node.func.id
                if isinstance(node.func, ast.Name)
                else node.func.attr
                if isinstance(node.func, ast.Attribute)
                else ""
            )
            if called_name != function_name:
                continue
            values: list[tuple[str, str]] = []
            for index, value in enumerate(node.args):
                name = argument_names[index] if index < len(argument_names) else f"arg{index + 1}"
                values.append((name, _literal(value)))
            values.extend((item.arg or "kwargs", _literal(item.value)) for item in node.keywords)
            rendered = [f"{name}={value}" for name, value in values]
            preferred = sum(name in preferred_arguments for name, _value in values)
            boundary = sum(
                ".005" in value or "duplicate" in value.casefold() for _name, value in values
            )
            choices.append((preferred * 100 + boundary * 10 + len(rendered), rendered))
    if not choices:
        return []
    return max(choices, key=lambda item: item[0])[1][:4]


def _function_text(record: FileRecord, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    lines = record.text.splitlines()
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


def _python_candidates(source: RepositorySnapshot, target: RepositorySnapshot) -> list[_Candidate]:
    source_functions = _python_functions(source)
    target_functions = _python_functions(target)
    candidates: list[_Candidate] = []
    for key, source_node in source_functions.items():
        target_node = target_functions.get(key)
        if target_node is None:
            continue
        path, name = key
        if len(path) > 300:
            continue
        source_record = source.by_path[path]
        target_record = target.by_path[path]
        source_arguments = _argument_names(source_node)
        target_arguments = _argument_names(target_node)
        removed_arguments = [item for item in source_arguments if item not in target_arguments]
        source_text = _function_text(source_record, source_node)
        target_text = _function_text(target_record, target_node)
        if removed_arguments:
            inputs = _call_inputs(
                source,
                name,
                source_arguments,
                preferred_arguments=set(removed_arguments),
            )
            if not inputs:
                inputs = [
                    f"{source_arguments[0]}=boundary-value",
                    f"{removed_arguments[0]}=non-default",
                ]
            removed = ", ".join(removed_arguments)
            candidates.append(
                _Candidate(
                    candidate_id=f"python-signature:{path}:{name}",
                    score=100,
                    proposal={
                        "name": f"Investigate removed {name} parameter {removed}",
                        "purpose": (
                            f"Compare source {name} behavior with {removed} against target {name} "
                            f"behavior after removal of {removed}"
                        ),
                        "repository": "source",
                        "path": path,
                        "line": source_node.lineno,
                        "inputs": inputs,
                        "expected_relation": "investigate",
                        "priority": "high",
                    },
                    match_terms=(name.casefold(), *(item.casefold() for item in removed_arguments)),
                )
            )
            continue
        if ast.dump(source_node) == ast.dump(target_node):
            continue
        changed_text = f"{source_text}\n{target_text}".casefold()
        behavior = (
            "rounding behavior"
            if any(marker in changed_text for marker in ("round", "quantize", "decimal"))
            else "implementation behavior"
        )
        inputs = _call_inputs(source, name, source_arguments)
        if not inputs:
            first = source_arguments[0] if source_arguments else "input"
            inputs = [f"{first}=boundary-value"]
        candidates.append(
            _Candidate(
                candidate_id=f"python-body:{path}:{name}",
                score=90 if behavior == "rounding behavior" else 70,
                proposal={
                    "name": f"Investigate {name} {behavior}",
                    "purpose": (
                        f"Compare source {name} {behavior} with target {name} {behavior} "
                        "for the changed implementation"
                    ),
                    "repository": "source",
                    "path": path,
                    "line": source_node.lineno,
                    "inputs": inputs,
                    "expected_relation": "investigate",
                    "priority": "high",
                },
                match_terms=(
                    name.casefold(),
                    *re.findall(r"[a-z0-9_.-]+", " ".join(inputs).casefold()),
                ),
            )
        )
    return candidates


def _model_alignment(
    candidate: _Candidate, proposals: list[dict[str, Any]]
) -> tuple[int, int | None]:
    best = (0, None)
    for index, proposal in enumerate(proposals):
        if proposal.get("path") != candidate.proposal["path"]:
            continue
        content = " ".join(
            [
                str(proposal.get("name", "")),
                str(proposal.get("purpose", "")),
                *[str(item) for item in proposal.get("inputs", [])],
            ]
        ).casefold()
        score = sum(term in content for term in candidate.match_terms if len(term) >= 3)
        if score > best[0]:
            best = (score, index)
    return best


def compile_model_plan(
    model_document: dict[str, Any],
    source: RepositorySnapshot,
    target: RepositorySnapshot,
) -> PlanCompilation:
    """Publish citable change tests while retaining the model as a bounded ranker."""

    raw_proposals = list(model_document.get("tests", []))
    candidates = [*_http_candidates(source, target), *_python_candidates(source, target)]
    if not candidates:
        return PlanCompilation(
            document=model_document,
            mode="model-direct",
            candidates_total=0,
            raw_proposals_total=len(raw_proposals),
            model_aligned_candidates=0,
            selections=(),
        )

    ranked: list[tuple[int, int, int | None, _Candidate]] = []
    for candidate in candidates:
        alignment, model_index = _model_alignment(candidate, raw_proposals)
        ranked.append((candidate.score + min(alignment, 5), alignment, model_index, candidate))
    ranked.sort(key=lambda item: (-item[0], item[3].candidate_id))

    tests: list[dict[str, Any]] = []
    selections: list[dict[str, Any]] = []
    aligned = 0
    for _rank, _alignment, model_index, candidate in ranked[:2]:
        proposal = dict(candidate.proposal)
        if model_index is not None:
            aligned += 1
            priority = raw_proposals[model_index].get("priority")
            if priority in {"high", "medium", "low"}:
                proposal["priority"] = priority
        tests.append(proposal)
        selections.append(
            {
                "candidate_id": candidate.candidate_id,
                "selection_reason": "model-aligned" if model_index is not None else "safety-floor",
                "raw_model_proposal_index": model_index,
            }
        )
    document = {
        "tests": tests,
        "limitations": [
            "Tests were compiled from repository changes; the local model influenced candidate "
            "priority only, and its raw output is retained separately."
        ],
    }
    validate_plan_document(document)
    return PlanCompilation(
        document=document,
        mode="model-ranked-deterministic-change-compiler",
        candidates_total=len(candidates),
        raw_proposals_total=len(raw_proposals),
        model_aligned_candidates=aligned,
        selections=tuple(selections),
    )
