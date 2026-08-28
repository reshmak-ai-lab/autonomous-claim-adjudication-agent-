
import json
import os
import re
import subprocess
import sys

import pandas as pd
import streamlit as st

from app.agent.workflows.claim_workflow import ClaimWorkflow


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Autonomous Claim Adjudication",
    layout="wide",
)

st.title("🏥 Autonomous Claim Adjudication & Fraud Detection")


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def flatten_dict(data, parent_key=""):
    """
    Flatten nested dictionaries/lists into Field/Value rows.

    Example:
        {
            "patient": {
                "name": "Amit"
            }
        }

    becomes:

        patient.name | Amit
    """
    rows = []

    if isinstance(data, dict):
        for key, value in data.items():
            field = f"{parent_key}.{key}" if parent_key else str(key)

            if isinstance(value, (dict, list)):
                rows.extend(flatten_dict(value, field))
            else:
                rows.append(
                    {
                        "Field": field,
                        "Value": value,
                    }
                )

    elif isinstance(data, list):
        if not data:
            rows.append(
                {
                    "Field": parent_key,
                    "Value": "[]",
                }
            )
        else:
            for index, value in enumerate(data):
                field = f"{parent_key}[{index}]"

                if isinstance(value, (dict, list)):
                    rows.extend(flatten_dict(value, field))
                else:
                    rows.append(
                        {
                            "Field": field,
                            "Value": value,
                        }
                    )

    else:
        rows.append(
            {
                "Field": parent_key,
                "Value": data,
            }
        )

    return rows


def json_to_table(data):
    """Convert JSON/dict/list data into a Streamlit dataframe."""
    rows = flatten_dict(data)

    if not rows:
        return pd.DataFrame(columns=["Field", "Value"])

    return pd.DataFrame(rows, columns=["Field", "Value"])


def section_table(data):
    """
    Convert workflow sections into a readable dataframe.
    """
    if isinstance(data, list) and data:
        if all(isinstance(item, dict) for item in data):
            return pd.json_normalize(data)

        return pd.DataFrame(
            [
                {
                    "Field": "Value",
                    "Value": item,
                }
                for item in data
            ]
        )

    if isinstance(data, dict):
        return json_to_table(data)

    return pd.DataFrame(
        [
            {
                "Field": "Value",
                "Value": data,
            }
        ]
    )


def first_present(mapping, *keys, default=None):
    """
    Return the first non-empty value found for the supplied keys.
    """
    if not isinstance(mapping, dict):
        return default

    for key in keys:
        value = mapping.get(key)

        if value not in (None, "", [], {}):
            return value

    return default


def parse_txt(text):
    """
    Convert simple TXT claim data into claim JSON.

    Example TXT:

        Claim ID: CLM001
        Diagnosis: Cancer
        Amount: 50000
    """

    fields = {}
    rows = []

    for line in text.splitlines():
        if ":" not in line:
            continue

        key, value = line.split(":", 1)

        key = key.strip()
        value = value.strip()

        fields[key.lower()] = value

        rows.append(
            {
                "Field": key,
                "Value": value,
            }
        )

    amount_text = re.sub(
        r"[^0-9.]",
        "",
        fields.get("amount", "0"),
    )

    try:
        amount = float(amount_text or 0)
    except ValueError:
        amount = 0.0

    claim = {
        "claim_id": fields.get(
            "claim id",
            "TXT_CLAIM",
        ),
        "diagnosis": {
            "name": fields.get("diagnosis"),
        },
        "financials": {
            "requested_amount": amount,
        },
    }

    return claim, rows


def run_test_suite(test_path):
    """
    Run pytest using the same Python interpreter that runs Streamlit.
    """
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-v",
                test_path,
            ],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
        )

        return result

    except Exception as exc:
        return None, str(exc)


def display_test_result(result, test_name):
    """
    Display pytest output in the Streamlit UI.
    """
    if isinstance(result, tuple):
        _, error = result

        st.error(
            f"❌ Unable to run {test_name}: {error}"
        )
        return

    if result.returncode == 0:
        st.success(
            f"✅ {test_name} completed successfully."
        )
    else:
        st.error(
            f"❌ {test_name} completed with failures. "
            f"Exit code: {result.returncode}"
        )

    if result.stdout:
        st.markdown("#### Test Output")
        st.code(
            result.stdout,
            language="text",
        )

    if result.stderr:
        st.markdown("#### Error Output")
        st.code(
            result.stderr,
            language="text",
        )


