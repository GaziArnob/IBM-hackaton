"""LegacyLift Converter engine.

Takes a zipped legacy Maven / Spring Boot project and migrates it to a modern
Java + Spring Boot version without AI:

  1. extract the zip safely and detect versions
  2. build and test the ORIGINAL project (baseline)
  3. run OpenRewrite (Spring's rule-based migration recipes)
  4. apply known fixes that OpenRewrite does not cover
  5. build and test the MIGRATED project on the new JDK
  6. prove test logic was not changed, write report + metrics, zip the result

Usage:  python converter.py path\\to\\project.zip [--java 21] [--boot 3.4] [--out DIR]
"""
from __future__ import annotations

import argparse
import json
import os
import queue
import re
import subprocess
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

TOOLS_DIR = Path.home() / ".legacylift"
# Keep jobs on the same drive as the Maven repository (~/.m2): OpenRewrite cannot
# relativize paths across Windows drives ("'other' has different root").
WORK_ROOT = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "LegacyLift" / "work"

BOOT_RECIPES = {
    "3.0": "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_0",
    "3.1": "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_1",
    "3.2": "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_2",
    "3.3": "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_3",
    "3.4": "org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_4",
}
JAVA_RECIPES = {
    "17": "org.openrewrite.java.migrate.UpgradeToJava17",
    "21": "org.openrewrite.java.migrate.UpgradeToJava21",
}
# Style/quality gates that fail on line endings or formatting, not on behaviour.
SKIP_GATES = ["-Dspring-javaformat.skip=true", "-Dcheckstyle.skip=true",
              "-Denforcer.skip=true", "-Dstyle.color=never"]

# javax packages that moved to jakarta (Jakarta EE 9+). JDK-owned javax packages
# such as javax.sql, javax.crypto, javax.net or javax.cache (JCache) are NOT listed.
JAKARTA_MOVED = re.compile(
    r"^\s*import\s+(?:static\s+)?javax\.(persistence|validation|servlet|transaction|"
    r"xml\.bind|xml\.ws|xml\.soap|jws|ws\.rs|ejb|enterprise|inject|faces|el|websocket|"
    r"mail|activation|json|jms|batch|interceptor|decorator|security\.enterprise|"
    r"annotation\.(?:PostConstruct|PreDestroy|Resource|Resources|Generated|Priority|"
    r"ManagedBean|security))\b", re.M)

MAVEN_VERSION = "3.9.9"
MAVEN_URL = (f"https://archive.apache.org/dist/maven/maven-3/{MAVEN_VERSION}/binaries/"
             f"apache-maven-{MAVEN_VERSION}-bin.zip")


class ConversionError(Exception):
    pass


# --------------------------------------------------------------------------- data
@dataclass
class TestResult:
    run: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    failed_tests: list[str] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return self.run - self.failures - self.errors - self.skipped


@dataclass
class Result:
    status: str = "RUNNING"            # SUCCESS | PARTIAL | FAILED
    message: str = ""
    project_name: str = ""
    java_before: str = "?"
    java_after: str = "?"
    boot_before: str = "?"
    boot_after: str = "?"
    baseline_jdk: str = ""
    baseline: TestResult | None = None
    migrated: TestResult | None = None
    coverage_before: dict | None = None
    coverage_after: dict | None = None
    javax_before: int = 0
    javax_after: int = 0
    fixes: list[str] = field(default_factory=list)
    changed_files: list[str] = field(default_factory=list)
    test_logic_changed: list[str] = field(default_factory=list)
    compile_errors: list[str] = field(default_factory=list)
    seconds: float = 0.0
    job_dir: Path | None = None
    zip_path: Path | None = None
    report_path: Path | None = None
    patch_path: Path | None = None
    metrics_path: Path | None = None


Log = Callable[[str], None]


# --------------------------------------------------------------------------- JDKs
def find_jdks() -> dict[int, Path]:
    """Return {major_version: jdk_home} for JDKs installed in common locations."""
    roots = [Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / d for d in
             ("Eclipse Adoptium", "Java", "Microsoft", "Zulu", "Amazon Corretto",
              "BellSoft", "OpenJDK")]
    candidates = [p for r in roots if r.is_dir() for p in r.iterdir() if p.is_dir()]
    for var in ("JAVA_HOME",):
        if os.environ.get(var):
            candidates.append(Path(os.environ[var]))
    jdks: dict[int, Path] = {}
    for home in candidates:
        if not (home / "bin" / "javac.exe").exists() and not (home / "bin" / "javac").exists():
            continue
        release = home / "release"
        major = None
        if release.exists():
            m = re.search(r'JAVA_VERSION="(1\.)?(\d+)', release.read_text(errors="ignore"))
            if m:
                major = int(m.group(2))
        if major and major not in jdks:
            jdks[major] = home
    return dict(sorted(jdks.items()))


