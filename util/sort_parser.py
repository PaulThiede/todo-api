from sqlalchemy.sql import asc, desc

def parse_sorting(sort: str, order: str, field_map: dict):
    if not sort:
        return []

    sort_fields = [s.strip() for s in sort.split(",")]
    order_fields = [o.strip().lower() for o in order.split(",")] if order else []

    if len(order_fields) != len(sort_fields):
        raise ValueError("Number of sort fields and order directives must match.")

    sorting = []
    for field, direction in zip(sort_fields, order_fields):
        column = field_map.get(field)
        if not column:
            raise ValueError(f"Invalid sort field: {field}. Correct ones: title, description, created_at. Separate by comma.")
        if direction == "asc":
            sorting.append(asc(column))
        elif direction == "desc":
            sorting.append(desc(column))
        else:
            raise ValueError(f"Invalid order directive: {direction}. Correct ones: asc, desc. Separate by comma.")

    return sorting
