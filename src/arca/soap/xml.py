from __future__ import annotations

import re
import xml.etree.ElementTree as ET


_INT_RE = re.compile(r"^-?\d+$")
_FLOAT_RE = re.compile(r"^-?\d+\.\d+$")



def local_name(tag: str) -> str:
    if "}" in tag:
        return tag.rsplit("}", 1)[1]
    return tag



def parse_scalar(text: str) -> object:
    v = text.strip()
    if v == "":
        return ""
    low = v.lower()
    if low == "true":
        return True
    if low == "false":
        return False
    if _INT_RE.match(v):
        try:
            return int(v)
        except ValueError:
            return v
    if _FLOAT_RE.match(v):
        try:
            return float(v)
        except ValueError:
            return v
    return v



def element_to_data(elem: ET.Element) -> object:
    children = list(elem)
    if not children:
        return parse_scalar(elem.text or "")

    result: dict[str, object] = {}
    grouped: dict[str, list[object]] = {}

    for child in children:
        key = local_name(child.tag)
        grouped.setdefault(key, []).append(element_to_data(child))

    for key, values in grouped.items():
        if len(values) == 1:
            result[key] = values[0]
        else:
            result[key] = values

    return result



def find_child(node: ET.Element, local: str) -> ET.Element | None:
    for child in list(node):
        if local_name(child.tag) == local:
            return child
    return None



def find_text(node: ET.Element, local: str) -> str | None:
    hit = node.find(f".//{{*}}{local}")
    if hit is None or hit.text is None:
        return None
    value = hit.text.strip()
    return value if value else None
