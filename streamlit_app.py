import streamlit as st
import json
import pandas as pd
import re
import subprocess

from app.agent.workflows.claim_workflow import ClaimWorkflow


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Autonomous Claim Adjudication",
    layout="wide"
)

st.title(
    "🏥 Autonomous Claim Adjudication & Fraud Detection"
)


# ============================================================
# MAIN PANELS
# ============================================================

claim_panel, testing_panel = st.tabs(
    [
        "📋 Claim Adjudication",
        "🧪 Testing"
    ]
)


# ============================================================
# WORKFLOW
# ============================================================

@st.cache_resource
def get_workflow():

    return ClaimWorkflow()


workflow = get_workflow()


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def dict_to_table(data):

    if isinstance(data, dict):

        return pd.DataFrame(
            [
                data
            ]
        )

    elif isinstance(data, list):

        return pd.DataFrame(
            data
        )

    else:

        return pd.DataFrame()


def parse_txt(text):

    """
    Converts:

    Claim ID: CLM001
    Diagnosis: Cancer
    Amount: 50000

    into claim JSON.
    """

    fields = {}

    rows = []

    for line in text.splitlines():

        if ":" not in line:
            continue

        key, value = line.split(
            ":",
            1
        )

        key = key.strip()

        value = value.strip()

        fields[key.lower()] = value

        rows.append(
            {
                "Field": key,
                "Value": value
            }
        )

    amount_text = re.sub(
        r"[^0-9.]",
        "",
        fields.get(
            "amount",
            "0"
        )
    )

    try:
        amount = float(amount_text or 0)
    except ValueError:
        amount = 0.0

    claim = {

        "claim_id":
            fields.get(
                "claim id",
                "TXT_CLAIM"
            ),

        "diagnosis":
        {
            "name":
                fields.get(
                    "diagnosis"
                )
        },

        "financials":
        {
            "requested_amount": amount
        }
    }

    return claim, rows


# ============================================================
# CLAIM ADJUDICATION PANEL
# ============================================================

with claim_panel:

    # ========================================================
    # UPLOAD
    # ========================================================

    uploaded = st.file_uploader(

        "Upload Claim File",

        type=[
            "json",
            "txt"
        ]

    )

    if uploaded:

        try:

            # ------------------------------------------------
            # JSON
            # ------------------------------------------------

            if uploaded.name.lower().endswith(
                ".json"
            ):

                data = json.load(
                    uploaded
                )

                txt_preview = None

            # ------------------------------------------------
            # TXT
            # ------------------------------------------------

            else:

                text = uploaded.read().decode(
                    "utf-8"
                )

                claim, txt_preview = parse_txt(
                    text
                )

                data = claim

        except Exception as e:

            st.error(
                f"Unable to process claim file: {e}"
            )

            st.stop()


        # ====================================================
        # MULTIPLE JSON CLAIMS
        # ====================================================

        if isinstance(
            data,
            list
        ):

            st.warning(
                f"{len(data)} claims detected"
            )

            index = st.selectbox(

                "Select Claim",

                range(
                    len(data)
                ),

                format_func=lambda x:
                    data[x].get(
                        "claim_id",
                        f"Claim {x + 1}"
                    )

            )

            claim = data[index]

        else:

            claim = data


        # ====================================================
        # VALIDATE CLAIM
        # ====================================================

        if not isinstance(
            claim,
            dict
        ):

            st.error(
                "Invalid claim format"
            )

            st.stop()


        # ====================================================
        # INPUT TABLES
        # ====================================================

        st.header(
            "📥 Claim Input"
        )


        # ----------------------------------------------------
        # Claim Summary
        # ----------------------------------------------------

        st.subheader(
            "Claim Summary"
        )

        st.dataframe(

            dict_to_table(
                {
                    "Claim ID":
                        claim.get(
                            "claim_id"
                        ),

                    "Status":
                        claim.get(
                            "status"
                        )
                }
            ),

            use_container_width=True

        )


        # ----------------------------------------------------
        # TXT Preview
        # ----------------------------------------------------

        if txt_preview:

            st.subheader(
                "TXT Document Fields"
            )

            st.dataframe(

                pd.DataFrame(
                    txt_preview
                ),

                use_container_width=True

            )


        # ----------------------------------------------------
        # Diagnosis
        # ----------------------------------------------------

        if claim.get(
            "diagnosis"
        ):

            st.subheader(
                "Diagnosis"
            )

            st.dataframe(

                dict_to_table(
                    claim[
                        "diagnosis"
                    ]
                ),

                use_container_width=True

            )


        # ----------------------------------------------------
        # Financial Details
        # ----------------------------------------------------

        if claim.get(
            "financials"
        ):

            st.subheader(
                "Financial Details"
            )

            st.dataframe(

                dict_to_table(
                    claim[
                        "financials"
                    ]
                ),

                use_container_width=True

            )


        # ----------------------------------------------------
        # Procedure
        # ----------------------------------------------------

        if claim.get(
            "procedure"
        ):

            st.subheader(
                "Procedure"
            )

            st.dataframe(

                dict_to_table(
                    claim[
                        "procedure"
                    ]
                ),

                use_container_width=True

            )


        # ====================================================
        # EXECUTE ADJUDICATION
        # ====================================================

        if st.button(
            "🚀 Run Adjudication",
            key="run_adjudication"
        ):

            with st.spinner(
                "Processing..."
            ):

                try:

                    result = workflow.run(
                        {
                            "claim": claim
                        }
                    )

                except Exception as e:

                    st.error(
                        f"Adjudication failed: {e}"
                    )

                    st.stop()


            st.success(
                "Completed"
            )


            # =================================================
            # OUTPUT
            # =================================================

            st.header(
                "📤 Claim Output"
            )


            # -------------------------------------------------
            # Final Decision
            # -------------------------------------------------

            st.subheader(
                "Final Decision"
            )

            adjudication_result = result.get(
                "adjudication_result",
                {}
            )

            decision_table = {

                "Claim ID":
                    claim.get(
                        "claim_id"
                    ),

                "Adjudication Decision":
                    adjudication_result.get(
                        "decision"
                    ),

                "Final Decision":
                    result.get(
                        "final_decision"
                    ),

                "Human Review Required":
                    result.get(
                        "human_review_required"
                    )
            }

            st.dataframe(

                dict_to_table(
                    decision_table
                ),

                use_container_width=True

            )


            # -------------------------------------------------
            # Financial Output
            # -------------------------------------------------

            st.subheader(
                "Financial Adjudication"
            )

            adjudication = result.get(
                "adjudication_result",
                {}
            )

            st.dataframe(

                dict_to_table(
                    {

                        "Claimed Amount":
                            adjudication.get(
                                "claimed_amount"
                            ),

                        "Payable Amount":
                            adjudication.get(
                                "payable_amount"
                            ),

                        "Decision":
                            adjudication.get(
                                "decision"
                            ),

                        "Reason":
                            adjudication.get(
                                "reason"
                            )

                    }
                ),

                use_container_width=True

            )


            # -------------------------------------------------
            # Fraud Output
            # -------------------------------------------------

            st.subheader(
                "Fraud Analysis"
            )

            fraud = result.get(
                "fraud_result",
                {}
            )

            st.dataframe(

                dict_to_table(
                    {

                        "Fraud Detected":
                            fraud.get(
                                "fraud_detected"
                            ),

                        "Risk Level":
                            fraud.get(
                                "risk_level"
                            ),

                        "Fraud Score":
                            fraud.get(
                                "fraud_score"
                            )

                    }
                ),

                use_container_width=True

            )


            # -------------------------------------------------
            # Guardrails
            # -------------------------------------------------

            st.subheader(
                "Guardrail Checks"
            )

            guard = result.get(
                "guardrail_result",
                {}
            )

            checks = guard.get(
                "checks",
                []
            )

            if checks:

                st.dataframe(

                    pd.DataFrame(
                        checks
                    ),

                    use_container_width=True

                )

            else:

                st.info(
                    "No guardrail checks returned."
                )


            # -------------------------------------------------
            # Execution Trace
            # -------------------------------------------------

            st.subheader(
                "Execution Trace"
            )

            execution_trace = result.get(
                "execution_trace",
                []
            )

            if execution_trace:

                st.dataframe(

                    pd.DataFrame(
                        execution_trace
                    ),

                    use_container_width=True

                )

            else:

                st.info(
                    "No execution trace returned."
                )


