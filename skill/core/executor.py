import json
import os
import re
import unicodedata
from collections import Counter
from typing import Dict, List, Optional, Tuple

from .types import SkillPlan

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "from", "has",
    "have", "in", "into", "is", "it", "its", "of", "on", "or", "that", "the", "their",
    "they", "this", "to", "was", "were", "will", "with", "you", "your",
}

_DEFAULT_CATEGORIES = [
    ("user-value", "User Value"),
    ("experience", "Experience"),
    ("capabilities", "Core Capabilities"),
    ("platform", "Platform Services"),
    ("infrastructure", "Infrastructure"),
]

_DEFAULT_ITEMS = {
    "user-value": ["Outcomes", "Self-Service", "Trust"],
    "experience": ["UI Portal", "API Access", "Notifications"],
    "capabilities": ["Core Processing", "Policy Engine", "Workflow Automation"],
    "platform": ["Monitoring", "Identity", "Orchestration"],
    "infrastructure": ["Compute", "Storage", "Networking"],
}


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_text.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")
    return slug or "item"


def _unique_id(base: str, used: set) -> str:
    slug = _slugify(base)
    if slug not in used:
        used.add(slug)
        return slug
    i = 2
    while f"{slug}-{i}" in used:
        i += 1
    unique = f"{slug}-{i}"
    used.add(unique)
    return unique


def _extract_keywords(text: str, limit: int = 24) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9]{2,}", text)
    counts = Counter()
    for word in words:
        lowered = word.lower()
        if lowered in _STOPWORDS:
            continue
        counts[lowered] += 1
    if not counts:
        return []
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [word for word, _ in ranked[:limit]]


def _first_paragraph(text: str) -> str:
    for chunk in re.split(r"\n\s*\n", text):
        lines = []
        for line in chunk.splitlines():
            line = re.sub(r"^\s*#+\s+", "", line).strip()
            if line:
                lines.append(line)
        if lines:
            cleaned = " ".join(" ".join(lines).split())
            if cleaned:
                return cleaned
    return ""


def _extract_outline(lines: List[str]) -> List[Tuple[str, List[str]]]:
    heading_re = re.compile(r"^\s*(#{1,6})\s+(.+?)\s*$")
    headings: List[Tuple[int, int, str]] = []
    for idx, line in enumerate(lines):
        match = heading_re.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append((idx, level, title))
    if not headings:
        return []

    counts = Counter(level for _, level, _ in headings)
    category_level: Optional[int] = None
    if counts.get(1, 0) >= 3:
        category_level = 1
    elif counts.get(1, 0) == 1 and counts.get(2, 0) >= 3:
        category_level = 2
    elif counts.get(2, 0) >= 3:
        category_level = 2
    elif counts.get(3, 0) >= 3:
        category_level = 3

    if category_level is None:
        return []

    categories: List[Tuple[str, List[str]]] = []
    for idx, (line_no, level, title) in enumerate(headings):
        if level != category_level:
            continue
        next_line = len(lines)
        for other_line, other_level, _ in headings:
            if other_line > line_no and other_level <= category_level:
                next_line = other_line
                break
        items = [
            txt
            for (ln, lvl, txt) in headings
            if line_no < ln < next_line and lvl == category_level + 1
        ]
        if len(items) < 2:
            for line in lines[line_no + 1 : next_line]:
                match = re.match(r"\s*[-*+]\s+(.+)", line)
                if match:
                    items.append(match.group(1).strip())
        categories.append((title, items))
    return categories


def _title_from_content(lines: List[str]) -> Optional[str]:
    for line in lines:
        match = re.match(r"^\s*#\s+(.+)", line)
        if match:
            return match.group(1).strip()
    for line in lines:
        cleaned = line.strip()
        if cleaned:
            return cleaned[:80]
    return None


def _fallback_abstract(title_hint: str) -> str:
    lowered = title_hint.lower()
    return (
        f"Users want reliable {lowered} outcomes delivered through clear experiences, "
        "supported by core capabilities, data services, and dependable infrastructure."
    )


