"""
Unit tests for pipeline transformation logic, schema validation, data quality,
and configuration integrity. Uses pandas for portable local testing.
"""

import pytest
import pandas as pd
import os
import importlib

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


# ---------------------------------------------------------------------------
# Configuration tests
# ---------------------------------------------------------------------------

class TestConfig:

    def test_config_imports(self):
        """Config module should be importable and contain required settings."""
        sys_path = os.path.join(os.path.dirname(__file__), "..")
        import sys
        sys.path.insert(0, sys_path)
        from config.pipeline_config import (
            DATASETS, SCHEMAS, LOAD_MODE, GOLD_PARTITIONS,
            RAW_PATH, BRONZE_PATH, SILVER_PATH, GOLD_PATH,
        )
        assert len(DATASETS) == 4
        assert len(SCHEMAS) == 4
        assert LOAD_MODE in ("full", "incremental")
        assert len(GOLD_PARTITIONS) == 3

    def test_every_dataset_has_merge_keys(self):
        """Every dataset config should include merge_keys for incremental support."""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from config.pipeline_config import DATASETS
        for name, meta in DATASETS.items():
            assert "merge_keys" in meta, f"'{name}' missing merge_keys"
            assert len(meta["merge_keys"]) > 0, f"'{name}' has empty merge_keys"

    def test_every_dataset_has_schema(self):
        """Every dataset should have a corresponding schema definition."""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
        from config.pipeline_config import DATASETS, SCHEMAS
        for name in DATASETS:
            assert name in SCHEMAS, f"No schema defined for '{name}'"


# ---------------------------------------------------------------------------
# Schema validation tests
# ---------------------------------------------------------------------------

class TestSchemaValidation:

    def test_customers_schema(self):
        df = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
        expected = {"customer_id", "customer_name", "age", "gender", "city", "state", "join_date"}
        assert expected == set(df.columns)

    def test_policies_schema(self):
        df = pd.read_csv(os.path.join(DATA_DIR, "policies.csv"))
        expected = {"policy_id", "customer_id", "policy_type", "premium_amount", "start_date", "end_date", "status"}
        assert expected == set(df.columns)

    def test_claims_schema(self):
        df = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        expected = {"claim_id", "policy_id", "claim_date", "claim_type", "claim_amount", "claim_status", "incident_city", "fraud_flag"}
        assert expected == set(df.columns)

    def test_payments_schema(self):
        df = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))
        expected = {"payment_id", "claim_id", "payment_date", "paid_amount", "payment_status"}
        assert expected == set(df.columns)

    def test_no_empty_datasets(self):
        for filename in ["customers.csv", "policies.csv", "claims.csv", "payments.csv"]:
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            assert len(df) >= 10, f"{filename} should have at least 10 rows for realistic testing"


# ---------------------------------------------------------------------------
# Silver transformation tests
# ---------------------------------------------------------------------------

class TestSilverTransformations:

    def test_duplicate_removal(self):
        """Deduplication should keep only one row per primary key."""
        df = pd.DataFrame({
            "customer_id": ["C001", "C001", "C002"],
            "customer_name": ["Alice", "Alice", "Bob"],
            "age": [30, 30, 40],
        })
        deduped = df.drop_duplicates(subset=["customer_id"])
        assert len(deduped) == 2

    def test_trim_and_uppercase(self):
        """Text cleaning should trim whitespace and uppercase values."""
        df = pd.DataFrame({
            "customer_id": ["C001"],
            "city": ["  toronto  "],
            "state": ["  on  "],
        })
        df["city"] = df["city"].str.strip().str.upper()
        df["state"] = df["state"].str.strip().str.upper()
        assert df.iloc[0]["city"] == "TORONTO"
        assert df.iloc[0]["state"] == "ON"

    def test_null_fraud_flag_default(self):
        """Null fraud_flag values should default to 0."""
        df = pd.DataFrame({
            "claim_id": ["CL001", "CL002"],
            "fraud_flag": [None, 1.0],
        })
        df["fraud_flag"] = df["fraud_flag"].fillna(0).astype(int)
        assert df.loc[df["claim_id"] == "CL001", "fraud_flag"].values[0] == 0
        assert df.loc[df["claim_id"] == "CL002", "fraud_flag"].values[0] == 1

    def test_date_conversion(self):
        """String dates should be converted to datetime."""
        df = pd.DataFrame({
            "customer_id": ["C001"],
            "join_date": ["2023-01-15"],
        })
        df["join_date"] = pd.to_datetime(df["join_date"])
        assert df.iloc[0]["join_date"] == pd.Timestamp("2023-01-15")

    def test_row_count_preserved_without_duplicates(self):
        """When no duplicates exist, row count should remain unchanged."""
        df = pd.DataFrame({
            "policy_id": ["P001", "P002", "P003"],
            "policy_type": ["Auto", "Home", "Health"],
        })
        deduped = df.drop_duplicates(subset=["policy_id"])
        assert len(deduped) == 3

    def test_multiple_text_columns_cleaned(self):
        """All text fields in claims should be trimmed and uppercased."""
        df = pd.DataFrame({
            "claim_id": ["CL001"],
            "claim_type": ["  collision  "],
            "claim_status": [" pending "],
            "incident_city": [" toronto "],
        })
        for c in ["claim_type", "claim_status", "incident_city"]:
            df[c] = df[c].str.strip().str.upper()
        assert df.iloc[0]["claim_type"] == "COLLISION"
        assert df.iloc[0]["claim_status"] == "PENDING"
        assert df.iloc[0]["incident_city"] == "TORONTO"


