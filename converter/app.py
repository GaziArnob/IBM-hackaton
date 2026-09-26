"""LegacyLift Converter: upload a legacy Spring Boot project zip, download it migrated."""
import tempfile
from pathlib import Path

import streamlit as st

import converter as cv

st.set_page_config(page_title="LegacyLift Converter", page_icon="🚀", layout="wide")
st.title("LegacyLift Converter")
st.caption("Upload a legacy Maven + Spring Boot 2.x project as a .zip and get it back on "
           "Java 21 + Spring Boot 3, with a test-verified report. Rule-based (OpenRewrite), no AI.")

# ── Sidebar: environment and options ───────────────────────────────────────
jdks = cv.find_jdks()
with st.sidebar:
    st.header("Settings")
    target_java = st.selectbox("Target Java", ["21", "17"], index=0)
    target_boot = st.selectbox("Target Spring Boot", ["3.4", "3.3", "3.2", "3.1", "3.0"], index=0)
    st.divider()
    st.subheader("Installed JDKs")
    if jdks:
        for major, home in jdks.items():
            st.write(f"✅ JDK {major}")
    else:
        st.error("No JDK found.")
    for need in (17, int(target_java)):
        if need not in jdks:
            st.warning(f"JDK {need} missing:\n\n`winget install --id "
                       f"EclipseAdoptium.Temurin.{need}.JDK -e`")
    st.divider()
    st.caption("⚠️ Building a project runs its code. Only convert projects you trust.")

# ── Upload ───────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Legacy project (.zip)", type=["zip"])
st.markdown("**What happens:** extract → build & test the original → OpenRewrite migration → "
            "known fixes → build & test on the new JDK → verify tests were not changed → report.")

if uploaded and st.button("Convert ▶", type="primary"):
    tmp = Path(tempfile.mkdtemp())
    zip_path = tmp / uploaded.name
    zip_path.write_bytes(uploaded.getbuffer())

    lines: list[str] = []
    with st.status("Converting... (first run downloads Maven recipes and can take 10+ minutes)",
                   expanded=True) as status:
        stage = st.empty()
        box = st.empty()

        def log(msg: str) -> None:
            lines.append(msg)
            if msg[:1].isdigit() and "/6" in msg[:5]:
                stage.markdown(f"**{msg}**")
            box.code("\n".join(lines[-18:]), language=None)

        result = cv.convert(zip_path, target_java, target_boot, log=log)
        state = {"SUCCESS": "complete", "PARTIAL": "complete", "FAILED": "error"}[result.status]
        status.update(label=f"{result.status}: {result.message}", state=state, expanded=False)
    st.session_state["result"] = result

# ── Result ───────────────────────────────────────────────────────────────────
res = st.session_state.get("result")
if res:
    color = {"SUCCESS": st.success, "PARTIAL": st.warning, "FAILED": st.error}[res.status]
    color(f"**{res.status}**: {res.message}")

    b, m = res.baseline or cv.TestResult(), res.migrated or cv.TestResult()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Java", res.java_after, f"from {res.java_before}", delta_color="off")
    c2.metric("Spring Boot", res.boot_after, f"from {res.boot_before}", delta_color="off")
    c3.metric("Tests passing", f"{m.passed}/{m.run - m.skipped}" if m.run else "-",
              f"baseline {b.passed}/{b.run - b.skipped}", delta_color="off")
    c4.metric("javax EE files", res.javax_after, f"{res.javax_after - res.javax_before}",
              delta_color="inverse")
    c5.metric("Time", f"{res.seconds / 60:.1f} min")

    if res.migrated:
        if res.test_logic_changed:
            st.warning("Test logic changed in: " + ", ".join(res.test_logic_changed))
        else:
            st.info("✅ Test integrity: no test logic was changed (only imports/formatting).")

    dl = st.columns(4)
    if res.zip_path and res.zip_path.exists():
        dl[0].download_button("⬇ Migrated project (.zip)", res.zip_path.read_bytes(),
                              file_name=res.zip_path.name, type="primary")
    if res.report_path and res.report_path.exists():
        dl[1].download_button("⬇ Report (.md)", res.report_path.read_bytes(),
                              file_name="MIGRATION_REPORT.md")
    if res.patch_path and res.patch_path.exists():
        dl[2].download_button("⬇ Diff (.patch)", res.patch_path.read_bytes(),
                              file_name="migration.patch")
    if res.metrics_path and res.metrics_path.exists():
        dl[3].download_button("⬇ metrics.json", res.metrics_path.read_bytes(),
                              file_name="metrics.json")

    if res.report_path and res.report_path.exists():
        with st.expander("Report", expanded=True):
            st.markdown(res.report_path.read_text(encoding="utf-8"))
    log_file = res.job_dir / "build.log" if res.job_dir else None
    if log_file and log_file.exists():
        with st.expander("Full build log"):
            st.code(log_file.read_text(encoding="utf-8", errors="replace")[-20000:], language=None)
    st.caption(f"Work folder: {res.job_dir}")