# ============================================================
# TESTING PANEL
# ============================================================

with testing_panel:

    st.header(
        "🧪 Testing"
    )

    st.write(
        "Run project test suites directly from the Streamlit application."
    )


    # ========================================================
    # TESTING TABS
    # ========================================================

    unit_tab, integration_tab, evaluation_tab = st.tabs(
        [
            "🔹 Unit Testing",
            "🔹 Integration Testing",
            "🔹 Evaluation Testing"
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
            language="bash"
        )

        if st.button(
            "▶ Run Unit Tests",
            key="run_unit_tests"
        ):

            with st.spinner(
                "Running unit tests..."
            ):

                result = subprocess.run(
                    [
                        "pytest",
                        "-v",
                        "tests/unit"
                    ],
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:

                st.success(
                    "✅ Unit tests completed successfully."
                )

            else:

                st.error(
                    "❌ Unit tests completed with failures."
                )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            st.text_area(
                "Unit Test Output",
                output,
                height=500
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
            "components such as MCP services, RAG, memory, "
            "fraud detection, and the claim workflow."
        )

        st.code(
            "pytest -v -m integration",
            language="bash"
        )

        if st.button(
            "▶ Run Integration Tests",
            key="run_integration_tests"
        ):

            with st.spinner(
                "Running integration tests..."
            ):

                result = subprocess.run(
                    [
                        "pytest",
                        "-v",
                        "-m",
                        "integration"
                    ],
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:

                st.success(
                    "✅ Integration tests completed successfully."
                )

            else:

                st.error(
                    "❌ Integration tests completed with failures."
                )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            st.text_area(
                "Integration Test Output",
                output,
                height=500
            )


    # ========================================================
    # EVALUATION TESTING
    # ========================================================

    with evaluation_tab:

        st.subheader(
            "🔹 Evaluation Testing"
        )

        st.write(
            "Evaluation tests measure the accuracy of claim "
            "adjudication decisions against expected outcomes."
        )

        st.code(
            "pytest -v tests/evaluation",
            language="bash"
        )

        if st.button(
            "▶ Run Evaluation Tests",
            key="run_evaluation_tests"
        ):

            with st.spinner(
                "Running evaluation tests..."
            ):

                result = subprocess.run(
                    [
                        "pytest",
                        "-v",
                        "tests/evaluation"
                    ],
                    capture_output=True,
                    text=True
                )

            if result.returncode == 0:

                st.success(
                    "✅ Evaluation tests completed successfully."
                )

            else:

                st.error(
                    "❌ Evaluation tests completed with failures."
                )

            output = (
                result.stdout
                + "\n"
                + result.stderr
            )

            st.text_area(
                "Evaluation Test Output",
                output,
                height=500
            )