def _build_items(
    item_titles: List[str],
    keywords: List[str],
    used_ids: set,
    used_words: set,
    category_title: str,
    target: Optional[int] = None,
    stage: Optional[int] = None,
) -> List[Dict[str, object]]:
    items: List[Dict[str, object]] = []
    base_target = len(item_titles) if item_titles else 3
    target_count = min(6, max(2, target or base_target))

    for title in item_titles[:target_count]:
        name = title.strip()
        if not name:
            continue
        item_id = _unique_id(name, used_ids)
        items.append({"id": item_id, "name": name})
        used_words.add(_slugify(name))

    keyword_iter = iter(keywords)
    while len(items) < target_count:
        try:
            keyword = next(keyword_iter)
        except StopIteration:
            keyword = None
        if keyword:
            if keyword in used_words:
                continue
            name = keyword.replace("-", " ").title()
            item_id = _unique_id(name, used_ids)
            items.append({"id": item_id, "name": name})
            used_words.add(keyword)
            continue
        break

    if len(items) < target_count:
        fallbacks = _DEFAULT_ITEMS.get(_slugify(category_title), [])
        for fallback in fallbacks:
            if len(items) >= target_count:
                break
            item_id = _unique_id(fallback, used_ids)
            items.append({"id": item_id, "name": fallback})

    if len(items) < target_count:
        while len(items) < target_count:
            fallback_name = f"{category_title} Support {len(items) + 1}"
            item_id = _unique_id(fallback_name, used_ids)
            items.append({"id": item_id, "name": fallback_name})

    if stage is not None:
        for item in items:
            item["stage"] = stage

    return items


def _assign_deps(categories: List[Dict[str, object]]) -> None:
    for idx, category in enumerate(categories):
        items = category["items"]
        if idx >= len(categories) - 1:
            for item in items:
                item["deps"] = []
            continue
        next_items = categories[idx + 1]["items"]
        next_ids = [item["id"] for item in next_items[:2]]
        for item in items:
            item["deps"] = list(next_ids)


def _generate_model(text: str, title_hint: str, want_wardley: bool) -> Dict[str, object]:
    lines = text.splitlines()
    outline = _extract_outline(lines)
    keywords = _extract_keywords(text)
    summary = _first_paragraph(text)
    if not summary or len(summary) < 40:
        summary = _fallback_abstract(title_hint)

    used_category_ids: set = set()
    used_item_ids: set = set()
    used_words: set = set()

    categories: List[Dict[str, object]] = []
    if outline and len(outline) >= 3:
        for title, item_titles in outline[:6]:
            category_id = _unique_id(title, used_category_ids)
            stage = None
            if want_wardley:
                stage = 1
            items = _build_items(
                item_titles,
                keywords,
                used_item_ids,
                used_words,
                title,
                stage=stage,
            )
            categories.append({"id": category_id, "title": title, "items": items})
    else:
        for idx, (category_id, category_title) in enumerate(_DEFAULT_CATEGORIES):
            used_category_ids.add(category_id)
            stage = None
            if want_wardley:
                stage = 1
            items = _build_items(
                _DEFAULT_ITEMS.get(category_id, []),
                keywords,
                used_item_ids,
                used_words,
                category_title,
                stage=stage,
            )
            categories.append(
                {"id": category_id, "title": category_title, "items": items}
            )

    if want_wardley and categories:
        for idx, category in enumerate(categories):
            stage = 1 + round((idx / max(1, len(categories) - 1)) * 3)
            stage = max(1, min(stage, 4))
            for item in category["items"]:
                item["stage"] = stage

    _assign_deps(categories)

    return {
        "id": _slugify(title_hint),
        "title": f"{title_hint} Blockscape",
        "abstract": summary,
        "categories": categories,
    }


def execute(plan: SkillPlan) -> str:
    source_text = plan.user_text
    title_hint = "Blockscape Map"
    if plan.file_path:
        with open(plan.file_path, "r", encoding="utf-8", errors="ignore") as handle:
            source_text = handle.read()
        title_hint = os.path.splitext(os.path.basename(plan.file_path))[0].replace("_", " ").replace("-", " ").title()
    content_lines = source_text.splitlines()
    detected_title = _title_from_content(content_lines)
    if detected_title:
        title_hint = detected_title

    if plan.want_series:
        models: List[Dict[str, object]] = []
        for label in ["Current", "Target"]:
            model = _generate_model(source_text, title_hint, plan.want_wardley)
            model_id = f"{model['id']}-{_slugify(label)}"
            model["id"] = model_id
            model["title"] = f"{title_hint} Blockscape ({label})"
            if label == "Target":
                model["abstract"] = (
                    model["abstract"].rstrip(".")
                    + " with a focus on future-state enablement."
                )
            models.append(model)
        return json.dumps(models, indent=2, ensure_ascii=True)

    model = _generate_model(source_text, title_hint, plan.want_wardley)
    return json.dumps(model, indent=2, ensure_ascii=True)