def pick_baseline_jdks(jdks: dict[int, Path]) -> list[int]:
    """Order in which to try JDKs for the legacy build (Boot 2.x supports up to 17)."""
    return [v for v in (17, 11, 8, 21) if v in jdks] + \
           [v for v in jdks if v not in (17, 11, 8, 21)]


# --------------------------------------------------------------------------- zip
def safe_extract(zip_path: Path, dest: Path) -> Path:
    """Extract without allowing paths outside dest; return the project root."""
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        for member in z.infolist():
            target = (dest / member.filename).resolve()
            if not str(target).startswith(str(dest.resolve())):
                raise ConversionError(f"Unsafe path in zip: {member.filename}")
        z.extractall(dest)
    poms = sorted(dest.rglob("pom.xml"), key=lambda p: len(p.parts))
    poms = [p for p in poms if "target" not in p.parts]
    if not poms:
        if list(dest.rglob("build.gradle*")):
            raise ConversionError("This is a Gradle project. Only Maven projects are "
                                  "supported in this version.")
        raise ConversionError("No pom.xml found. Is this a Maven project?")
    return poms[0].parent


def zip_dir(src: Path, zip_path: Path) -> None:
    skip = {"target", ".git", "node_modules", ".idea", ".vscode"}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in src.rglob("*"):
            rel = p.relative_to(src)
            if any(part in skip for part in rel.parts) or p.is_dir():
                continue
            z.write(p, Path(src.name) / rel)


# --------------------------------------------------------------------------- pom
NS = {"m": "http://maven.apache.org/POM/4.0.0"}


def _pom_root(project: Path):
    return ET.parse(project / "pom.xml").getroot()


def _find(el, path):
    found = el.find(path, NS)
    return found if found is not None else el.find(path.replace("m:", ""))


def detect_versions(project: Path) -> tuple[str, str]:
    """Return (java_version, spring_boot_version) declared in pom.xml."""
    root = _pom_root(project)
    boot = "?"
    parent = _find(root, "m:parent")
    if parent is not None:
        aid = _find(parent, "m:artifactId")
        if aid is not None and aid.text == "spring-boot-starter-parent":
            boot = (_find(parent, "m:version").text or "?").strip()
    if boot == "?":
        text = (project / "pom.xml").read_text(encoding="utf-8", errors="ignore")
        m = re.search(r"<artifactId>spring-boot-dependencies</artifactId>\s*"
                      r"<version>([^<]+)</version>", text)
        if m:
            boot = m.group(1).strip()
    java = "?"
    props = _find(root, "m:properties")
    if props is not None:
        for key in ("java.version", "maven.compiler.release", "maven.compiler.source",
                    "maven.compiler.target"):
            el = _find(props, f"m:{key}")
            if el is not None and el.text:
                java = el.text.strip()
                break
    return java, boot


def uses_jacoco(project: Path) -> bool:
    return "jacoco-maven-plugin" in (project / "pom.xml").read_text(encoding="utf-8",
                                                                     errors="ignore")


# --------------------------------------------------------------------------- maven
def ensure_maven(log: Log) -> Path:
    """Download a private Apache Maven if the project has no wrapper."""
    home = TOOLS_DIR / f"apache-maven-{MAVEN_VERSION}"
    mvn = home / "bin" / "mvn.cmd"
    if mvn.exists():
        return mvn
    TOOLS_DIR.mkdir(parents=True, exist_ok=True)
    archive = TOOLS_DIR / "maven.zip"
    log(f"Downloading Apache Maven {MAVEN_VERSION} (one time)...")
    urllib.request.urlretrieve(MAVEN_URL, archive)
    with zipfile.ZipFile(archive) as z:
        z.extractall(TOOLS_DIR)
    archive.unlink()
    return mvn


