"""Analytics engine for AI dashboard generation.

Provides 9 parameterized tools that the AI agent calls to explore project data.
All SQL is parameterized via SQLAlchemy text() with bind variables against Fila.data JSONB.
Virtual tables (v_ prefix) are stored as pandas DataFrames for join operations.
"""

from typing import Any, Union

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from models import Tabla, Columna


class AnalyticsEngine:
    """Session-scoped analytics tool executor.

    Each instance is tied to a single generation request.
    Virtual tables live in memory and are garbage-collected with the engine.
    """

    def __init__(self, db: Session, project_id: int):
        self.db = db
        self.project_id = project_id
        self._virtual_tables: dict[str, pd.DataFrame] = {}
        self._vtable_counter: int = 0

    # ── Internal helpers ──────────────────────────────────────────────

    def _is_virtual(self, table_id: Union[int, str]) -> bool:
        """Check if table_id refers to a virtual (in-memory) table."""
        return isinstance(table_id, str) and table_id.startswith("v_")

    def _get_virtual_table(self, table_id: str) -> pd.DataFrame | None:
        """Retrieve a virtual DataFrame by ID."""
        return self._virtual_tables.get(table_id)

    def _validate_table(self, table_id: int) -> Tabla | None:
        """Check that a real table belongs to this project.

        Returns the Tabla ORM object or None.
        """
        tabla = (
            self.db.query(Tabla)
            .filter(Tabla.id == table_id, Tabla.proyecto_id == self.project_id)
            .first()
        )
        return tabla

    def _get_column_type(self, table_id: int, column_name: str) -> str | None:
        """Get the inferred type of a column from the Columna table."""
        col = (
            self.db.query(Columna)
            .filter(Columna.tabla_id == table_id, Columna.nombre == column_name)
            .first()
        )
        return col.tipo if col else None

    def _get_virtual_column_type(self, df: pd.DataFrame, column_name: str) -> str:
        """Infer the type of a virtual table column from its DataFrame dtype."""
        if column_name not in df.columns:
            return "string"
        dtype = df[column_name].dtype
        if pd.api.types.is_datetime64_any_dtype(dtype):
            return "date"
        if pd.api.types.is_numeric_dtype(dtype):
            return "number"
        return "string"

    def _execute_sql(self, query: str, params: dict) -> list[dict]:
        """Execute parameterized SQL and return list of row dicts."""
        result = self.db.execute(text(query), params)
        rows = result.fetchall()
        columns = result.keys()
        return [dict(zip(columns, row)) for row in rows]

    def _load_table_as_dataframe(self, table_id: int) -> pd.DataFrame:
        """Load all rows of a real table into a pandas DataFrame."""
        rows = self._execute_sql(
            "SELECT data FROM fila WHERE tabla_id = :tid ORDER BY orden",
            {"tid": table_id},
        )
        if not rows:
            return pd.DataFrame()
        return pd.DataFrame([r["data"] for r in rows if r["data"] is not None])

    # ── Tool dispatch ─────────────────────────────────────────────────

    def execute_tool(self, tool_name: str, args: dict) -> dict:
        """Dispatch a tool call by name with the given arguments."""
        dispatch = {
            "get_columns": self.get_columns,
            "get_sample": self.get_sample,
            "count_rows": self.count_rows,
            "aggregate": self.aggregate,
            "group_by": self.group_by,
            "filter": self.filter,
            "distinct_values": self.distinct_values,
            "date_range": self.date_range,
            "join_tables": self.join_tables,
        }

        handler = dispatch.get(tool_name)
        if handler is None:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            return handler(**args)
        except TypeError as exc:
            return {"error": f"Invalid arguments for {tool_name}: {exc}"}
        except Exception as exc:
            return {"error": f"Tool execution error: {exc}"}

    # ── Tool 1: get_columns ───────────────────────────────────────────

    def get_columns(self, table_id: Union[int, str], **_kwargs) -> dict:
        """Return column names and types for a table."""
        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            columns = []
            for col_name in df.columns:
                columns.append({
                    "name": col_name,
                    "type": self._get_virtual_column_type(df, col_name),
                })
            return {"columns": columns}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        rows = self._execute_sql(
            "SELECT nombre, tipo FROM columna WHERE tabla_id = :tid",
            {"tid": table_id},
        )
        return {
            "columns": [{"name": r["nombre"], "type": r["tipo"]} for r in rows],
        }

    # ── Tool 2: get_sample ────────────────────────────────────────────

    def get_sample(self, table_id: Union[int, str], limit: int = 50, **_kwargs) -> dict:
        """Return up to `limit` sample rows from a table."""
        limit = max(1, min(limit, 200))

        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            sample = df.head(limit).where(pd.notna(df.head(limit)), None)
            rows = sample.to_dict(orient="records")
            # Convert NaN/None values to JSON-safe
            safe_rows = []
            for row in rows:
                safe_rows.append({
                    k: (None if pd.isna(v) else v)
                    for k, v in row.items()
                })
            return {"rows": safe_rows, "count": len(safe_rows)}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        rows = self._execute_sql(
            "SELECT data FROM fila WHERE tabla_id = :tid ORDER BY orden LIMIT :lim",
            {"tid": table_id, "lim": limit},
        )
        return {
            "rows": [r["data"] for r in rows if r["data"] is not None],
            "count": len(rows),
        }

    # ── Tool 3: count_rows ────────────────────────────────────────────

    def count_rows(self, table_id: Union[int, str], **_kwargs) -> dict:
        """Return the total number of rows in a table."""
        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            return {"count": len(df)}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        rows = self._execute_sql(
            "SELECT COUNT(*) AS cnt FROM fila WHERE tabla_id = :tid",
            {"tid": table_id},
        )
        return {"count": rows[0]["cnt"] if rows else 0}

    # ── Tool 4: aggregate ─────────────────────────────────────────────

    def aggregate(
        self,
        table_id: Union[int, str],
        column: str,
        operation: str,
        **_kwargs,
    ) -> dict:
        """Apply SUM|AVG|MAX|MIN|COUNT on a numeric column."""
        operation = operation.upper()
        valid_ops = {"SUM", "AVG", "MAX", "MIN", "COUNT"}
        if operation not in valid_ops:
            return {"error": f"Invalid operation '{operation}'. Must be one of {valid_ops}"}

        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in virtual table"}
            col_series = pd.to_numeric(df[column], errors="coerce")
            if operation == "SUM":
                value = float(col_series.sum()) if not col_series.isna().all() else None
            elif operation == "AVG":
                value = float(col_series.mean()) if not col_series.isna().all() else None
            elif operation == "MAX":
                value = float(col_series.max()) if not col_series.isna().all() else None
            elif operation == "MIN":
                value = float(col_series.min()) if not col_series.isna().all() else None
            else:  # COUNT
                value = int(col_series.notna().sum())
            return {"operation": operation, "column": column, "value": value}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        # Validate column type is numeric
        col_type = self._get_column_type(table_id, column)
        if col_type is None:
            return {"error": f"Column '{column}' not found in table {table_id}"}
        if col_type != "number" and operation != "COUNT":
            return {"error": f"Column '{column}' is not numeric (type: {col_type})"}

        sql_op = {
            "SUM": f"SUM((data->>:col)::numeric)",
            "AVG": f"AVG((data->>:col)::numeric)",
            "MAX": f"MAX((data->>:col)::numeric)",
            "MIN": f"MIN((data->>:col)::numeric)",
            "COUNT": f"COUNT((data->>:col)::numeric)",
        }[operation]

        query = f"SELECT {sql_op} AS result FROM fila WHERE tabla_id = :tid"
        rows = self._execute_sql(query, {"tid": table_id, "col": column})

        value = rows[0]["result"] if rows and rows[0]["result"] is not None else None
        if value is not None and operation != "COUNT":
            value = float(value)
        elif value is not None:
            value = int(value)

        return {"operation": operation, "column": column, "value": value}

    # ── Tool 5: group_by ──────────────────────────────────────────────

    def group_by(
        self,
        table_id: Union[int, str],
        group_column: str,
        agg_column: str,
        operation: str,
        **_kwargs,
    ) -> dict:
        """Group by categorical column, aggregate numeric column."""
        operation = operation.upper()
        valid_ops = {"SUM", "AVG", "MAX", "MIN", "COUNT"}
        if operation not in valid_ops:
            return {"error": f"Invalid operation '{operation}'. Must be one of {valid_ops}"}

        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            if group_column not in df.columns:
                return {"error": f"Group column '{group_column}' not found"}
            if agg_column not in df.columns:
                return {"error": f"Aggregate column '{agg_column}' not found"}

            pandas_op = operation.lower()
            if pandas_op == "avg":
                pandas_op = "mean"

            grouped = (
                df.groupby(group_column)[agg_column]
                .agg(pandas_op)
                .reset_index()
            )
            grouped.columns = ["group", "value"]
            grouped = grouped.sort_values("value", ascending=False).head(100)
            result = grouped.to_dict(orient="records")
            # Convert values to native Python types
            for item in result:
                item["group"] = str(item["group"])
                item["value"] = float(item["value"]) if item["value"] is not None else 0
            return {"groups": result}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        # Validate columns exist
        grp_type = self._get_column_type(table_id, group_column)
        if grp_type is None:
            return {"error": f"Group column '{group_column}' not found in table {table_id}"}
        agg_type = self._get_column_type(table_id, agg_column)
        if agg_type is None:
            return {"error": f"Aggregate column '{agg_column}' not found in table {table_id}"}
        if agg_type != "number" and operation != "COUNT":
            return {"error": f"Aggregate column '{agg_column}' is not numeric (type: {agg_type})"}

        sql_op = {
            "SUM": "SUM((data->>:agg)::numeric)",
            "AVG": "AVG((data->>:agg)::numeric)",
            "MAX": "MAX((data->>:agg)::numeric)",
            "MIN": "MIN((data->>:agg)::numeric)",
            "COUNT": "COUNT((data->>:agg)::numeric)",
        }[operation]

        query = f"""
            SELECT data->>:grp AS "group", {sql_op} AS "value"
            FROM fila
            WHERE tabla_id = :tid
            GROUP BY "group"
            ORDER BY "value" DESC
            LIMIT 100
        """
        rows = self._execute_sql(query, {"tid": table_id, "grp": group_column, "agg": agg_column})

        result = []
        for r in rows:
            val = r["value"]
            if val is not None:
                val = float(val) if operation != "COUNT" else int(val)
            result.append({"group": str(r["group"]), "value": val})

        return {"groups": result}

    # ── Tool 6: filter ────────────────────────────────────────────────

    def filter(
        self,
        table_id: Union[int, str],
        column: str,
        operator: str,
        value: Any,
        **_kwargs,
    ) -> dict:
        """Filter rows by a condition on a column."""
        valid_ops = {"eq", "neq", "gt", "gte", "lt", "lte", "contains", "starts_with"}
        if operator not in valid_ops:
            return {"error": f"Invalid operator '{operator}'. Must be one of {valid_ops}"}

        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in virtual table"}

            col = df[column]
            op_map = {
                "eq": lambda c, v: c == v,
                "neq": lambda c, v: c != v,
                "gt": lambda c, v: pd.to_numeric(c, errors="coerce") > float(v),
                "gte": lambda c, v: pd.to_numeric(c, errors="coerce") >= float(v),
                "lt": lambda c, v: pd.to_numeric(c, errors="coerce") < float(v),
                "lte": lambda c, v: pd.to_numeric(c, errors="coerce") <= float(v),
                "contains": lambda c, v: c.astype(str).str.contains(str(v), case=False, na=False),
                "starts_with": lambda c, v: c.astype(str).str.startswith(str(v), na=False),
            }
            mask = op_map[operator](col, value)
            filtered = df[mask]
            sample = filtered.head(20).where(pd.notna(filtered.head(20)), None)
            safe_rows = []
            for _, row in sample.iterrows():
                safe_rows.append({
                    k: (None if pd.isna(v) else v) for k, v in row.items()
                })
            return {"filtered_count": len(filtered), "sample": safe_rows}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        # Build parameterized SQL condition
        if operator == "eq":
            cond = "data->>:col = :val"
        elif operator == "neq":
            cond = "data->>:col != :val"
        elif operator == "gt":
            cond = "(data->>:col)::numeric > :val"
            value = float(value)
        elif operator == "gte":
            cond = "(data->>:col)::numeric >= :val"
            value = float(value)
        elif operator == "lt":
            cond = "(data->>:col)::numeric < :val"
            value = float(value)
        elif operator == "lte":
            cond = "(data->>:col)::numeric <= :val"
            value = float(value)
        elif operator == "contains":
            cond = "data->>:col ILIKE '%' || :val || '%'"
        elif operator == "starts_with":
            cond = "data->>:col ILIKE :val || '%'"
        else:
            return {"error": f"Unsupported operator: {operator}"}

        # Count query
        count_query = f"SELECT COUNT(*) AS cnt FROM fila WHERE tabla_id = :tid AND {cond}"
        count_rows = self._execute_sql(count_query, {"tid": table_id, "col": column, "val": value})
        filtered_count = count_rows[0]["cnt"] if count_rows else 0

        # Sample query
        sample_query = f"SELECT data FROM fila WHERE tabla_id = :tid AND {cond} ORDER BY orden LIMIT 20"
        sample_rows = self._execute_sql(sample_query, {"tid": table_id, "col": column, "val": value})

        return {
            "filtered_count": filtered_count,
            "sample": [r["data"] for r in sample_rows if r["data"] is not None],
        }

    # ── Tool 7: distinct_values ───────────────────────────────────────

    def distinct_values(
        self,
        table_id: Union[int, str],
        column: str,
        limit: int = 20,
        **_kwargs,
    ) -> dict:
        """Return unique values with frequency for a column."""
        limit = max(1, min(limit, 100))

        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in virtual table"}
            counts = df[column].value_counts().head(limit)
            result = [{"value": str(v), "count": int(c)} for v, c in counts.items()]
            return {"values": result}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        rows = self._execute_sql(
            """SELECT data->>:col AS val, COUNT(*) AS cnt
               FROM fila
               WHERE tabla_id = :tid
               GROUP BY val
               ORDER BY cnt DESC
               LIMIT :lim""",
            {"tid": table_id, "col": column, "lim": limit},
        )
        return {
            "values": [
                {"value": str(r["val"]) if r["val"] is not None else None, "count": r["cnt"]}
                for r in rows
            ],
        }

    # ── Tool 8: date_range ────────────────────────────────────────────

    def date_range(self, table_id: Union[int, str], column: str, **_kwargs) -> dict:
        """Return min/max dates and span in days for a date column."""
        if self._is_virtual(table_id):
            df = self._get_virtual_table(str(table_id))
            if df is None:
                return {"error": f"Virtual table {table_id} not found"}
            if column not in df.columns:
                return {"error": f"Column '{column}' not found in virtual table"}
            dates = pd.to_datetime(df[column], errors="coerce").dropna()
            if dates.empty:
                return {"error": f"No valid dates found in column '{column}'"}
            min_date = str(dates.min().date())
            max_date = str(dates.max().date())
            span = (dates.max() - dates.min()).days
            return {"min": min_date, "max": max_date, "span_days": span}

        table_id = int(table_id)
        tabla = self._validate_table(table_id)
        if tabla is None:
            return {"error": f"Table {table_id} not found in project"}

        # Validate column is date type
        col_type = self._get_column_type(table_id, column)
        if col_type is None:
            return {"error": f"Column '{column}' not found in table {table_id}"}
        if col_type != "date":
            return {"error": f"Column '{column}' is not a date column (type: {col_type})"}

        rows = self._execute_sql(
            "SELECT MIN(data->>:col) AS mn, MAX(data->>:col) AS mx FROM fila WHERE tabla_id = :tid",
            {"tid": table_id, "col": column},
        )

        if not rows or rows[0]["mn"] is None:
            return {"error": f"No date values found in column '{column}'"}

        min_date = str(rows[0]["mn"])
        max_date = str(rows[0]["mx"])

        # Calculate span in days
        try:
            min_dt = pd.to_datetime(min_date)
            max_dt = pd.to_datetime(max_date)
            span_days = (max_dt - min_dt).days
        except (ValueError, TypeError):
            span_days = 0

        return {"min": min_date, "max": max_date, "span_days": span_days}

    # ── Tool 9: join_tables ───────────────────────────────────────────

    def join_tables(
        self,
        left_table_id: Union[int, str],
        right_table_id: Union[int, str],
        left_column: str,
        right_column: str,
        join_type: str = "inner",
        **_kwargs,
    ) -> dict:
        """Join two tables via pandas merge and store as virtual table."""
        valid_joins = {"inner", "left", "right"}
        if join_type not in valid_joins:
            return {"error": f"Invalid join_type '{join_type}'. Must be one of {valid_joins}"}

        # Load left table
        if self._is_virtual(left_table_id):
            left_df = self._get_virtual_table(str(left_table_id))
            if left_df is None:
                return {"error": f"Virtual table {left_table_id} not found"}
        else:
            left_table_id = int(left_table_id)
            tabla = self._validate_table(left_table_id)
            if tabla is None:
                return {"error": f"Table {left_table_id} not found in project"}
            left_df = self._load_table_as_dataframe(left_table_id)

        # Load right table
        if self._is_virtual(right_table_id):
            right_df = self._get_virtual_table(str(right_table_id))
            if right_df is None:
                return {"error": f"Virtual table {right_table_id} not found"}
        else:
            right_table_id = int(right_table_id)
            tabla = self._validate_table(right_table_id)
            if tabla is None:
                return {"error": f"Table {right_table_id} not found in project"}
            right_df = self._load_table_as_dataframe(right_table_id)

        # Validate join columns exist
        if left_column not in left_df.columns:
            return {"error": f"Left column '{left_column}' not found in table"}
        if right_column not in right_df.columns:
            return {"error": f"Right column '{right_column}' not found in table"}

        # Handle duplicate columns (suffix conflicting names)
        left_cols = set(left_df.columns) - {left_column}
        right_cols = set(right_df.columns) - {right_column}
        overlap = left_cols & right_cols
        if overlap:
            right_df = right_df.rename(
                columns={c: f"{c}_right" for c in overlap}
            )

        # Perform merge
        try:
            merged = pd.merge(
                left_df,
                right_df,
                left_on=left_column,
                right_on=right_column,
                how=join_type,
            )
        except Exception as exc:
            return {"error": f"Join failed: {exc}"}

        if merged.empty:
            return {"error": "Join produced no results"}

        # Store virtual table
        self._vtable_counter += 1
        vtable_id = f"v_{self._vtable_counter}"
        self._virtual_tables[vtable_id] = merged

        # Build column info
        columns = []
        for col_name in merged.columns:
            columns.append({
                "name": col_name,
                "type": self._get_virtual_column_type(merged, col_name),
            })

        return {
            "virtual_table_id": vtable_id,
            "columns": columns,
            "row_count": len(merged),
        }
