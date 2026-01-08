from utils.risk_shift import (
    build_risk_timeseries,
    compute_risk_shift,
    summarize_latest_shift
)

def test_risk_shift_pipeline_nvda():
    df = build_risk_timeseries("NVDA")

    assert df is not None
    assert not df.empty
    assert "year" in df.columns

    shift_df = compute_risk_shift(df)
    assert shift_df is not None
    assert not shift_df.empty

    summary = summarize_latest_shift(df)
    assert isinstance(summary, dict)
    assert "latest_year" in summary