def maven_cmd(project: Path, log: Log) -> list[str]:
    wrapper = project / "mvnw.cmd"
    if wrapper.exists() and (project / ".mvn" / "wrapper").exists():
        return ["cmd", "/c", str(wrapper)]
    return ["cmd", "/c", str(ensure_maven(log))]


def _kill_tree(proc: subprocess.Popen) -> None:
    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)], capture_output=True)


def run_maven(project: Path, args: list[str], jdk: Path, log: Log, log_file: Path,
              timeout: int = 1800, stall: int = 600, retries: int = 1) -> int:
    """Run Maven, streaming output. A run that prints nothing for `stall` seconds
    (e.g. a hung network download) is killed and retried."""
    env = dict(os.environ)
    env["JAVA_HOME"] = str(jdk)
    env["PATH"] = str(jdk / "bin") + os.pathsep + env.get("PATH", "")
    # Finite network timeouts so a dead connection cannot hang the JVM forever.
    env["MAVEN_OPTS"] = (env.get("MAVEN_OPTS", "") + " -Dfile.encoding=UTF-8 -Xmx2g"
                         " -Dsun.net.client.defaultConnectTimeout=30000"
                         " -Dsun.net.client.defaultReadTimeout=120000")
    cmd = maven_cmd(project, log) + ["-B"] + args
    for attempt in range(retries + 1):
        log(f"$ mvn {' '.join(args)}   [JDK {jdk.name}]")
        with open(log_file, "a", encoding="utf-8", errors="replace") as fh:
            fh.write(f"\n\n===== {' '.join(cmd)}  (JAVA_HOME={jdk})\n")
            proc = subprocess.Popen(cmd, cwd=project, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                    errors="replace")
            lines: queue.Queue = queue.Queue()
            threading.Thread(target=lambda: ([lines.put(l) for l in proc.stdout],
                                             lines.put(None)), daemon=True).start()
            start = last = time.time()
            outcome = None
            while outcome is None:
                try:
                    line = lines.get(timeout=5)
                except queue.Empty:
                    line = ""
                now = time.time()
                if line is None:
                    outcome = proc.wait()
                    break
                if line:
                    last = now
                    fh.write(line)
                    s = line.rstrip()
                    if re.search(r"Tests run: \d+, Failures|BUILD (SUCCESS|FAILURE)|"
                                 r"Downloading Apache|Running recipe|Changes have been made|"
                                 r"\[ERROR\] .*\.java", s):
                        log("  " + s[:240])
                if now - start > timeout:
                    _kill_tree(proc)
                    log("  Timed out.")
                    return 124
                if now - last > stall:
                    _kill_tree(proc)
                    outcome = "stalled"
            if outcome != "stalled":
                return outcome
            log(f"  No output for {stall // 60} min (likely a hung download). "
                + ("Retrying..." if attempt < retries else "Giving up."))
    return 125


# --------------------------------------------------------------------------- reports
def read_surefire(project: Path) -> TestResult:
    res = TestResult()
    for xml_file in (project / "target" / "surefire-reports").glob("TEST-*.xml"):
        try:
            suite = ET.parse(xml_file).getroot()
        except ET.ParseError:
            continue
        res.run += int(suite.get("tests", 0))
        res.failures += int(suite.get("failures", 0))
        res.errors += int(suite.get("errors", 0))
        res.skipped += int(suite.get("skipped", 0))
        for case in suite.iter("testcase"):
            if case.find("failure") is not None or case.find("error") is not None:
                res.failed_tests.append(f"{case.get('classname')}.{case.get('name')}")
    return res


def read_jacoco(project: Path) -> dict | None:
    csv = project / "target" / "site" / "jacoco" / "jacoco.csv"
    if not csv.exists():
        return None
    tot = [0] * 6
    for line in csv.read_text(encoding="utf-8").splitlines()[1:]:
        cols = line.split(",")
        for i in range(6):
            tot[i] += int(cols[3 + i])
    pct = lambda missed, covered: round(100 * covered / (missed + covered), 1) \
        if missed + covered else None
    return {"instruction": pct(tot[0], tot[1]), "branch": pct(tot[2], tot[3]),
            "line": pct(tot[4], tot[5])}


def count_javax(project: Path) -> int:
    count = 0
    for f in (project / "src").rglob("*.java"):
        if JAKARTA_MOVED.search(f.read_text(encoding="utf-8", errors="ignore")):
            count += 1
    return count


