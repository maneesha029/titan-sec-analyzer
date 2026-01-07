from core.engine import extract_risk_factors
from core.risk_features import extract_risk_features


def run_risk_pipeline(filing):
    risk_text = extract_risk_factors(filing)
    features = extract_risk_features(risk_text)

    return {
        "raw_text": risk_text,
        "features": features
    }
