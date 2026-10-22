"""Structural validation only: SQL expressions are never parsed or executed."""

import re

ACTIONS = ("NO ACTION", "RESTRICT", "CASCADE", "SET NULL", "SET DEFAULT")
METHODS = ("btree", "hash", "gist", "spgist", "gin", "brin")
IDENTITIES = ("NONE", "ALWAYS", "BY DEFAULT")
ORDERS = ("DEFAULT", "ASC", "DESC")
TYPES = ("text", "integer", "bigint", "smallint", "boolean", "numeric(12,2)",
         "varchar(255)", "uuid", "date", "timestamp", "timestamptz", "jsonb", "bytea", "text[]")


class ModelError(ValueError):
    pass


def identifier(value, label):
    if not isinstance(value, str) or not value.strip() or "\x00" in value:
        raise ModelError(f"{label}: escribe un nombre válido.")
    if len(value.encode("utf-8")) > 63:
        raise ModelError(f"{label}: PostgreSQL admite hasta 63 bytes UTF-8 por identificador.")


def eligible_keys(table):
    result = [k["columns"] for k in table["keys"]]
    result += [[e["column"] for e in idx["entries"]] for idx in table["indexes"]
               if idx["unique"] and not idx["predicate"].strip() and idx["entries"]
               and all(e["column"] and not e["expression"].strip() for e in idx["entries"])]
    return result


def validate(data, tables):
    """Validate an edited table against the proposed complete database snapshot."""
    identifier(data["name"], "Tabla")
    cols = {c["id"]: c for c in data["columns"]}
    if len(cols) != len(data["columns"]):
        raise ModelError("Hay identificadores de columna duplicados.")
    names = set()
    for col in cols.values():
        identifier(col["name"], "Columna")
        if col["name"] in names:
            raise ModelError(f"Columna repetida: {col['name']}.")
        names.add(col["name"])
        if not col["type"].strip() or "\x00" in col["type"]:
            raise ModelError(f"{col['name']}: falta el tipo PostgreSQL.")
        if col["identity"] not in IDENTITIES:
            raise ModelError("Identidad desconocida.")
        if col["identity"] != "NONE":
            if col["default"].strip():
                raise ModelError(f"{col['name']}: identidad y DEFAULT no pueden coexistir.")
            if canonical_type(col["type"]) not in ("smallint", "integer", "bigint"):
                raise ModelError(f"{col['name']}: la identidad requiere smallint, integer o bigint.")
            col["nullable"] = False
    names = set()
    index_names = set()
    ids = set(cols)
    for kind in ("keys", "foreign_keys", "checks", "indexes"):
        for row in data[kind]:
            identifier(row["name"], "Restricción/índice")
            namespace = index_names if kind == "indexes" else names
            if row["name"] in namespace:
                raise ModelError(f"Nombre de restricción/índice repetido: {row['name']}.")
            namespace.add(row["name"])
            if row["id"] in ids:
                raise ModelError("Hay identificadores duplicados en el editor.")
            ids.add(row["id"])
            for detail in row.get("pairs", row.get("entries", [])):
                if detail["id"] in ids:
                    raise ModelError("Hay identificadores de detalle duplicados en el editor.")
                ids.add(detail["id"])
    primary = [k for k in data["keys"] if k["kind"] == "PRIMARY"]
    if len(primary) > 1:
        raise ModelError("Una tabla solo puede tener una clave primaria.")

    def require_columns(selected, label):
        if not selected or len(selected) != len(set(selected)) or any(c not in cols for c in selected):
            raise ModelError(f"{label}: selecciona columnas existentes, sin repetir.")

    for key in data["keys"]:
        if key["kind"] not in ("PRIMARY", "UNIQUE"):
            raise ModelError("Tipo de clave desconocido.")
        require_columns(key["columns"], key["name"])
        if key["kind"] == "PRIMARY":
            for cid in key["columns"]:
                cols[cid]["nullable"] = False
            key["nulls_not_distinct"] = False
    for check in data["checks"]:
        if not check["expression"].strip():
            raise ModelError(f"{check['name']}: falta la expresión CHECK.")
    for idx in data["indexes"]:
        if idx["method"] not in METHODS or not idx["entries"]:
            raise ModelError(f"{idx['name']}: indica método y al menos un campo.")
        if idx["unique"] and idx["method"] != "btree":
            raise ModelError("Los índices UNIQUE requieren B-tree.")
        if idx["nulls_not_distinct"] and not idx["unique"]:
            raise ModelError("NULLS NOT DISTINCT requiere un índice UNIQUE.")
        if idx["method"] in ("hash", "spgist") and len(idx["entries"]) != 1:
            raise ModelError(f"{idx['method']}: admite un solo campo clave.")
        for entry in idx["entries"]:
            if bool(entry["column"]) == bool(entry["expression"].strip()):
                raise ModelError(f"{idx['name']}: cada campo debe ser columna o expresión.")
            if entry["column"] and entry["column"] not in cols:
                raise ModelError(f"{idx['name']}: una columna ya no existe.")
            if entry["order"] not in ORDERS or (entry["order"] != "DEFAULT" and idx["method"] != "btree"):
                raise ModelError("ASC/DESC solo se admiten con B-tree.")
        if idx["include"]:
            require_columns(idx["include"], "INCLUDE")
            if idx["method"] not in ("btree", "gist", "spgist"):
                raise ModelError("INCLUDE requiere B-tree, GiST o SP-GiST.")
            if set(idx["include"]) & {e["column"] for e in idx["entries"]}:
                raise ModelError("INCLUDE no debe repetir columnas clave del índice.")
    warnings = []
    for fk in data["foreign_keys"]:
        target = tables.get(fk["target"])
        if target is None:
            raise ModelError(f"{fk['name']}: la tabla destino ya no existe en esta base de datos.")
        if fk["on_delete"] not in ACTIONS or fk["on_update"] not in ACTIONS:
            raise ModelError(f"{fk['name']}: acción referencial desconocida.")
        local = [p["local"] for p in fk["pairs"]]
        remote = [p["remote"] for p in fk["pairs"]]
        require_columns(local, fk["name"])
        remote_cols = {c["id"]: c for c in target["columns"]}
        if len(remote) != len(set(remote)) or any(c not in remote_cols for c in remote):
            raise ModelError(f"{fk['name']}: revisa las columnas de destino.")
        if not any(len(k) == len(remote) and set(k) == set(remote) for k in eligible_keys(target)):
            raise ModelError(f"{fk['name']}: el destino debe ser PK, UNIQUE o un índice único completo de columnas.")
        for left, right in zip(local, remote):
            if canonical_type(cols[left]["type"]) != canonical_type(remote_cols[right]["type"]):
                warnings.append(f"{fk['name']}: verifica en PostgreSQL la compatibilidad de tipos de {cols[left]['name']}.")
        if "SET NULL" in (fk["on_delete"], fk["on_update"]) and any(not cols[c]["nullable"] for c in local):
            warnings.append(f"{fk['name']}: SET NULL puede fallar por NOT NULL.")
    return warnings


def canonical_type(text):
    value = re.sub(r"\s+", " ", text.strip().lower())
    return {"int": "integer", "int4": "integer", "int8": "bigint", "int2": "smallint",
            "bool": "boolean", "timestamp with time zone": "timestamptz"}.get(value, value)