def compile_errors(log_file: Path) -> list[str]:
    errs = []
    for line in log_file.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.search(r"\[ERROR\] .+\.java:\[\d+", line):
            errs.append(line.replace("[ERROR] ", "").strip())
    return list(dict.fromkeys(errs))[:40]


# --------------------------------------------------------------------------- git
def git(project: Path, *args: str) -> str:
    out = subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.safecrlf=false",
                          "-c", "user.name=LegacyLift", "-c", "user.email=legacylift@local",
                          *args], cwd=project, capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return out.stdout


def snapshot(project: Path, message: str) -> None:
    if not (project / ".git").exists():
        git(project, "init", "-q")
        (project / ".git" / "info").mkdir(exist_ok=True)
        (project / ".git" / "info" / "exclude").write_text("target/\n")
    git(project, "add", "-A")
    git(project, "commit", "-q", "--allow-empty", "-m", message)


def _logic(text: str) -> str:
    """Test source without imports, comments' whitespace and formatting."""
    body = "\n".join(l for l in text.splitlines() if not l.strip().startswith("import "))
    return re.sub(r"\s+", "", body)


def changed_test_logic(project: Path, base_rev: str) -> list[str]:
    changed = []
    names = git(project, "diff", "--name-only", base_rev, "--", "src/test").split()
    for name in names:
        before = git(project, "show", f"{base_rev}:{name}")
        path = project / name
        after = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
        if _logic(before) != _logic(after):
            changed.append(name)
    return changed


# --------------------------------------------------------------------------- fixes
def _version_lt(a: str, b: str) -> bool:
    pa = [int(x) for x in re.findall(r"\d+", a)[:3]]
    pb = [int(x) for x in re.findall(r"\d+", b)[:3]]
    return pa < pb


def apply_known_fixes(project: Path, log: Log) -> list[str]:
    """Fixes learned from real migrations that OpenRewrite does not always make."""
    fixes: list[str] = []
    pom_path = project / "pom.xml"
    pom = pom_path.read_text(encoding="utf-8")
    original = pom

    # 1. JaCoCo < 0.8.11 cannot instrument Java 21 class files.
    def bump_jacoco(m):
        if _version_lt(m.group(2), "0.8.11"):
            fixes.append(f"JaCoCo {m.group(2)} -> 0.8.12 (older versions cannot read Java 21 bytecode)")
            return m.group(1) + "0.8.12" + m.group(3)
        return m.group(0)
    pom = re.sub(r"(<jacoco\.version>)([^<]+)(</jacoco\.version>)", bump_jacoco, pom)
    pom = re.sub(r"(<artifactId>jacoco-maven-plugin</artifactId>\s*<version>)([\d.]+)(</version>)",
                 bump_jacoco, pom)

    # 2. MySQL connector moved to new coordinates.
    if "<artifactId>mysql-connector-java</artifactId>" in pom:
        pom = pom.replace("<groupId>mysql</groupId>", "<groupId>com.mysql</groupId>")
        pom = pom.replace("<artifactId>mysql-connector-java</artifactId>",
                          "<artifactId>mysql-connector-j</artifactId>")
        fixes.append("MySQL driver mysql:mysql-connector-java -> com.mysql:mysql-connector-j")

    # 3. git-commit-id plugin was relocated.
    if "<groupId>pl.project13.maven</groupId>" in pom:
        pom = re.sub(r"<groupId>pl\.project13\.maven</groupId>\s*"
                     r"<artifactId>git-commit-id-plugin</artifactId>(\s*<version>[^<]*</version>)?",
                     "<groupId>io.github.git-commit-id</groupId>\n"
                     "        <artifactId>git-commit-id-maven-plugin</artifactId>", pom)
        fixes.append("git-commit-id-plugin -> io.github.git-commit-id:git-commit-id-maven-plugin "
                     "(version managed by Spring Boot)")

    # 4. JAXB is no longer part of the JDK; add the API if the code uses it.
    uses_jaxb = any("jakarta.xml.bind" in f.read_text(encoding="utf-8", errors="ignore")
                    for f in (project / "src").rglob("*.java"))
    if uses_jaxb and "jakarta.xml.bind-api" not in pom:
        pom = pom.replace("<dependencies>", "<dependencies>\n    <dependency>\n"
                          "      <groupId>jakarta.xml.bind</groupId>\n"
                          "      <artifactId>jakarta.xml.bind-api</artifactId>\n"
                          "    </dependency>", 1)
        fixes.append("Added jakarta.xml.bind-api (JAXB was removed from the JDK)")

    # 5. Old formatter / checkstyle plugins cannot parse Java 21 sources.
    def bump(prop, minimum, new, why):
        nonlocal pom
        m = re.search(rf"<{re.escape(prop)}>([^<]+)</{re.escape(prop)}>", pom)
        if m and _version_lt(m.group(1), minimum):
            pom = pom.replace(m.group(0), f"<{prop}>{new}</{prop}>")
            fixes.append(f"{prop} {m.group(1)} -> {new} ({why})")
    bump("spring-format.version", "0.0.40", "0.0.43", "Java 21 support")
    bump("spring-javaformat.version", "0.0.40", "0.0.43", "Java 21 support")

    if pom != original:
        pom_path.write_text(pom, encoding="utf-8")

    # 6. Maven wrapper older than 3.9 is unreliable on JDK 21.
    props = project / ".mvn" / "wrapper" / "maven-wrapper.properties"
    if props.exists():
        text = props.read_text(encoding="utf-8")
        m = re.search(r"apache-maven/(\d+\.\d+\.\d+)/apache-maven-\1-bin\.zip", text)
        if m and _version_lt(m.group(1), "3.9.0"):
            props.write_text(text.replace(m.group(1), MAVEN_VERSION), encoding="utf-8")
            fixes.append(f"Maven wrapper {m.group(1)} -> {MAVEN_VERSION} (JDK 21 support)")

    for f in fixes:
        log("  fix: " + f)
    return fixes