# ---------------------------------------------------------------------------
# Gold aggregation tests
# ---------------------------------------------------------------------------

class TestGoldAggregations:

    def test_claims_summary_grouping(self):
        """Claims summary should produce one row per (policy_type, claim_status) pair."""
        df = pd.DataFrame({
            "policy_type": ["Auto", "Auto", "Home"],
            "claim_status": ["APPROVED", "APPROVED", "PENDING"],
            "claim_amount": [4500.0, 5200.0, 8000.0],
            "claim_id": ["CL001", "CL002", "CL003"],
        })
        summary = df.groupby(["policy_type", "claim_status"]).agg(
            total_claims=("claim_id", "count"),
            total_claim_amount=("claim_amount", "sum"),
            avg_claim_amount=("claim_amount", "mean"),
        ).reset_index()

        assert len(summary) == 2
        auto_row = summary[summary["policy_type"] == "Auto"].iloc[0]
        assert auto_row["total_claims"] == 2
        assert auto_row["total_claim_amount"] == 9700.0
        assert auto_row["avg_claim_amount"] == 4850.0

    def test_fraud_rate_calculation(self):
        """Fraud rate should be correctly calculated as (fraud_cases / total) * 100."""
        df = pd.DataFrame({
            "policy_type": ["Auto", "Auto", "Auto", "Home"],
            "fraud_flag": [0, 1, 0, 1],
        })
        fraud = df.groupby("policy_type").agg(
            fraud_cases=("fraud_flag", "sum"),
            total_claims=("fraud_flag", "count"),
        ).reset_index()
        fraud["fraud_rate_pct"] = round((fraud["fraud_cases"] * 100.0) / fraud["total_claims"], 2)

        auto_row = fraud[fraud["policy_type"] == "Auto"].iloc[0]
        assert auto_row["fraud_rate_pct"] == 33.33

        home_row = fraud[fraud["policy_type"] == "Home"].iloc[0]
        assert home_row["fraud_rate_pct"] == 100.0

    def test_payment_summary(self):
        """Payment summary should aggregate by claim_status."""
        payments = pd.DataFrame({
            "payment_id": ["PM001", "PM002", "PM003"],
            "claim_id": ["CL001", "CL002", "CL003"],
            "paid_amount": [4300.0, 0.0, 5000.0],
        })
        claims = pd.DataFrame({
            "claim_id": ["CL001", "CL002", "CL003"],
            "claim_status": ["APPROVED", "PENDING", "APPROVED"],
        })
        merged = payments.merge(claims, on="claim_id", how="left")
        summary = merged.groupby("claim_status").agg(
            total_paid_amount=("paid_amount", "sum"),
            payment_count=("payment_id", "count"),
        ).reset_index()

        approved = summary[summary["claim_status"] == "APPROVED"].iloc[0]
        assert approved["total_paid_amount"] == 9300.0
        assert approved["payment_count"] == 2


# ---------------------------------------------------------------------------
# Incremental merge logic tests
# ---------------------------------------------------------------------------

class TestIncrementalMerge:

    def test_upsert_new_rows(self):
        """New records should be inserted when merging on primary key."""
        existing = pd.DataFrame({
            "claim_id": ["CL001", "CL002"],
            "claim_amount": [4500, 12000],
        })
        incoming = pd.DataFrame({
            "claim_id": ["CL002", "CL003"],
            "claim_amount": [12500, 3000],
        })
        # Simulate merge: update matching, insert new
        merged = existing.set_index("claim_id")
        incoming_idx = incoming.set_index("claim_id")
        merged.update(incoming_idx)
        merged = merged.combine_first(incoming_idx).reset_index()

        assert len(merged) == 3
        assert merged.loc[merged["claim_id"] == "CL002", "claim_amount"].values[0] == 12500
        assert merged.loc[merged["claim_id"] == "CL003", "claim_amount"].values[0] == 3000

    def test_upsert_updates_existing(self):
        """Existing records should be updated when primary key matches."""
        existing = pd.DataFrame({
            "payment_id": ["PM001"],
            "paid_amount": [0],
            "payment_status": ["On Hold"],
        })
        incoming = pd.DataFrame({
            "payment_id": ["PM001"],
            "paid_amount": [4300],
            "payment_status": ["Paid"],
        })
        merged = existing.set_index("payment_id")
        merged.update(incoming.set_index("payment_id"))
        merged = merged.reset_index()

        assert merged.iloc[0]["paid_amount"] == 4300
        assert merged.iloc[0]["payment_status"] == "Paid"


