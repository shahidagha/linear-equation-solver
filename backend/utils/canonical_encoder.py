import json


def canonicalize_equation(eq_data: dict) -> str:
    """
    Convert equation JSON data into a canonical string.
    Ensures consistent ordering for hashing.
    """

    # Extract positions
    positions = eq_data.get("positions", {})

    # Extract terms
    term1 = eq_data.get("term1", {})
    term2 = eq_data.get("term2", {})
    constant = eq_data.get("constant", {})

    canonical = {
        "positions": {
            "term1": positions.get("term1"),
            "term2": positions.get("term2"),
            "equals": positions.get("equals"),
            "constant": positions.get("constant"),
        },
        "term1": term1,
        "term2": term2,
        "constant": constant,
    }

    # Convert to sorted JSON string
    return json.dumps(canonical, sort_keys=True)