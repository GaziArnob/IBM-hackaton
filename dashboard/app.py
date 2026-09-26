"""LegacyLift Streamlit dashboard."""
from pathlib import Path
import json
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = ROOT / "reports" / "metrics.json"
REPORTS = {
    "Architecture": ROOT / "reports" / "ARCHITECTURE.md",
    "Coverage":     ROOT / "reports" / "COVERAGE.md",
    "Changelog":    ROOT / "reports" / "CHANGELOG.md",
    "Migration Report": ROOT / "reports" / "MIGRATION_REPORT.md",
}
BOB_SESSIONS = ROOT / "bob_sessions"

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="LegacyLift", layout="wide")

# ── Load metrics ─────────────────────────────────────────────────────────────
if not METRICS_FILE.exists():
    st.error(f"metrics.json not found at {METRICS_FILE}")
    st.stop()

with open(METRICS_FILE) as f:
    m = json.load(f)

# ── Header ───────────────────────────────────────────────────────────────────
st.title("LegacyLift – Legacy to Modern, with Tests as Proof")
st.caption(
    f"Spring PetClinic: Java {m['java_before']} + Boot {m['boot_before']} "
    f"→ Java {m['java_after']} + Boot {m['boot_after']}, powered by IBM Bob"
)

st.divider()

# ── Pipeline row ─────────────────────────────────────────────────────────────
st.subheader("Pipeline")
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown("### ✅ Explain")
    st.write("Architecture analysis, dependency diagram, migration inventory and risk list.")
with c2:
    st.markdown("### ✅ Protect")
    tests_added = m["tests_after"] - m["tests_before"]
    st.write(f"{tests_added} characterization tests added (OwnerTests, PetValidatorTests, VisitTests + extensions).")
with c3:
    st.markdown("### ✅ Migrate")
    st.write(
        f"javax → jakarta, Boot {m['boot_before']} → {m['boot_after']}, "
        f"Java {m['java_before']} → {m['java_after']}, all dependency updates applied."
    )
with c4:
    st.markdown("### ✅ Prove")
    st.write(
        f"70/70 executed tests passing (1 skipped), "
        f"{m['tests_failed_after_migration']} failures, "
        f"branch coverage held at {m['branch_cov_after_migration']} %."
    )

st.divider()

# ── KPI row ──────────────────────────────────────────────────────────────────
st.subheader("Key Metrics")
k1, k2, k3, k4 = st.columns(4)
with k1:
    st.metric(
        label="Time Saved",
        value=f"{m['time_saved_percent']} %",
        delta=f"vs {m['hours_manual_estimate']} h manual estimate",
    )
with k2:
    st.metric(
        label="Tests",
        value=m["tests_after"],
        delta=f"+{m['tests_after'] - m['tests_before']} (was {m['tests_before']})",
    )
with k3:
    st.metric(
        label="Failures after migration",
        value=m["tests_failed_after_migration"],
        delta="0 regressions",
        delta_color="off",
    )
with k4:
    st.metric(
        label="javax files",
        value=m["javax_files_after"],
        delta=f"-{m['javax_files_before']} (was {m['javax_files_before']})",
        delta_color="inverse",
    )

st.divider()

# ── Charts ───────────────────────────────────────────────────────────────────
st.subheader("Coverage & Effort")
ch1, ch2 = st.columns(2)

with ch1:
    stages = ["Baseline", "After Char. Tests", "After Migration"]
    instr_y = [
        m["instruction_cov_baseline"],
        m["instruction_cov_after_tests"],
        m["instruction_cov_after_migration"],
    ]
    branch_y = [
        m["branch_cov_baseline"],
        m["branch_cov_after_tests"],
        m["branch_cov_after_migration"],
    ]
    fig_cov = go.Figure(data=[
        go.Bar(
            name="Instruction Coverage (%)",
            x=stages,
            y=instr_y,
            text=[f"{v} %" for v in instr_y],
            textposition="outside",
        ),
        go.Bar(
            name="Branch Coverage (%)",
            x=stages,
            y=branch_y,
            text=[f"{v} %" for v in branch_y],
            textposition="outside",
        ),
    ])
    fig_cov.update_layout(
        barmode="group",
        title="Coverage Across Stages",
        yaxis=dict(range=[0, 100], title="%"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(t=60),
    )
    st.plotly_chart(fig_cov, use_container_width=True)

with ch2:
    fig_hours = go.Figure(data=[
        go.Bar(
            x=["With LegacyLift", "Manual Estimate"],
            y=[m["hours_with_legacylift"], m["hours_manual_estimate"]],
            marker_color=["#2ecc71", "#e74c3c"],
        )
    ])
    fig_hours.update_layout(
        title="Migration Time (hours)",
        yaxis_title="Hours",
        margin=dict(t=60),
    )
    st.plotly_chart(fig_hours, use_container_width=True)

st.divider()

# ── Before / After table ─────────────────────────────────────────────────────
st.subheader("Before / After")
table = pd.DataFrame(
    {
        "Component": ["Java", "Spring Boot"],
        "Before": [f"Java {m['java_before']}", f"Boot {m['boot_before']}"],
        "After":  [f"Java {m['java_after']}",  f"Boot {m['boot_after']}"],
    }
)
st.table(table)

st.divider()

# ── Detail tabs ──────────────────────────────────────────────────────────────
tab_names = list(REPORTS.keys()) + ["Bob Evidence"]
tabs = st.tabs(tab_names)

for tab, (name, path) in zip(tabs[:-1], REPORTS.items()):
    with tab:
        if not path.exists():
            st.warning(f"{path.name} not found.")
            continue
        content = path.read_text(encoding="utf-8")
        if name == "Architecture":
            # Render markdown but show mermaid blocks as code fences
            parts = content.split("```mermaid")
            st.markdown(parts[0])
            for part in parts[1:]:
                mermaid_end = part.find("```")
                mermaid_src = part[:mermaid_end]
                after = part[mermaid_end + 3:]
                st.code("```mermaid\n" + mermaid_src + "```", language=None)
                st.markdown(after)
        else:
            st.markdown(content)

# Bob Evidence tab
with tabs[-1]:
    if not BOB_SESSIONS.exists():
        st.warning(f"bob_sessions/ directory not found at {BOB_SESSIONS}")
    else:
        pngs = sorted(BOB_SESSIONS.glob("*.png"))
        if not pngs:
            st.info("No PNG screenshots found in bob_sessions/.")
        else:
            for png in pngs:
                st.image(str(png), caption=png.name, use_container_width=True)
