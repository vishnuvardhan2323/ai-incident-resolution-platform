# ============================================================
# STEP 1: IMPORTS
# ============================================================

import requests
import streamlit as st
import os

# ============================================================
# STEP 2: FASTAPI ENDPOINTS
# ============================================================

#BACKEND_URL = "http://127.0.0.1:8000"
BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
)

INCIDENT_ENDPOINT = f"{BACKEND_URL}/incidents/resolve"
ACTION_ENDPOINT = f"{BACKEND_URL}/actions/execute"


# ============================================================
# STEP 3: STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Incident Resolution Platform",
    page_icon="🛠️",
    layout="wide"
)

st.title("AI-Powered IT Service Desk")
st.caption(
    "Multi-Agent Incident Investigation, Resolution "
    "and Human-in-the-Loop Operations"
)


# ============================================================
# STEP 4: INITIALIZE SESSION STATE
# ============================================================

if "incident_result" not in st.session_state:
    st.session_state.incident_result = None

if "action_result" not in st.session_state:
    st.session_state.action_result = None


# ============================================================
# STEP 5: INCIDENT INPUT
# ============================================================

st.subheader("Report Production Incident")

incident_text = st.text_area(
    "Incident Description",
    placeholder=(
        "Example: Payments API is returning HTTP 500 "
        "and customers cannot complete checkout."
    ),
    height=120
)


# ============================================================
# STEP 6: ANALYZE INCIDENT
# ============================================================

if st.button("Analyze Incident", type="primary"):

    if not incident_text.strip():
        st.warning("Please enter an incident description.")

    else:
        try:
            with st.spinner(
                "AI agents are investigating the incident..."
            ):
                response = requests.post(
                    INCIDENT_ENDPOINT,
                    json={
                        "incident": incident_text
                    },
                    #timeout=180
                    timeout = 900
                )

            response.raise_for_status()

            st.session_state.incident_result = response.json()
            st.session_state.action_result = None

        except requests.RequestException as exc:
            st.error(
                f"Unable to communicate with FastAPI backend: {exc}"
            )


# ============================================================
# STEP 7: DISPLAY INCIDENT RESULTS
# ============================================================

result = st.session_state.incident_result

if result:

    st.divider()

    st.header("Incident Analysis")

    # --------------------------------------------------------
    # Classification
    # --------------------------------------------------------

    classification = result.get("classification", {})

    st.subheader("1. Incident Classification")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Service",
        classification.get("service", "Unknown")
    )

    col2.metric(
        "Severity",
        classification.get("severity", "Unknown")
    )

    col3.metric(
        "Route",
        result.get("route", "Unknown")
    )

    st.write(
        "**Category:**",
        classification.get("category", "Unknown")
    )

    st.write(
        "**Intent:**",
        classification.get("intent", "Unknown")
    )


    # --------------------------------------------------------
    # Knowledge / RAG
    # --------------------------------------------------------

    knowledge = result.get("knowledge", {})

    st.subheader("2. Knowledge Agent")

    if knowledge:
        st.markdown(
            knowledge.get(
                "answer",
                "No knowledge response available."
            )
        )

        source_files = knowledge.get("source_files", [])

        with st.expander("RAG Sources"):
            if source_files:
                for source in source_files:
                    st.write(f"- {source}")
            else:
                st.write("No sources returned.")

        st.write(
            "**Grounded:**",
            knowledge.get("grounded", False)
        )


    # --------------------------------------------------------
    # Investigation
    # --------------------------------------------------------

    investigation = result.get("investigation")

    st.subheader("3. Investigation Agent")

    if investigation:

        st.write(
            "**Service:**",
            investigation.get("service", "Unknown")
        )

        st.write("**Current Service Health**")
        st.json(
            investigation.get("health", {})
        )

        with st.expander("Recent Service Logs"):
            logs = investigation.get("logs", [])

            if logs:
                for log in logs:
                    st.code(log)
            else:
                st.write("No logs returned.")

        with st.expander("Asset Information"):
            st.json(
                investigation.get("asset", {})
            )

        st.write("**Investigation Findings**")

        findings = investigation.get("findings", [])

        if findings:
            for finding in findings:
                st.write(f"- {finding}")
        else:
            st.write("No findings returned.")

    else:
        st.info(
            "Live investigation was not required for this request."
        )


    # --------------------------------------------------------
    # Resolution
    # --------------------------------------------------------

    resolution = result.get("resolution")

    st.subheader("4. Resolution Agent")

    if resolution:

        st.write("**Root Cause**")
        st.write(
            resolution.get(
                "root_cause",
                "Not available."
            )
        )

        st.write("**Recommended Actions**")

        recommended_actions = resolution.get(
            "recommended_actions",
            []
        )

        for index, action in enumerate(
            recommended_actions,
            start=1
        ):
            st.write(f"{index}. {action}")

        st.write(
            "**Escalation Required:**",
            resolution.get(
                "escalation_required",
                False
            )
        )

        if resolution.get("escalation_required"):
            st.write(
                "**Escalation Team:**",
                resolution.get(
                    "escalation_team",
                    "Not specified"
                )
            )

    else:
        st.info(
            "Resolution stage was not required for this request."
        )


    # ========================================================
    # STEP 8: HUMAN APPROVAL
    # ========================================================

    if result.get("requires_human_approval"):

        st.divider()

        st.header("Human Approval Required")

        st.warning(
            "The AI has identified a production action that "
            "requires engineer approval."
        )

        service_name = investigation.get(
            "service",
            "payments-api"
        )

        st.write(
            f"**Proposed Action:** Restart `{service_name}`"
        )

        approve_col, reject_col = st.columns(2)


        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        with approve_col:

            if st.button(
                "Approve Restart",
                type="primary"
            ):

                try:
                    with st.spinner(
                        "Executing approved action..."
                    ):
                        response = requests.post(
                            ACTION_ENDPOINT,
                            json={
                                "service_name": service_name,
                                "action": "restart",
                                "approved": True
                            },
                            timeout=60
                        )

                    response.raise_for_status()

                    st.session_state.action_result = (
                        response.json()
                    )

                except requests.RequestException as exc:
                    st.error(
                        f"Action execution failed: {exc}"
                    )


        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        with reject_col:

            if st.button("Reject Restart"):

                try:
                    response = requests.post(
                        ACTION_ENDPOINT,
                        json={
                            "service_name": service_name,
                            "action": "restart",
                            "approved": False
                        },
                        timeout=60
                    )

                    response.raise_for_status()

                    st.session_state.action_result = (
                        response.json()
                    )

                except requests.RequestException as exc:
                    st.error(
                        f"Unable to reject action: {exc}"
                    )


# ============================================================
# STEP 9: DISPLAY ACTION RESULT
# ============================================================

if st.session_state.action_result:

    action_result = st.session_state.action_result

    st.divider()
    st.subheader("Action Result")

    execution_status = action_result.get(
        "execution_status"
    )

    if execution_status == "COMPLETED":
        st.success(
            action_result.get(
                "message",
                "Action completed successfully."
            )
        )

    elif execution_status == "NOT_EXECUTED":
        st.warning(
            action_result.get(
                "message",
                "Action was not executed."
            )
        )

    else:
        st.error(
            action_result.get(
                "message",
                "Action execution failed."
            )
        )

    st.json(action_result)