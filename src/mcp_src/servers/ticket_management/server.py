from mcp.server.fastmcp import FastMCP

from src.common.logging_config import get_logger


logger = get_logger("ticket_management")

mcp = FastMCP("Ticket Management Server")


# =========================================================
# SIMULATED TICKET DATABASE
# =========================================================

TICKETS = {
    "INC-1001": {
        "ticket_id": "INC-1001",
        "service": "payments-api",
        "summary": "Payments API returning HTTP 500",
        "severity": "P1",
        "status": "Open"
    },

    "INC-1002": {
        "ticket_id": "INC-1002",
        "service": "checkout-api",
        "summary": "Checkout API response time increased",
        "severity": "P2",
        "status": "Investigating"
    }
}


# =========================================================
# TOOL 1: GET TICKET
# =========================================================

@mcp.tool()
def get_ticket(ticket_id: str) -> dict:
    """
    Get an existing incident ticket.
    """

    logger.info("Ticket requested: %s", ticket_id)

    ticket = TICKETS.get(ticket_id)

    if ticket is None:

        logger.warning("Ticket not found: %s", ticket_id)

        return {
            "found": False,
            "ticket_id": ticket_id,
            "message": "Ticket not found"
        }

    logger.info("Ticket found: %s", ticket_id)

    return {
        "found": True,
        "ticket": ticket
    }


# =========================================================
# TOOL 2: CREATE TICKET
# =========================================================

@mcp.tool()
def create_ticket(
    service: str,
    summary: str,
    severity: str
) -> dict:
    """
    Create a new incident ticket.
    """

    next_number = len(TICKETS) + 1001

    ticket_id = f"INC-{next_number}"

    new_ticket = {
        "ticket_id": ticket_id,
        "service": service,
        "summary": summary,
        "severity": severity,
        "status": "Open"
    }

    TICKETS[ticket_id] = new_ticket

    logger.info(
        "Ticket created: %s service=%s severity=%s",
        ticket_id,
        service,
        severity
    )

    return {
        "created": True,
        "ticket": new_ticket
    }


# =========================================================
# TOOL 3: UPDATE TICKET
# =========================================================

@mcp.tool()
def update_ticket(
    ticket_id: str,
    status: str
) -> dict:
    """
    Update the status of an existing incident ticket.
    """

    logger.info(
        "Ticket update requested: %s status=%s",
        ticket_id,
        status
    )

    ticket = TICKETS.get(ticket_id)

    if ticket is None:

        logger.warning(
            "Cannot update. Ticket not found: %s",
            ticket_id
        )

        return {
            "updated": False,
            "ticket_id": ticket_id,
            "message": "Ticket not found"
        }

    ticket["status"] = status

    logger.info(
        "Ticket updated: %s status=%s",
        ticket_id,
        status
    )

    return {
        "updated": True,
        "ticket": ticket
    }


# =========================================================
# START MCP SERVER
# =========================================================

if __name__ == "__main__":
    mcp.run()