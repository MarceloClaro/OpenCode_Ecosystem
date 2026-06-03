"""CTs para Data Consolidation Engine -- 4 testes criticos de consolidacao de dados."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from data_consolidation_engine import (
    ColumnSchema, SourceSchema, AggFunc, DataConsolidator,
)


def test_ct1_schema_registration():
    """CT-01: Registro de schemas e deteccao de colunas comuns."""
    consolidator = DataConsolidator()

    source_a = SourceSchema(source_name="CRM", columns=[
        ColumnSchema(name="client_id", dtype="str"),
        ColumnSchema(name="client_name", dtype="str"),
        ColumnSchema(name="revenue", dtype="float"),
    ])
    source_b = SourceSchema(source_name="ERP", columns=[
        ColumnSchema(name="client_id", dtype="str"),
        ColumnSchema(name="client_name", dtype="str"),
        ColumnSchema(name="tax_id", dtype="str"),
    ])

    assert consolidator.register_source(source_a) is True
    assert consolidator.register_source(source_b) is True
    assert consolidator.register_source(source_a) is False

    common = consolidator.common_columns
    assert "client_id" in common
    assert "client_name" in common
    assert "revenue" not in common
    assert "tax_id" not in common


def test_ct2_data_merging_with_key():
    """CT-02: Merge de datasets por chave com deteccao de duplicatas."""
    consolidator = DataConsolidator()

    crm_data = [
        {"account_id": "A001", "name": "Empresa Alpha", "revenue": 500000},
        {"account_id": "A002", "name": "Empresa Beta", "revenue": 300000},
    ]
    erp_data = [
        {"account_id": "A001", "name": "Empresa Alpha", "tax_id": "123456"},
        {"account_id": "A003", "name": "Empresa Gamma", "tax_id": "789012"},
    ]

    result = consolidator.merge(
        {"CRM": crm_data, "ERP": erp_data},
        key_column="account_id",
    )

    assert result.total_rows == 3
    assert result.source_counts["CRM"] == 2
    assert result.source_counts["ERP"] == 1
    assert result.has_warnings is True
    assert len(result.warnings) == 1


def test_ct3_aggregation_functions():
    """CT-03: Funcoes de agregacao sobre colunas numericas."""
    consolidator = DataConsolidator()

    rows = [
        {"sales_rep": "Alice", "amount": 15000},
        {"sales_rep": "Alice", "amount": 22000},
        {"sales_rep": "Bob", "amount": 18000},
        {"sales_rep": "Bob", "amount": 25000},
        {"sales_rep": "Charlie", "amount": None},
    ]

    assert consolidator.aggregate(rows, "amount", AggFunc.SUM) == 80000
    assert consolidator.aggregate(rows, "amount", AggFunc.AVG) == 20000.0
    assert consolidator.aggregate(rows, "amount", AggFunc.COUNT) == 4
    assert consolidator.aggregate(rows, "amount", AggFunc.MIN) == 15000
    assert consolidator.aggregate(rows, "amount", AggFunc.MAX) == 25000


def test_ct4_empty_and_edge_cases():
    """CT-04: Casos de borda -- datasets vazios, colunas inexistentes."""
    consolidator = DataConsolidator()

    result = consolidator.merge({}, key_column="id")
    assert result.total_rows == 0
    assert result.has_warnings is False

    result = consolidator.merge(
        {"A": [{"id": "1", "val": 10}], "B": []},
        key_column="id",
    )
    assert result.total_rows == 1

    assert consolidator.aggregate([], "amount", AggFunc.SUM) == 0
    assert consolidator.aggregate([{"x": 1}], "amount", AggFunc.AVG) == 0

    assert consolidator.common_columns == set()
    assert consolidator.registered_sources == []
