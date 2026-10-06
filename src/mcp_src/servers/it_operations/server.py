import json

from mcp.server.fastmcp import FastMCP

from src.common.logging_config import get_logger
from src.rag_src.config.rag_settings import BASE_DIR


logger = get_logger("it_operations")


# =========================================================
# CREATE IT OPERATIONS MCP SERVER
# =========================================================

mcp = FastMCP("IT Operations Server")


# =========================================================
# PERSISTENT STATE FILE
# =========================================================

STATE_FILE = BASE_DIR / "data" / "service_state.json"


# =========================================================
# DEFAULT SIMULATED PRODUCTION SERVICE DATA
# =========================================================

SERVICE_DATA = {

    "payments-api": {
        "status": "degraded",
        "cpu_percent": 72,
        "memory_percent": 68,
        "db_pool_utilization_percent": 98,
        "active_db_connections": 49,
        "max_db_connections": 50
    },

    "checkout-api": {
        "status": "healthy",
        "cpu_percent": 35,
        "memory_percent": 42,
        "db_pool_utilization_percent": 45,
        "active_db_connections": 18,
        "max_db_connections": 40
    }
}


# =========================================================
# DEFAULT SIMULATED APPLICATION LOGS
# =========================================================

SERVICE_LOGS = {

    "payments-api": [
        "ERROR DatabaseConnectionPoolTimeout",
        "ERROR HTTP 500 POST /payments",
        "WARN DB connection pool utilization reached 98%",
        "ERROR Unable to acquire database connection"
    ],

    "checkout-api": [
        "INFO Checkout request processed successfully",
        "INFO HTTP 200 POST /checkout"
    ]
}


# =========================================================
# INITIALIZE PERSISTENT STATE
# =========================================================

def initialize_state() -> None:
    """
    Create service_state.json only if it does not already exist.

    SERVICE_DATA and SERVICE_LOGS are used only for the
    first initialization.
    """

    # If state already exists, do not overwrite it.
    if STATE_FILE.exists():
        return

    # Create data directory if required.
    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Initial simulated production state.
    initial_state = {
        "services": SERVICE_DATA,
        "logs": SERVICE_LOGS
    }

    # Persist initial state to JSON.
    STATE_FILE.write_text(
        json.dumps(
            initial_state,
            indent=4
        ),
        encoding="utf-8"
    )

    logger.info(
        "IT Operations: persistent service state initialized"
    )


# =========================================================
# LOAD PERSISTENT STATE
# =========================================================

def load_state() -> dict:
    """
    Read the latest service state from service_state.json.
    """

    # Make sure state file exists.
    initialize_state()

    # Read JSON and convert it into a Python dictionary.
    return json.loads(
        STATE_FILE.read_text(
            encoding="utf-8"
        )
    )


# =========================================================
# SAVE PERSISTENT STATE
# =========================================================

def save_state(state: dict) -> None:
    """
    Save the complete updated service state
    to service_state.json.
    """

    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=4
        ),
        encoding="utf-8"
    )

    logger.info(
        "IT Operations: persistent service state saved"
    )


# =========================================================
# TOOL 1: GET SERVICE HEALTH
# =========================================================

@mcp.tool()
def get_service_health(service_name: str) -> dict:
    """
    Return the latest persisted health information
    for a service.
    """

    logger.info(
        "IT Operations: health requested for service=%s",
        service_name
    )

    # Load latest state from JSON.
    state = load_state()

    # Find requested service.
    service = state["services"].get(service_name)

    # Service does not exist.
    if service is None:

        logger.warning(
            "IT Operations: service not found=%s",
            service_name
        )

        return {
            "service": service_name,
            "found": False,
            "message": "Service not found"
        }

    logger.info(
        "IT Operations: health retrieved "
        "service=%s status=%s",
        service_name,
        service["status"]
    )

    # Return complete latest service health.
    return {
        "service": service_name,
        "found": True,
        **service
    }


# =========================================================
# TOOL 2: GET SERVICE LOGS
# =========================================================

