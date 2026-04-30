# Latest Plan: GitLab Housekeeping Policy Simulator

## North Star

Build a **GitLab Housekeeping Policy Simulator**, not an “active-cap proof.”

Purpose:

```text
Compare merge-queue policies under controlled GitLab-like conditions:
old per-run limit, top-K eligibility, active-cap CI inventory, and Phase 1 optimistic multi-merge.
```

Primary question:

```text
What does each policy optimize, and under which queue conditions does it fail?
```

The simulator should support fair scenarios where:

```text
top-K wins
active-cap wins
both are similar
Phase 1 multi-merge wins
Phase 1 is blocked by overlap/conflict
priority preemption might matter
```

This keeps the work clean and prevents overfitting the tool to one argument.

---

# 1. Core Invariant From ADR-019

The simulator should center this invariant:

```text
limit controls steady-state CI concurrency, not per-run rebase bursts.
```

Equivalent framing:

```text
top-K controls eligibility.
active-cap controls useful in-flight CI inventory.
Phase 1 multi-merge consumes same-root green inventory.
```

The simulator should make that distinction measurable.

---

# 2. Policy Families To Simulate

## Policy A: Old Per-Run Burst

Current/old behavior shape:

```text
Each reconcile run can rebase up to limit MRs.
The limit resets every run.
Over time, active CI can exceed the intended cap.
```

Measures:

```text
rebase burst churn
duplicate rebases
stale pipelines
peak active pipelines
```

---

## Policy B: Top-K Eligibility

Behavior:

```text
Only the first K sorted MRs are eligible for rebase/CI work.
```

Optimizes:

```text
strict queue-position visibility
simple bounded eligibility
priority purity
```

Possible weakness:

```text
top-K window can be occupied by slow/flaky/blocked/stale candidates,
while lower candidates that could fill useful CI slots remain invisible.
```

---

## Policy C: Active-Cap CI Inventory

Behavior:

```text
Count already-active/useful candidates.
Only rebase enough MRs to fill remaining budget.
Refill slots by priority as they free up.
```

Optimizes:

```text
steady-state CI concurrency
useful CI inventory
reduced wasted rebases
future same-root success pool
```

Possible weakness:

```text
new high-priority MRs may wait for next slot instead of preempting active work.
```

---

## Policy D: Phase 1 Optimistic Multi-Merge

Behavior:

```text
Use same-root successful MRs.
Merge multiple non-overlapping candidates in one batch.
Avoid target-head invalidation for safe independent changes.
```

Optimizes:

```text
MRs merged per target advancement
total queue throughput
reduced one-merge-per-pipeline-cycle ceiling
```

Requires:

```text
same-root green pool
tenant/change-domain overlap detection
merge_limit
safe batch semantics
```

---

# 3. Simulator Architecture

```text
scenario YAML
    ↓
stateful fake GitLab API server
    ↓
real unmodified gitlab-housekeeping integration
    ↓
state mutations: rebase / merge / pipeline / target head
    ↓
metrics NDJSON
    ↓
single-run + policy comparison reports
```

No modification to `run()`.

No monkeypatching.

No reverse proxy.

The fake GitLab server should be compatible enough with the real `python-gitlab` path used by `qontract-reconcile`.

---

# 4. Repo Layout

```text
tools/gitlab_housekeeping_perf_sim/
  README.md
  pyproject.toml

  gitlab_hk_sim/
    __init__.py
    cli.py
    scenario.py
    state.py
    server.py
    endpoints.py
    mutations.py
    metrics.py
    report.py
    gitlab_shapes.py
    policies.py
    phase1.py

  scenarios/
    mvp-active-cap.yaml
    top-k-favorable.yaml
    top-k-poisoned-window.yaml
    high-priority-arrival.yaml
    clean-nonoverlap-phase1.yaml
    overlap-conflict-phase1.yaml
    long-running-ci.yaml
    external-target-advance.yaml

  reports/
    .gitkeep

  tests/
    test_state.py
    test_mutations.py
    test_metrics.py
    test_phase1.py
    test_gitlab_shapes.py
```

Use FastAPI/uvicorn unless dependency policy makes that annoying.

---

# 5. CLI

```bash
python -m gitlab_hk_sim.cli serve \
  --scenario scenarios/top-k-poisoned-window.yaml \
  --host 127.0.0.1 \
  --port 8080 \
  --metrics-out reports/active-cap/metrics.ndjson
```

```bash
python -m gitlab_hk_sim.cli report \
  --metrics reports/active-cap/metrics.ndjson \
  --out reports/active-cap/summary.md
```

```bash
python -m gitlab_hk_sim.cli compare \
  --run old=reports/old/metrics.ndjson \
  --run top-k=reports/top-k/metrics.ndjson \
  --run active-cap=reports/active-cap/metrics.ndjson \
  --run phase1=reports/phase1/metrics.ndjson \
  --out reports/comparison.md
```

