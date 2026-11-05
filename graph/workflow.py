from langgraph.graph import StateGraph, END

from agents.monitoring import monitoring_agent
from agents.correlation import correlation_agent
from agents.crew_runner import run_crew


# ------------------ DECISION FUNCTIONS ------------------ #

def check_anomaly(state):
    """
    Decision after Monitoring Agent
    """
    if state.get("anomaly_score", 0) >= state.get("threshold", 1):
        state["steps"].append("Decision: Anomaly detected → moving to Correlation")
        return "Correlation Agent"
    else:
        state["steps"].append("Decision: No anomaly → END")
        return END


def check_confidence(state):
    """
    Decision after RCA Agent
    """
    if state.get("confidence", 0) >= 0.75:
        state["steps"].append("Decision: Confidence sufficient → END")
        return END
    else:
        state["steps"].append("Decision: Low confidence → Re-running RCA")
        return "RCA Agent"


# ------------------ BUILD GRAPH ------------------ #

def build_graph():
    builder = StateGraph(dict)

    # 🔷 Nodes (Agents)
    builder.add_node("Monitoring Agent", monitoring_agent)
    builder.add_node("Correlation Agent", correlation_agent)
    builder.add_node("RCA Agent", run_crew)

    # 🔷 Entry point
    builder.set_entry_point("Monitoring Agent")

    # 🔷 Flow connections
    builder.add_conditional_edges("Monitoring Agent", check_anomaly)
    builder.add_edge("Correlation Agent", "RCA Agent")
    builder.add_conditional_edges("RCA Agent", check_confidence)
    

    # 🔷 Compile graph
    return builder.compile()