# ============================================================
# WORKFLOW
# ============================================================

@st.cache_resource
def get_workflow():
    return ClaimWorkflow()


workflow = get_workflow()


# ============================================================
# MAIN PANELS
# ============================================================

claim_panel, testing_panel = st.tabs(
    [
        "📋 Claim Adjudication",
        "🧪 Testing",
    ]
)


# ============================================================
# CLAIM ADJUDICATION PANEL
# ============================================================

with claim_panel:

    # ========================================================
    # UPLOAD CLAIM
    # ========================================================

    uploaded = st.file_uploader(
        "Upload Claim File",
        type=[
            "json",
            "txt",
        ],
        key="claim_file_uploader",
    )

    if uploaded:

        # ====================================================
        # READ CLAIM FILE
        # ====================================================

        try:

            if uploaded.name.lower().endswith(".json"):

                data = json.load(uploaded)

                txt_preview = None

            else:

                text = uploaded.read().decode(
                    "utf-8"
                )

                claim, txt_preview = parse_txt(
                    text
                )

                data = claim

        except Exception as exc:

            st.error(
                f"Unable to process claim file: {exc}"
            )

            st.stop()

        # ====================================================
        # MULTIPLE JSON CLAIMS
        # ====================================================

        if isinstance(data, list):

            st.warning(
                f"{len(data)} claims detected."
            )

            index = st.selectbox(
                "Select Claim",
                range(len(data)),
                format_func=lambda x: (
                    data[x].get(
                        "claim_id",
                        f"Claim {x + 1}",
                    )
                    if isinstance(data[x], dict)
                    else f"Claim {x + 1}"
                ),
            )

            claim = data[index]

        else:

            claim = data

        # ====================================================
        # VALIDATE CLAIM
        # ====================================================

        if not isinstance(claim, dict):

            st.error(
                "Invalid claim format. "
                "The uploaded claim must be a JSON object."
            )

            st.stop()

        # ====================================================
        # CLAIM INPUT
        # ====================================================

        st.header("📥 Claim Input")

        # ----------------------------------------------------
        # CLAIM SUMMARY
        # ----------------------------------------------------

        st.subheader("Claim Summary")

        summary = {
            "Claim ID": first_present(
                claim,
                "claim_id",
                "id",
                default="N/A",
            ),
            "Patient ID": first_present(
                claim,
                "patient_id",
                default="N/A",
            ),
            "Policy ID": first_present(
                claim,
                "policy_id",
                default="N/A",
            ),
            "Hospital ID": first_present(
                claim,
                "hospital_id",
                default="N/A",
            ),
            "Status": first_present(
                claim,
                "status",
                default="Submitted",
            ),
        }

        st.dataframe(
            pd.DataFrame([summary]),
            use_container_width=True,
            hide_index=True,
        )

        # ----------------------------------------------------
        # COMPLETE CLAIM DETAILS
        # ----------------------------------------------------

        st.subheader("📄 Complete Claim Details")

        claim_table = json_to_table(claim)

        if not claim_table.empty:

            st.dataframe(
                claim_table,
                use_container_width=True,
                hide_index=True,
                height=min(
                    650,
                    max(
                        180,
                        42 * len(claim_table),
                    ),
                ),
            )

        else:

            st.warning(
                "No claim fields were found."
            )

        # ----------------------------------------------------
        # TXT PREVIEW
        # ----------------------------------------------------

        if txt_preview:

            st.subheader(
                "📄 TXT Document Fields"
            )

            st.dataframe(
                pd.DataFrame(txt_preview),
                use_container_width=True,
                hide_index=True,
            )

        # ====================================================
        # EXECUTE ADJUDICATION
        # ====================================================

        if st.button(
            "🚀 Run Adjudication",
            key="run_adjudication",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Processing claim adjudication..."
            ):

                try:

                    result = workflow.run(
                        {
                            "claim": claim,
                        }
                    )

                except Exception as exc:

                    st.error(
                        f"Adjudication failed: {exc}"
                    )

                    st.exception(exc)

                    st.stop()

            st.success(
                "✅ Claim adjudication completed."
            )

            # =================================================
            # CLAIM OUTPUT
            # =================================================

            st.header("📤 Claim Output")

            # -------------------------------------------------
            # EXTRACT RESULTS
            # -------------------------------------------------

            if not isinstance(result, dict):
                result = {
                    "workflow_result": result,
                }

            adjudication_result = (
                result.get("adjudication_result")
                or result.get("adjudication")
                or {}
            )

            fraud_result = (
                result.get("fraud_result")
                or result.get("fraud_analysis")
                or result.get("fraud")
                or {}
            )

            guardrail_result = (
                result.get("guardrail_result")
                or result.get("guardrails")
                or result.get("guardrail_checks")
                or {}
            )

            # -------------------------------------------------
            # 1. FINAL DECISION
            # -------------------------------------------------

            st.subheader(
                "🎯 Final Decision"
            )

            decision = first_present(
                result,
                "final_decision",
                "decision",
                default=first_present(
                    adjudication_result,
                    "decision",
                    "final_decision",
                    default="NOT_AVAILABLE",
                ),
            )

            human_review = first_present(
                result,
                "human_review_required",
                "requires_human_review",
                default=first_present(
                    adjudication_result,
                    "human_review_required",
                    "requires_human_review",
                    default=False,
                ),
            )

            final_decision_table = pd.DataFrame(
                [
                    {
                        "Claim ID": claim.get(
                            "claim_id",
                            "N/A",
                        ),
                        "Final Decision": decision,
                        "Adjudication Decision": first_present(
                            adjudication_result,
                            "decision",
                            "adjudication_decision",
                            default="N/A",
                        ),
                        "Human Review Required": human_review,
                        "Status": first_present(
                            result,
                            "status",
                            default="Completed",
                        ),
                    }
                ]
            )

            st.dataframe(
                final_decision_table,
                use_container_width=True,
                hide_index=True,
            )

            # -------------------------------------------------
            # 2. FINANCIAL ADJUDICATION
            # -------------------------------------------------

            st.subheader(
                "💰 Financial Adjudication"
            )

            claim_financials = claim.get(
                "financials",
                {},
            )

            if not isinstance(
                claim_financials,
                dict,
            ):
                claim_financials = {}

            financial_summary = {
                "Claimed Amount": first_present(
                    adjudication_result,
                    "claimed_amount",
                    "requested_amount",
                    default=first_present(
                        claim_financials,
                        "claimed_amount",
                        "requested_amount",
                        "total_amount",
                        default="N/A",
                    ),
                ),
                "Eligible Amount": first_present(
                    adjudication_result,
                    "eligible_amount",
                    "approved_amount",
                    default="N/A",
                ),
                "Payable Amount": first_present(
                    adjudication_result,
                    "payable_amount",
                    "final_payable_amount",
                    "net_payable_amount",
                    default="N/A",
                ),
                "Deduction / Non-Payable": first_present(
                    adjudication_result,
                    "non_payable_amount",
                    "deduction_amount",
                    "total_deduction",
                    default="N/A",
                ),
                "Decision": first_present(
                    adjudication_result,
                    "decision",
                    default=decision,
                ),
                "Reason": first_present(
                    adjudication_result,
                    "reason",
                    "rationale",
                    "explanation",
                    default="N/A",
                ),
            }

            st.dataframe(
                pd.DataFrame(
                    [financial_summary]
                ),
                use_container_width=True,
                hide_index=True,
            )

            if adjudication_result:

                with st.expander(
                    "View all financial/adjudication details",
                    expanded=True,
                ):

                    st.dataframe(
                        json_to_table(
                            adjudication_result
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

            # -------------------------------------------------
            # 3. FRAUD ANALYSIS
            # -------------------------------------------------

            st.subheader(
                "🛡️ Fraud Analysis"
            )

            if fraud_result:

                fraud_summary = {
                    "Fraud Detected": first_present(
                        fraud_result,
                        "fraud_detected",
                        "is_fraud",
                        default="N/A",
                    ),
                    "Risk Level": first_present(
                        fraud_result,
                        "risk_level",
                        "risk",
                        default="N/A",
                    ),
                    "Fraud Score": first_present(
                        fraud_result,
                        "fraud_score",
                        "risk_score",
                        "score",
                        default="N/A",
                    ),
                    "Reason": first_present(
                        fraud_result,
                        "reason",
                        "rationale",
                        "explanation",
                        default="N/A",
                    ),
                }

                st.dataframe(
                    pd.DataFrame(
                        [fraud_summary]
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

                with st.expander(
                    "View all fraud-analysis details",
                    expanded=True,
                ):

                    st.dataframe(
                        json_to_table(
                            fraud_result
                        ),
                        use_container_width=True,
                        hide_index=True,
                    )

            else:

                st.warning(
                    "No fraud-analysis result was returned "
                    "by the workflow."
                )

            # -------------------------------------------------
            # 4. GUARDRAIL CHECKS
            # -------------------------------------------------

            st.subheader(
                "🔐 Guardrail Checks"
            )

            checks = []

            if isinstance(
                guardrail_result,
                dict,
            ):

                checks = (
                    guardrail_result.get(
                        "checks"
                    )
                    or guardrail_result.get(
                        "guardrail_checks"
                    )
                    or guardrail_result.get(
                        "results"
                    )
                    or []
                )

            if isinstance(
                checks,
                dict,
            ):

                checks = [
                    {
                        "Check": key,
                        "Result": value,
                    }
                    for key, value in checks.items()
                ]

            if checks:

                st.dataframe(
                    section_table(checks),
                    use_container_width=True,
                    hide_index=True,
                )

            elif guardrail_result:

                st.dataframe(
                    json_to_table(
                        guardrail_result
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.warning(
                    "No guardrail result was returned "
                    "by the workflow. The UI cannot report "
                    "guardrail status unless the workflow "
                    "returns it."
                )

            # -------------------------------------------------
            # 5. EXECUTION TRACE
            # -------------------------------------------------

            st.subheader(
                "🔎 Execution Trace"
            )

            execution_trace = (
                result.get(
                    "execution_trace"
                )
                or result.get(
                    "trace"
                )
                or result.get(
                    "steps"
                )
                or []
            )

            if execution_trace:

                st.dataframe(
                    section_table(
                        execution_trace
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

            else:

                st.info(
                    "No execution trace was returned "
                    "by the workflow."
                )

            # -------------------------------------------------
            # 6. COMPLETE WORKFLOW RESPONSE
            # -------------------------------------------------

            st.subheader(
                "📦 Complete Workflow Result"
            )

            with st.expander(
                "View complete raw adjudication response",
                expanded=False,
            ):

                st.json(result)


# ============================================================
# TESTING PANEL
# ============================================================

with testing_panel:

    st.header("🧪 Testing")

    st.write(
        "Run project test suites directly from the "
        "Streamlit application."
    )

    # --------------------------------------------------------
    # CREATE TESTING TABS
    # --------------------------------------------------------

    unit_tab, integration_tab, evaluation_tab = st.tabs(
        [
            "🔹 Unit Testing",
            "🔹 Integration Testing",
            "🔹 Evaluation Testing",
        ]
    )

    # ========================================================
    # UNIT TESTING
    # ========================================================

    with unit_tab:

        st.subheader(
            "🔹 Unit Testing"
        )

        st.write(
            "Unit tests validate individual modules such as "
            "extraction, privacy, rules, fraud detection, "
            "and utilities."
        )

        st.code(
            "pytest -v tests/unit",
            language="bash",
        )

        if st.button(
            "▶️ Run Unit Tests",
            key="run_unit_tests",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Running unit tests..."
            ):

                result = run_test_suite(
                    "tests/unit"
                )

            display_test_result(
                result,
                "Unit tests",
            )

    # ========================================================
    # INTEGRATION TESTING
    # ========================================================

    with integration_tab:

        st.subheader(
            "🔹 Integration Testing"
        )

        st.write(
            "Integration tests validate interactions between "
            "the agent, memory, MCP tools, RAG, and other services."
        )

        st.code(
            "pytest -v tests/integration",
            language="bash",
        )

        if st.button(
            "▶️ Run Integration Tests",
            key="run_integration_tests",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Running integration tests..."
            ):

                result = run_test_suite(
                    "tests/integration"
                )

            display_test_result(
                result,
                "Integration tests",
            )

    # ========================================================
    # EVALUATION TESTING
    # ========================================================

    with evaluation_tab:

        st.subheader(
            "🔹 Evaluation Testing"
        )

        st.write(
            "Evaluation tests validate adjudication accuracy, "
            "fraud detection, PII detection, and RAG accuracy."
        )

        st.code(
            "pytest -v tests/evaluation",
            language="bash",
        )

        if st.button(
            "▶️ Run Evaluation Tests",
            key="run_evaluation_tests",
            type="primary",
            use_container_width=True,
        ):

            with st.spinner(
                "Running evaluation tests..."
            ):

                result = run_test_suite(
                    "tests/evaluation"
                )

            display_test_result(
                result,
                "Evaluation tests",
            )