Optional:

```bash
python -m gitlab_hk_sim.cli validate \
  --scenario scenarios/top-k-poisoned-window.yaml
```

---

# 6. Minimum GitLab API Surface

Implement only what housekeeping hits.

```text
GET  /api/v4/user
GET  /api/v4/personal_access_tokens

GET  /api/v4/groups/:id_or_path
GET  /api/v4/groups/:id/members

GET  /api/v4/projects/:id_or_encoded_path
GET  /api/v4/projects/:id/issues
GET  /api/v4/projects/:id/merge_requests
GET  /api/v4/projects/:id/merge_requests/:iid
GET  /api/v4/projects/:id/merge_requests/:iid/commits
GET  /api/v4/projects/:id/merge_requests/:iid/resource_label_events
GET  /api/v4/projects/:id/merge_requests/:iid/pipelines

GET  /api/v4/projects/:id/repository/commits
GET  /api/v4/projects/:id/repository/compare

PUT  /api/v4/projects/:id/merge_requests/:iid
PUT  /api/v4/projects/:id/merge_requests/:iid/rebase
PUT  /api/v4/projects/:id/merge_requests/:iid/merge

GET  /api/v4/projects/:id/pipelines/:pipeline_id
POST /api/v4/projects/:id/pipelines/:pipeline_id/cancel

POST /__sim/tick
GET  /__sim/metrics
GET  /__sim/state
POST /__sim/reset
```

Return GitLab-compatible pagination headers on list endpoints.

---

# 7. Core State Model

## Project

```yaml
project:
  id: 1001
  name: sim-repo
  path: sim-repo
  path_with_namespace: app-sre/sim-repo
  web_url: http://127.0.0.1:8080/app-sre/sim-repo
  default_branch: master
  squash_option: default_on
  target_head: target-001
```

## MR

```yaml
merge_requests:
  - id: 2001
    iid: 1
    title: "MR 1"
    state: opened
    draft: false
    merge_status: can_be_merged
    target_branch: master
    source_branch: sim/mr-1
    source_project_id: 1001
    target_project_id: 1001
    sha: mr1-sha-001
    rebased_target_sha: target-001
    labels: ["lgtm", "tenant-a"]
    tenant_domains: ["tenant-a"]
    pipelines:
      - id: 5001
        status: success
        sha: mr1-sha-001
        root_sha: target-001
```

## Pipeline

```yaml
pipelines:
  - id: 5001
    status: running
    sha: mr1-sha-001
    root_sha: target-001
    pending_ticks_remaining: 0
    running_ticks_remaining: 4
    outcome: success
```

## SHA Pools

Use captured/imported SHAs when available. Generate fallback synthetic SHAs only when the sim creates counterfactual state not present in the scenario.

```yaml
sha_pools:
  mr_rebases:
    "3": ["mr3-sha-rebased-001", "mr3-sha-rebased-002"]
  target_advances:
    master: ["target-002", "target-003"]
```

---

# 8. Essential Semantics

## Repository Compare

This is critical.

```text
GET /api/v4/projects/:id/repository/compare?from=<mr_sha>&to=<target_head>
```

Logic:

```python
if mr.rebased_target_sha == to:
    return {"commits": []}
else:
    return {"commits": [synthetic_commit]}
```

Meaning:

```text
commits == []  -> housekeeping considers MR rebased
commits != []  -> housekeeping considers MR not rebased
```

---

## Rebase Mutation

On:

```text
PUT /api/v4/projects/:id/merge_requests/:iid/rebase
```

Do:

```text
1. Select next MR branch SHA from sha_pools; fallback synthetic.
2. Set MR.sha to selected SHA.
3. Set MR.rebased_target_sha = current target_head.
4. Append commit object.
5. Create pending pipeline:
   - sha = MR.sha
   - root_sha = current target_head
   - status = pending
6. Record metrics.
```

---

## Merge Mutation

On:

```text
PUT /api/v4/projects/:id/merge_requests/:iid/merge
```

Do:

```text
1. Mark MR merged.
2. Select next target SHA from sha_pools; fallback synthetic.
3. Advance project.target_head.
4. Previously successful pipelines with old root become stale.
5. Record metrics.
```

---

## Tick

On:

```text
POST /__sim/tick
```

Do:

```text
pending -> running -> success/failed
recompute active pipeline count
recompute same-root success pool
recompute stale successes
emit metrics snapshot
```

---

# 9. Phase 1 Multi-Merge Model

Add lightweight Phase 1 support now, even if the first demo only partially uses it.

Scenario config:

```yaml
phase1:
  enabled: true
  merge_limit: 5
  conflict_key: tenant_domains
```