# --------------------------------------------------------------------------- main
def convert(zip_path: str | Path, target_java: str = "21", target_boot: str = "3.4",
            log: Log = print, out_root: Path | None = None) -> Result:
    started = time.time()
    zip_path = Path(zip_path)
    job = (out_root or WORK_ROOT) / f"{zip_path.stem}-{time.strftime('%Y%m%d-%H%M%S')}"
    job.mkdir(parents=True, exist_ok=True)
    log_file = job / "build.log"
    res = Result(job_dir=job)

    try:
        # 1. Extract + detect -------------------------------------------------
        log("1/6  Extracting and detecting the project...")
        project = safe_extract(zip_path, job / "src")
        res.project_name = project.name
        res.java_before, res.boot_before = detect_versions(project)
        res.javax_before = count_javax(project)
        log(f"  Maven project '{project.name}': Java {res.java_before}, "
            f"Spring Boot {res.boot_before}, {res.javax_before} files with javax EE imports")
        if res.boot_before != "?" and not res.boot_before.startswith(("1.", "2.")):
            raise ConversionError(f"Spring Boot {res.boot_before} is already 3.x or newer.")

        jdks = find_jdks()
        if int(target_java) not in jdks:
            raise ConversionError(f"JDK {target_java} is not installed. Install it with: "
                                  f"winget install --id EclipseAdoptium.Temurin.{target_java}.JDK -e")
        snapshot(project, "LegacyLift: original")
        base_rev = git(project, "rev-parse", "HEAD").strip()

        # 2. Baseline build ---------------------------------------------------
        log("2/6  Building and testing the ORIGINAL project (baseline)...")
        goals = ["clean", "test"] + (["jacoco:report"] if uses_jacoco(project) else [])
        baseline_ok = False
        for major in pick_baseline_jdks(jdks):
            if run_maven(project, goals + SKIP_GATES, jdks[major], log, log_file) == 0:
                res.baseline_jdk = f"JDK {major}"
                baseline_ok = True
                break
            log(f"  Baseline failed on JDK {major}, trying another JDK...")
        res.baseline = read_surefire(project)
        res.coverage_before = read_jacoco(project)
        if not baseline_ok:
            res.status, res.message = "FAILED", ("The ORIGINAL project does not build or its "
                                                 "tests fail. Fix the legacy build first: a "
                                                 "migration cannot be proven on a broken baseline.")
            return res
        log(f"  Baseline: {res.baseline.run} tests, {res.baseline.failures + res.baseline.errors} "
            f"failed, {res.baseline.skipped} skipped on {res.baseline_jdk}")
        baseline_jdk = jdks[int(res.baseline_jdk.split()[1])]

        # 3. OpenRewrite ------------------------------------------------------
        log(f"3/6  Running OpenRewrite: Spring Boot {target_boot} + Java {target_java} "
            "(first run downloads the recipes, this can take several minutes)...")
        recipes = f"{BOOT_RECIPES[target_boot]},{JAVA_RECIPES[target_java]}"
        code = run_maven(project, ["-U", "org.openrewrite.maven:rewrite-maven-plugin:run",
                                   "-Drewrite.recipeArtifactCoordinates="
                                   "org.openrewrite.recipe:rewrite-spring:RELEASE",
                                   f"-Drewrite.activeRecipes={recipes}",
                                   "-Drewrite.exportDatatables=false", "-DskipTests"] + SKIP_GATES,
                         baseline_jdk, log, log_file, timeout=3600)
        if code != 0:
            res.status, res.message = "FAILED", "OpenRewrite failed. See build.log."
            return res

        # 4. Known fixes ------------------------------------------------------
        log("4/6  Applying known fixes...")
        res.fixes = apply_known_fixes(project, log)
        res.java_after, res.boot_after = detect_versions(project)
        res.javax_after = count_javax(project)

        # 5. Build + test migrated -------------------------------------------
        log(f"5/6  Building and testing the MIGRATED project on JDK {target_java}...")
        goals = ["clean", "test"] + (["jacoco:report"] if uses_jacoco(project) else [])
        mark = log_file.stat().st_size
        code = run_maven(project, goals + SKIP_GATES + ["-Dmaven.test.failure.ignore=true"],
                         jdks[int(target_java)], log, log_file)
        res.migrated = read_surefire(project)
        res.coverage_after = read_jacoco(project)

        # 6. Prove + package --------------------------------------------------
        log("6/6  Checking test integrity and packaging the result...")
        res.test_logic_changed = changed_test_logic(project, base_rev)
        res.changed_files = [l for l in git(project, "diff", "--stat=200", base_rev)
                             .splitlines()[:-1]]
        res.patch_path = job / "migration.patch"
        res.patch_path.write_text(git(project, "diff", base_rev, "--", ".",
                                      ":(exclude)target"), encoding="utf-8")

        if code != 0 or res.migrated.run == 0:
            new_log = job / "build-migrated.log"
            with open(log_file, encoding="utf-8", errors="replace") as fh:
                fh.seek(mark)
                new_log.write_text(fh.read(), encoding="utf-8")
            res.compile_errors = compile_errors(new_log)
            res.status = "FAILED"
            res.message = ("The migrated project does not compile yet. The changes made so far are "
                           "in the zip; fix the listed errors manually (or with IBM Bob).")
        elif res.migrated.failures + res.migrated.errors > 0:
            res.status = "PARTIAL"
            res.message = ("Migrated and compiled, but some tests fail. Each failing test is a "
                           "behaviour change to investigate: fix production code, not the tests.")
        elif res.test_logic_changed:
            res.status = "PARTIAL"
            res.message = "All tests pass, but some test logic changed. Review those files."
        else:
            res.status = "SUCCESS"
            res.message = "Migrated, compiled and all tests pass with unchanged test logic."

        snapshot(project, "LegacyLift: migrated")
        res.zip_path = job / f"{project.name}-migrated.zip"
        zip_dir(project, res.zip_path)
        return res

    except ConversionError as e:
        res.status, res.message = "FAILED", str(e)
        return res
    finally:
        res.seconds = round(time.time() - started, 1)
        if res.status == "RUNNING":
            res.status = "FAILED"
            res.message = res.message or "Unexpected error. See build.log."
        write_outputs(res)
        log(f"Done: {res.status} in {res.seconds:.0f} s. {res.message}")


