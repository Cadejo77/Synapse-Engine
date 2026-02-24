from typing import List


def get_node_class(name: str):
    try:
        import nodes
        if hasattr(nodes, "NODE_CLASS_MAPPINGS") and name in nodes.NODE_CLASS_MAPPINGS:
            return nodes.NODE_CLASS_MAPPINGS[name]
        return getattr(nodes, name, None)
    except Exception:
        return None


def call_node(node_obj, **kwargs):
    fn_name = getattr(node_obj, "FUNCTION", None)
    if not fn_name:
        raise RuntimeError("Node object has no FUNCTION attribute")
    return getattr(node_obj, fn_name)(**kwargs)


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def join_nonempty(parts: List[str]) -> str:
    return ", ".join([p.strip(" ,") for p in parts if (p or "").strip()]).strip(" ,")