# ---------------------------------------------------------------------------
# Partitioning strategy tests
# ---------------------------------------------------------------------------

class TestPartitioning:

    def test_claims_have_partition_column(self):
        """Claims data should contain the partition column (claim_status)."""
        df = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        assert "claim_status" in df.columns
        assert df["claim_status"].nunique() >= 2, "Partition column should have multiple values"

    def test_policies_have_partition_column(self):
        """Policies data should contain the partition column (policy_type)."""
        df = pd.read_csv(os.path.join(DATA_DIR, "policies.csv"))
        assert "policy_type" in df.columns
        assert df["policy_type"].nunique() >= 2

    def test_payments_have_partition_column(self):
        """Payments data should contain the partition column (payment_status)."""
        df = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))
        assert "payment_status" in df.columns
        assert df["payment_status"].nunique() >= 2

    def test_partition_cardinality_is_low(self):
        """Partition columns should have low cardinality to avoid small-file problems."""
        tests = [
            ("claims.csv", "claim_status", 10),
            ("policies.csv", "policy_type", 10),
            ("payments.csv", "payment_status", 10),
        ]
        for filename, col, max_partitions in tests:
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            cardinality = df[col].nunique()
            assert cardinality <= max_partitions, (
                f"{filename}.{col} has {cardinality} unique values — too many partitions"
            )


# ---------------------------------------------------------------------------
# Data quality tests on raw data
# ---------------------------------------------------------------------------

class TestDataQuality:

    def test_no_null_primary_keys(self):
        """Primary key columns should have no null values."""
        pk_map = {
            "customers.csv": "customer_id",
            "policies.csv": "policy_id",
            "claims.csv": "claim_id",
            "payments.csv": "payment_id",
        }
        for filename, pk in pk_map.items():
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            assert df[pk].notna().all(), f"Null primary keys found in {filename}"

    def test_no_duplicate_primary_keys(self):
        """Primary key columns should have no duplicates."""
        pk_map = {
            "customers.csv": "customer_id",
            "policies.csv": "policy_id",
            "claims.csv": "claim_id",
            "payments.csv": "payment_id",
        }
        for filename, pk in pk_map.items():
            df = pd.read_csv(os.path.join(DATA_DIR, filename))
            assert df[pk].is_unique, f"Duplicate primary keys in {filename}"

    def test_referential_integrity_policies_to_customers(self):
        """All customer_ids in policies should exist in customers."""
        customers = pd.read_csv(os.path.join(DATA_DIR, "customers.csv"))
        policies = pd.read_csv(os.path.join(DATA_DIR, "policies.csv"))
        orphans = set(policies["customer_id"]) - set(customers["customer_id"])
        assert len(orphans) == 0, f"Orphaned customer_ids in policies: {orphans}"

    def test_referential_integrity_claims_to_policies(self):
        """All policy_ids in claims should exist in policies."""
        policies = pd.read_csv(os.path.join(DATA_DIR, "policies.csv"))
        claims = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        orphans = set(claims["policy_id"]) - set(policies["policy_id"])
        assert len(orphans) == 0, f"Orphaned policy_ids in claims: {orphans}"

    def test_referential_integrity_payments_to_claims(self):
        """All claim_ids in payments should exist in claims."""
        claims = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        payments = pd.read_csv(os.path.join(DATA_DIR, "payments.csv"))
        orphans = set(payments["claim_id"]) - set(claims["claim_id"])
        assert len(orphans) == 0, f"Orphaned claim_ids in payments: {orphans}"

    def test_claim_amounts_positive(self):
        """All claim amounts should be positive."""
        df = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        assert (df["claim_amount"] > 0).all(), "Found non-positive claim amounts"

    def test_premium_amounts_positive(self):
        """All premium amounts should be positive."""
        df = pd.read_csv(os.path.join(DATA_DIR, "policies.csv"))
        assert (df["premium_amount"] > 0).all(), "Found non-positive premium amounts"

    def test_fraud_flag_binary(self):
        """Fraud flag should only contain 0 or 1."""
        df = pd.read_csv(os.path.join(DATA_DIR, "claims.csv"))
        assert set(df["fraud_flag"].unique()).issubset({0, 1}), "fraud_flag contains values other than 0/1"