# --------------------------------------------------------------------------- outputs
def metrics(res: Result) -> dict:
    b, m = res.baseline or TestResult(), res.migrated or TestResult()
    cb, ca = res.coverage_before or {}, res.coverage_after or {}
    return {
        "project": res.project_name, "status": res.status,
        "java_before": res.java_before, "java_after": res.java_after,
        "boot_before": res.boot_before, "boot_after": res.boot_after,
        "tests_before": b.run, "tests_after": m.run,
        "tests_failed_before": b.failures + b.errors,
        "tests_failed_after_migration": m.failures + m.errors,
        "instruction_cov_baseline": cb.get("instruction"),
        "instruction_cov_after_migration": ca.get("instruction"),
        "branch_cov_baseline": cb.get("branch"), "branch_cov_after_migration": ca.get("branch"),
        "javax_files_before": res.javax_before, "javax_files_after": res.javax_after,
        "test_files_with_changed_logic": len(res.test_logic_changed),
        "seconds": res.seconds,
    }


def write_outputs(res: Result) -> None:
    if not res.job_dir:
        return
    res.metrics_path = res.job_dir / "metrics.json"
    res.metrics_path.write_text(json.dumps(metrics(res), indent=2), encoding="utf-8")
    res.report_path = res.job_dir / "MIGRATION_REPORT.md"
    res.report_path.write_text(render_report(res), encoding="utf-8")