Each MR has:

```yaml
tenant_domains: ["tenant-a"]
```

Safe co-merge rule:

```text
Two MRs are co-mergeable if their tenant_domains do not overlap.
```

Phase 1 merge candidate selection:

```text
1. Find open MRs with successful pipelines.
2. Require pipeline.root_sha == current target_head.
3. Require MR.rebased_target_sha == current target_head.
4. Sort by queue priority.
5. Build merge batch:
   - include first eligible MR
   - include later MRs only if tenant_domains do not overlap with already selected batch
   - stop at merge_limit
6. Merge batch.
```

For the simulator, batch merge can be represented either as:

```text
A. multiple merge endpoint calls before target advances
```

or:

```text
B. internal Phase 1 policy mode that merges batch and advances target once
```

For realism against current housekeeping, start with A for normal integration testing. For policy-lab mode, support B.

Phase 1 metrics:

```text
same_root_success_pool_size
co_mergeable_success_pool_size
multi_merge_batch_size
merge_batches_completed
average_mrs_per_target_advance
target_advances_per_merged_mr
overlap_blocked_successes
serial_vs_multi_merge_delta
```

Most important Phase 1 metric:

```text
average_mrs_per_target_advance
```

Serial behavior:

```text
~1 MR per target advance
```

Phase 1 goal:

```text
>1 non-overlapping MRs per target advance
```

---

# 10. Scenario Families

## Scenario 1: Top-K Favorable

Purpose:

```text
Show where top-K is simple and good.
```

Shape:

```text
Top K MRs are clean, fast, valid candidates.
No poisoned/flaky/blocked top window.
No useful candidates below K needed.
```

Expected:

```text
top-K looks good
active-cap similar
old may over-rebase across runs
```

---

## Scenario 2: Top-K Poisoned Window

Purpose:

```text
Show top-K can preserve queue purity while starving useful CI inventory.
```

Shape:

```text
limit = 5

MR 1: running long
MR 2: running long
MR 3: failed
MR 4: non-rebased but running/stuck
MR 5: pending/stuck

MR 6-10: clean candidates outside top-K
```

Expected:

```text
top-K:
  sees top 5 only
  may underfill useful same-root success pool

active-cap:
  accounts for active/success slots
  refills available budget by priority
```

README line:

```text
This scenario demonstrates that top-K can preserve queue priority while starving useful CI inventory. Active-cap preserves the repo-level concurrency invariant and refills useful slots by priority.
```

---

## Scenario 3: High-Priority Arrival

Purpose:

```text
Show the priority preemption tradeoff fairly.
```

Shape:

```text
limit = 2
two lower-priority MRs have long-running pipelines
new high-priority MR appears
```

Expected:

```text
top-K/preemptive model:
  starts high-priority MR earlier

active-cap:
  waits for next slot

comparison:
  measure high-priority time-to-start / time-to-merge
  measure wasted CI and pool impact
```

This is the scenario that fairly represents hemslo/fishi0x01’s concern.

---

## Scenario 4: Long-Running CI

Purpose:

```text
Show slot starvation and queue behavior under slow pipelines.
```

Expected:

```text
top-K may freeze if top K are slow
active-cap protects concurrency but non-preemptive behavior may delay new arrivals
metrics decide the tradeoff
```

---

## Scenario 5: External Target Advance

Purpose:

```text
Show stale success blast radius when target moves outside housekeeping.
```

Expected:

```text
all policies suffer some stale success
active-cap should limit blast radius
old burst behavior likely wastes more
```

---

## Scenario 6: Clean Non-Overlap Phase 1

Purpose:

```text
Show why same-root success pool matters.
```

Shape:

```text
MR 1: tenant-a, success on target-001
MR 2: tenant-b, success on target-001
MR 3: tenant-c, success on target-001
MR 4: tenant-d, success on target-001
```

Expected:

```text
serial:
  1 MR per target advance

phase1:
  multiple MRs per target advance

active-cap + phase1:
  best throughput when same-root pool is maintained
```

---

## Scenario 7: Overlap Conflict Phase 1

Purpose:

```text
Show Phase 1 does not magically merge everything.
```

Shape:

```text
MR 1: tenant-a
MR 2: tenant-a
MR 3: tenant-b
MR 4: tenant-c
```

Expected:

```text
phase1 merges MR 1, MR 3, MR 4
phase1 blocks MR 2 due to overlap
overlap_blocked_successes increments
```

---

# 11. Metrics

## API Metrics

```text
total_requests
request_count_by_endpoint
merge_request_list_calls
repository_compare_calls
pipeline_list_calls
label_event_calls
commit_list_calls
rebase_endpoint_calls
merge_endpoint_calls
pipeline_cancel_calls
```

## CI / Queue Metrics

