"""Language-aware extraction of public behavioral surfaces."""

from __future__ import annotations

import ast
import json
import re

from proofedge.models import Contract
from proofedge.security import FileRecord, RepositorySnapshot

GO_FUNCTION = re.compile(
    r"^func\s+(?:\([^)]*\)\s*)?([A-Z][A-Za-z0-9_]*)\s*(\([^)]*\))", re.MULTILINE
)
GO_TYPE = re.compile(r"^type\s+([A-Z][A-Za-z0-9_]*)\s+(struct|interface)\b", re.MULTILINE)
JS_EXPORT = re.compile(
    r"^export\s+(?:default\s+)?(?:async\s+)?(?:function|class|const|let|var)\s+([A-Za-z_$][\w$]*)",
    re.MULTILINE,
)
INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all\s+)?(?:previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:the\s+)?(?:system|developer)\s+(?:prompt|message)", re.IGNORECASE),
    re.compile(r"(?:exfiltrate|upload|send)\s+(?:credentials|secrets|tokens)", re.IGNORECASE),
)


def _python_contracts(record: FileRecord) -> list[Contract]:
    try:
        tree = ast.parse(record.text, filename=record.path)
    except SyntaxError:
        return []
    contracts: list[Contract] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith(
            "_"
        ):
            positional = len(node.args.posonlyargs) + len(node.args.args)
            defaults = len(node.args.defaults)
            required = max(0, positional - defaults)
            signature = f"args={positional};required={required};kwonly={len(node.args.kwonlyargs)}"
            contracts.append(Contract("function", node.name, signature, record.path, node.lineno))
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            contracts.append(Contract("type", node.name, "class", record.path, node.lineno))
    return contracts


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _go_contracts(record: FileRecord) -> list[Contract]:
    contracts = [
        Contract(
            "function",
            match.group(1),
            re.sub(r"\s+", " ", match.group(2)),
            record.path,
            _line_number(record.text, match.start()),
        )
        for match in GO_FUNCTION.finditer(record.text)
    ]
    contracts.extend(
        Contract(
            "type",
            match.group(1),
            match.group(2),
            record.path,
            _line_number(record.text, match.start()),
        )
        for match in GO_TYPE.finditer(record.text)
    )
    return contracts


def _javascript_contracts(record: FileRecord) -> list[Contract]:
    return [
        Contract(
            "export",
            match.group(1),
            "exported",
            record.path,
            _line_number(record.text, match.start()),
        )
        for match in JS_EXPORT.finditer(record.text)
    ]


def _openapi_contracts(record: FileRecord) -> list[Contract]:
    if record.path.casefold().endswith(".json"):
        try:
            document = json.loads(record.text)
        except json.JSONDecodeError:
            return []
        if not isinstance(document, dict) or not ("openapi" in document or "swagger" in document):
            return []
        contracts: list[Contract] = []
        for route, operations in document.get("paths", {}).items():
            if not isinstance(operations, dict):
                continue
            for method, operation in operations.items():
                if method.casefold() not in {
                    "get",
                    "post",
                    "put",
                    "patch",
                    "delete",
                    "head",
                    "options",
                }:
                    continue
                responses = sorted(str(code) for code in (operation or {}).get("responses", {}))
                contracts.append(
                    Contract(
                        "http",
                        f"{method.upper()} {route}",
                        f"responses={','.join(responses)}",
                        record.path,
                        1,
                    )
                )
        return contracts
    return []


def extract_contracts(snapshot: RepositorySnapshot) -> tuple[Contract, ...]:
    contracts: list[Contract] = []
    for record in snapshot.files:
        if record.is_test:
            continue
        suffix = record.path.rsplit(".", 1)[-1].casefold() if "." in record.path else ""
        if suffix == "py":
            contracts.extend(_python_contracts(record))
        elif suffix == "go":
            contracts.extend(_go_contracts(record))
        elif suffix in {"js", "ts", "tsx"}:
            contracts.extend(_javascript_contracts(record))
        elif suffix == "json":
            contracts.extend(_openapi_contracts(record))
    return tuple(
        sorted(contracts, key=lambda item: (item.kind, item.name.casefold(), item.path, item.line))
    )


def find_prompt_injections(snapshot: RepositorySnapshot) -> tuple[tuple[FileRecord, int, str], ...]:
    matches: list[tuple[FileRecord, int, str]] = []
    for record in snapshot.files:
        for pattern in INJECTION_PATTERNS:
            for match in pattern.finditer(record.text):
                matches.append((record, _line_number(record.text, match.start()), match.group(0)))
    return tuple(matches)