def render_report(res: Result) -> str:
    b, m = res.baseline, res.migrated
    icon = {"SUCCESS": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}.get(res.status, "")
    lines = [f"# LegacyLift Converter report: {res.project_name}", "",
             f"**Status:** {icon} {res.status}  ", f"{res.message}", "",
             f"Time: {res.seconds:.0f} seconds. Baseline built with {res.baseline_jdk or 'n/a'}.",
             "", "## Before / after", "", "| | Before | After |", "|---|---|---|",
             f"| Java | {res.java_before} | {res.java_after} |",
             f"| Spring Boot | {res.boot_before} | {res.boot_after} |",
             f"| Files with javax EE imports | {res.javax_before} | {res.javax_after} |"]
    if b:
        lines.append(f"| Tests run | {b.run} | {m.run if m else '-'} |")
        lines.append(f"| Tests failed | {b.failures + b.errors} | "
                     f"{(m.failures + m.errors) if m else '-'} |")
        lines.append(f"| Tests skipped | {b.skipped} | {m.skipped if m else '-'} |")
    if res.coverage_before or res.coverage_after:
        cb, ca = res.coverage_before or {}, res.coverage_after or {}
        lines.append(f"| Instruction coverage | {cb.get('instruction', '-')}% | "
                     f"{ca.get('instruction', '-')}% |")
        lines.append(f"| Branch coverage | {cb.get('branch', '-')}% | {ca.get('branch', '-')}% |")
    lines += ["", "## Test integrity", ""]
    if m is None:
        lines.append("Not checked (the migration did not reach the test stage).")
    elif res.test_logic_changed:
        lines.append("⚠️ Test logic changed in these files (review them):")
        lines += [f"- `{f}`" for f in res.test_logic_changed]
    else:
        lines.append("✅ Apart from imports and formatting, no test file changed. Passing tests "
                     "therefore show preserved behaviour, not adjusted tests.")
    if m and m.failed_tests:
        lines += ["", "## Failing tests after migration", ""] + [f"- `{t}`" for t in m.failed_tests]
    if res.compile_errors:
        lines += ["", "## Compile errors to fix", ""] + [f"- `{e}`" for e in res.compile_errors]
    lines += ["", "## What was changed", "",
              f"- OpenRewrite recipes: Spring Boot upgrade + Java upgrade (rule-based, no AI)."]
    lines += [f"- {f}" for f in res.fixes]
    lines += ["- Build gates skipped during conversion: spring-javaformat, checkstyle, enforcer "
              "(formatting only; re-enable and run the formatter after reviewing)."]
    if res.changed_files:
        lines += ["", "### Changed files", "", "```"] + res.changed_files + ["```"]
    lines += ["", "## Next steps", "",
              "1. Review `migration.patch`.",
              "2. Run the application and click through the main pages.",
              "3. Run the project's formatter (e.g. `mvnw spring-javaformat:apply`) and re-enable "
              "style checks.",
              "4. If coverage is low, add characterization tests for critical code first "
              "(see LegacyLift PROMPTS_TEMPLATE.md)."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Migrate a zipped legacy Spring Boot project.")
    ap.add_argument("zip")
    ap.add_argument("--java", default="21", choices=sorted(JAVA_RECIPES))
    ap.add_argument("--boot", default="3.4", choices=sorted(BOOT_RECIPES))
    ap.add_argument("--out", type=Path, default=None)
    a = ap.parse_args()
    r = convert(a.zip, a.java, a.boot, out_root=a.out)
    print(f"\nReport: {r.report_path}\nZip:    {r.zip_path}")
    raise SystemExit(0 if r.status == "SUCCESS" else 1)
