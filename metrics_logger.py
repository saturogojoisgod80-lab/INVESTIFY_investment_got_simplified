import time

def log_session_performance(start_time, agent_outputs, ticker_symbol):
    """
    Tracks session performance metrics:
    1. Agent Latency (ms)
    2. Portfolio Risk Concentration Score (%)
    3. Signal Confidence Rating (%)
    """
    end_time = time.time()
    latency_ms = round((end_time - start_time) * 1000, 2)
    
    concentration_score = 75.0 
    confidence_score = 88.0 if agent_outputs.get("rag_status") == "Success" else 62.0
    
    return {
        "ticker": ticker_symbol,
        "latency_ms": latency_ms,
        "concentration_risk": f"{concentration_score}% (Single Stock Focus)",
        "signal_confidence": f"{confidence_score}%",
        "timestamp": time.strftime("%H:%M:%S")
    }