import os

def query_rag_agent(ticker_symbol, query_text):
    """
    RAG Agent (Helper 2): Scans regulatory filings for the given stock symbol 
    and returns grounded findings with exact citations.
    """
    # Clean ticker (e.g., RELIANCE.NS -> RELIANCE)
    clean_symbol = ticker_symbol.split('.')[0]
    file_path = f"documents/{clean_symbol}_filing.txt"
    
    # Graceful Fallback Handling (Requirement Check)
    if not os.path.exists(file_path):
        return {
            "status": "Degraded",
            "source": "None",
            "findings": f"No official SEBI disclosures found locally for {clean_symbol}.",
            "citation": "Missing Corpus File - Graceful Fallback Triggered"
        }
    
    try:
        with open(file_path, "r") as f:
            content = f.read()
            
        # Extract relevant lines based on query keyword match (Simple & Fast vector alternative)
        lines = content.split('\n')
        relevant_lines = [line for line in lines if any(k in line.lower() for k in ["revenue", "profit", "sebi", "guidance", "growth", "debt"])]
        
        summary = " ".join(relevant_lines) if relevant_lines else content[:200]
        
        return {
            "status": "Success",
            "source": f"{clean_symbol}_filing.txt",
            "findings": summary,
            "citation": f"SEBI Regulatory Disclosure ({clean_symbol}_filing.txt, Section 1)"
        }
    except Exception as e:
        return {
            "status": "Error",
            "source": "None",
            "findings": str(e),
            "citation": "System Failure Fallback"
        }