```text
rebase_calls
merge_calls
pipelines_created
peak_active_pipelines
active_pipeline_count_by_tick
same_root_success_pool_size_by_tick
same_root_success_pool_p50
same_root_success_pool_p95
same_root_success_pool_max
same_root_success_pool_min_over_active_windows
stale_success_count
duplicate_rebases_per_mr
wasted_pipeline_count
time_to_first_merge
time_to_merge_top_N
high_priority_time_to_start
high_priority_time_to_merge
```

## Phase 1 Metrics

```text
co_mergeable_success_pool_size
multi_merge_batch_size
merge_batches_completed
average_mrs_per_target_advance
target_advances_per_merged_mr
overlap_blocked_successes
```

## Definitions

```text
active pipeline:
  pending or running

useful successful pipeline:
  MR is open
  pipeline.status == success
  pipeline.root_sha == current target_head
  MR.rebased_target_sha == current target_head

same_root_success_pool_size:
  count of open MRs with useful successful pipelines for current target_head

stale success:
  pipeline.status == success
  pipeline.root_sha != current target_head

wasted pipeline:
  canceled pipeline
  OR stale success
  OR pipeline for MR that was rebased again before merge
```

---

# 12. Reports

## Single-Run Report

Sections:

```text
1. Scenario summary
2. Policy branch / git SHA under test
3. API call summary
4. Rebase / merge summary
5. Active pipeline pressure
6. Same-root success pool
7. Stale / wasted CI
8. Priority delay metrics
9. Phase 1 batch metrics, if enabled
10. Interpretation
```

## Comparison Report

```markdown
| policy | API calls | compare calls | pipeline calls | rebases | pipelines created | peak active | same-root green p95 | stale successes | duplicate rebase p95 | high-prio TTM | avg MRs / target advance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| old |  |  |  |  |  |  |  |  |  |  |  |
| top-K |  |  |  |  |  |  |  |  |  |  |  |
| active-cap |  |  |  |  |  |  |  |  |  |  |  |
| phase1 |  |  |  |  |  |  |  |  |  |  |  |
```

Interpretation should avoid advocacy language. Use:

```text
This scenario favors top-K because...
This scenario favors active-cap because...
This scenario shows the preemption tradeoff...
This scenario shows Phase 1 dependency on same-root pool...
```

---

# 13. Tomorrow MVP Delivery

Do not attempt the 8-hour importer tomorrow.

Deliver:

```text
1. Fake GitLab server starts from YAML.
2. Real housekeeping can list/preprocess MRs.
3. Real housekeeping can call repository compare.
4. Real housekeeping can list MR pipelines.
5. Real housekeeping can call rebase.
6. Rebase creates pipeline and updates MR state.
7. Tick advances pipeline state.
8. Merge can advance target head.
9. Metrics report shows:
   - rebase calls
   - active pipelines
   - same-root success pool
   - stale successes
   - duplicate rebases
```

Stretch for tomorrow:

```text
top_k_poisoned_window scenario
clean_nonoverlap_phase1 scenario schema
Phase 1 metric stubs
```

---

# 14. Build Order

## Phase 1: Server Boots

```text
scenario loader
state model
GET /user
GET /projects/:id_or_path
GET /merge_requests
pagination headers
```

Done when curl works.

---

## Phase 2: Real Client Compatibility

Add as errors surface:

```text
GET /personal_access_tokens
GET /issues
GET /groups/:id_or_path
GET /groups/:id/members
GET /merge_requests/:iid/commits
GET /merge_requests/:iid/resource_label_events
```

Done when housekeeping completes preprocessing.

---

## Phase 3: Rebase Path

```text
GET /repository/commits
GET /repository/compare
GET /merge_requests/:iid/pipelines
PUT /merge_requests/:iid/rebase
```

Done when housekeeping calls fake rebase endpoint.

---

## Phase 4: Pipeline Tick + Metrics

```text
POST /__sim/tick
GET /__sim/metrics
metrics NDJSON
```

Done when pipeline state advances.

---

## Phase 5: Merge Path

```text
PUT /merge_requests/:iid/merge
target_head advancement
stale success calculation
```

Done when target movement affects same-root pool.

---

## Phase 6: Reports

```text
single-run summary
comparison report
```

---

# 15. Final Acceptance Criteria

The project is successful when:

```text
1. Real unmodified gitlab-housekeeping can run against the fake GitLab server.
2. The simulator mutates state on rebase/merge/cancel.
3. Pipeline status evolves over ticks.
4. Target-head movement makes old successes stale.
5. Metrics expose active CI inventory and same-root green pool.
6. Scenarios cover top-K-favorable, active-cap-favorable, preemption, and Phase 1 multi-merge.
7. Reports compare policies without hiding tradeoffs.
```

That’s the latest shape: **not a proof weapon — a policy lab**.
