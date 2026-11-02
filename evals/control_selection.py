"""Versioned neutral-control selection and immutable run freezes; no transport."""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re
import subprocess

CONTROL_TEXT = "placebo.snapshot.txt"
CONTROL_METADATA = "control-selection.snapshot.json"
CONTROL_CORPUS = "control-corpus.snapshot.txt"
CONTROL_REGISTRY = "control-registry.snapshot.json"


class ControlError(ValueError):
    pass


def digest(value):
    return hashlib.sha256(value.encode() if isinstance(value, str) else value).hexdigest()


def validate_length(treatment, text):
    words = len(treatment.split())
    if not words:
        raise ControlError("A nonempty frozen treatment is required")
    difference = (len(text.split()) - words) / words
    if abs(difference) > 0.05:
        raise ControlError("Placebo and frozen treatment differ by more than five percent in words")
    return difference


@dataclass(frozen=True)
class Control:
    text: str
    metadata: dict
    corpus: bytes | None = None
    registry: bytes | None = None


def registry_entry(registry_bytes, treatment):
    try:
        registry = json.loads(registry_bytes)
        matches = [entry for entry in registry["controls"]
                   if entry["treatment_sha256"] == digest(treatment)]
    except (ValueError, KeyError, TypeError):
        raise ControlError("Invalid versioned neutral-control registry") from None
    if len(matches) != 1:
        raise ControlError("No unique versioned neutral control matches this treatment; author and freeze a new control version")
    return registry, matches[0]


def derive_control(registry_bytes, corpus, treatment):
    """Reproduce selected text and all metadata from the frozen raw sources."""
    registry, entry = registry_entry(registry_bytes, treatment)
    if digest(corpus) != entry["corpus_sha256"]:
        raise ControlError("Versioned neutral-control corpus hash mismatch")
    text = corpus.decode().strip()
    if entry["selection"] == "prefix_complete_sentence":
        words = len(treatment.split())
        if len(text.split()) < words:
            raise ControlError("Generic placebo corpus is shorter than the treatment")
        text = " ".join(text.split()[:words])
        if "." in text:
            text = text.rsplit(".", 1)[0] + "."
    elif entry["selection"] != "whole":
        raise ControlError("Unknown frozen control selection policy")
    difference = validate_length(treatment, text)
    metadata = dict(entry, protocol_version=registry["protocol_version"],
                    registry_path="evals/controls/index.json",
                    registry_sha256=digest(registry_bytes), control_sha256=digest(text),
                    treatment_words=len(treatment.split()), control_words=len(text.split()),
                    word_difference_fraction=difference)
    return Control(text, metadata, corpus, registry_bytes)


def select_current_control(root, treatment):
    root = Path(root).resolve()
    registry_path = root / "evals/controls/index.json"
    registry_bytes = registry_path.read_bytes()
    _, entry = registry_entry(registry_bytes, treatment)
    path = root / entry["corpus_path"]
    if path.is_symlink() or not path.resolve().is_relative_to(root / "evals/controls"):
        raise ControlError("Control corpus must be a contained regular file")
    return derive_control(registry_bytes, path.read_bytes(), treatment)


def freeze_control(folder, control):
    folder = Path(folder)
    inputs = {CONTROL_TEXT: control.text.encode(),
              CONTROL_METADATA: (json.dumps(control.metadata, sort_keys=True, indent=2) + "\n").encode()}
    if control.corpus is not None:
        inputs[CONTROL_CORPUS] = control.corpus
    if control.registry is not None:
        inputs[CONTROL_REGISTRY] = control.registry
    for name, data in inputs.items():
        path = folder / name
        if path.exists() and path.read_bytes() != data:
            raise ControlError("Frozen neutral-control input changed: " + name + "; select a fresh run ID")
    folder.mkdir(parents=True, exist_ok=True)
    for name, data in inputs.items():
        path = folder / name
        if not path.exists():
            path.write_bytes(data)


def read_frozen_control(folder, treatment, expected_metadata):
    folder = Path(folder)
    if not isinstance(expected_metadata, dict):
        raise ControlError("Historical execution requires a verifiable frozen neutral control; retained records remain unchanged")
    if not (folder / CONTROL_TEXT).is_file() or not (folder / CONTROL_METADATA).is_file():
        raise ControlError("Historical execution lacks its frozen neutral control; retained records remain unchanged")
    metadata = json.loads((folder / CONTROL_METADATA).read_text())
    text = (folder / CONTROL_TEXT).read_text()
    if metadata != expected_metadata:
        raise ControlError("Frozen neutral-control metadata differs from the recorded manifest")
    for name, key in ((CONTROL_CORPUS, "corpus_sha256"), (CONTROL_REGISTRY, "registry_sha256")):
        path = folder / name
        if not path.is_file() or digest(path.read_bytes()) != metadata.get(key):
            raise ControlError("Frozen neutral-control source bytes differ: " + name)
    if metadata.get("treatment_sha256") != digest(treatment):
        raise ControlError("Frozen neutral control belongs to another treatment version")
    if metadata.get("control_sha256") != digest(text):
        raise ControlError("Frozen neutral-control bytes differ from their recorded hash")
    difference = validate_length(treatment, text)
    if (metadata.get("treatment_words") != len(treatment.split()) or
            metadata.get("control_words") != len(text.split()) or
            metadata.get("word_difference_fraction") != difference):
        raise ControlError("Frozen neutral-control word-count metadata mismatch")
    derived = derive_control((folder / CONTROL_REGISTRY).read_bytes(),
                             (folder / CONTROL_CORPUS).read_bytes(), treatment)
    if derived.text != text or derived.metadata != metadata:
        raise ControlError("Frozen neutral control does not match corpus/registry selection")
    return derived



def committed_source_errors(root, source_hashes, commit):
    """Live preflight checks recorded inputs against Git and current bytes."""
    root = Path(root).resolve()
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40,64}", commit):
        return ["Selected inputs have no exact Git commit; commit them before live calls"]
    errors = []
    for relative, expected in source_hashes.items():
        path = root / relative
        if not path.resolve().is_relative_to(root):
            errors.append("Selected source path escapes repository: " + relative)
            continue
        result = subprocess.run(["git", "-C", str(root), "show", commit + ":" + relative],
                                capture_output=True, check=False)
        if result.returncode or digest(result.stdout) != expected:
            errors.append(relative + " differs from selected Git commit; commit inputs before live calls")
        if not path.is_file() or digest(path.read_bytes()) != expected:
            errors.append(relative + " changed after selection; start a fresh record")
    return errors