@mcp.tool()
def get_service_logs(service_name: str) -> dict:
    """
    Return the latest persisted application logs
    for a service.
    """

    logger.info(
        "IT Operations: logs requested for service=%s",
        service_name
    )

    # Load latest state from JSON.
    state = load_state()

    # Get logs for requested service.
    logs = state["logs"].get(service_name)

    # Logs/service not found.
    if logs is None:

        logger.warning(
            "IT Operations: logs not found service=%s",
            service_name
        )

        return {
            "service": service_name,
            "found": False,
            "logs": [],
            "message": "Service logs not found"
        }

    logger.info(
        "IT Operations: %d log entries retrieved "
        "for service=%s",
        len(logs),
        service_name
    )

    return {
        "service": service_name,
        "found": True,
        "logs": logs
    }


# =========================================================
# TOOL 3: RESTART SERVICE
# =========================================================

@mcp.tool()
def restart_service(service_name: str) -> dict:
    """
    Simulate a controlled restart of a production service.

    This tool must only be called after human approval.
    """

    logger.info(
        "IT Operations: restart requested for service=%s",
        service_name
    )


    # -----------------------------------------------------
    # STEP 1: LOAD LATEST PERSISTENT STATE
    # -----------------------------------------------------

    state = load_state()

    service = state["services"].get(service_name)


    # -----------------------------------------------------
    # STEP 2: CHECK SERVICE EXISTS
    # -----------------------------------------------------

    if service is None:

        logger.warning(
            "IT Operations: restart failed. "
            "Service not found=%s",
            service_name
        )

        return {
            "success": False,
            "service": service_name,
            "action": "restart",
            "action_status": "failed",
            "message": "Service not found."
        }


    # -----------------------------------------------------
    # STEP 3: CHECK IF SERVICE IS ALREADY HEALTHY
    # -----------------------------------------------------

    if service["status"] == "healthy":

        logger.info(
            "IT Operations: restart skipped. "
            "Service already healthy=%s",
            service_name
        )

        return {
            "success": True,
            "service": service_name,
            "action": "restart",

            # Status of the ACTION, not service health.
            "action_status": "skipped",

            # Current health loaded from service_state.json.
            "health_after_restart": service,

            "message": (
                f"{service_name} is already healthy. "
                f"Restart not required."
            )
        }


    # -----------------------------------------------------
    # STEP 4: SIMULATE SERVICE RECOVERY
    # -----------------------------------------------------

    # Update the complete service health state.
    service["status"] = "healthy"
    service["cpu_percent"] = 38
    service["memory_percent"] = 45
    service["db_pool_utilization_percent"] = 42
    service["active_db_connections"] = 21


    # -----------------------------------------------------
    # STEP 5: ADD RESTART EVENT TO LOGS
    # -----------------------------------------------------

    state["logs"].setdefault(
        service_name,
        []
    ).append(
        "INFO Service restarted after human approval"
    )


    # -----------------------------------------------------
    # STEP 6: SAVE COMPLETE UPDATED STATE
    # -----------------------------------------------------

    # This persists status + CPU + memory + DB metrics
    # + connections + updated logs.
    save_state(state)


    # -----------------------------------------------------
    # STEP 7: VERIFY SAVED STATE
    # -----------------------------------------------------

    # Read the JSON again instead of assuming
    # that the update succeeded.
    verification_state = load_state()

    health_after_restart = (
        verification_state["services"].get(service_name)
    )

    restart_successful = (
        health_after_restart is not None
        and
        health_after_restart["status"] == "healthy"
    )


    # -----------------------------------------------------
    # STEP 8: LOG RESULT
    # -----------------------------------------------------

    logger.info(
        "IT Operations: restart completed "
        "service=%s success=%s",
        service_name,
        restart_successful
    )


    # -----------------------------------------------------
    # STEP 9: RETURN RESULT
    # -----------------------------------------------------

    return {
        "success": restart_successful,
        "service": service_name,
        "action": "restart",

        # Status of restart action.
        "action_status": (
            "completed"
            if restart_successful
            else "failed"
        ),

        # Actual service health read back from JSON.
        "health_after_restart": health_after_restart,

        "message": (
            f"{service_name} restarted and "
            f"health verified successfully."
            if restart_successful
            else
            f"{service_name} restart verification failed."
        )
    }


# =========================================================
# START MCP SERVER
# =========================================================

if __name__ == "__main__":
    mcp.run()