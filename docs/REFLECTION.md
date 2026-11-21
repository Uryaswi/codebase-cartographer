# HW4 Reflection — Codebase Cartographer

*Target: 1–2 pages. Replace every prompt in italics with your own experience.
Specific moments beat general statements.*

## 1. Project summary (2–3 sentences)
*What Cartographer does, which feature you built with Explore → Plan →
Implement → Commit (hotspots) and which with TDD (change coupling).*

## 2. Explore → Plan → Implement → Commit vs. my previous approach
*How did you work with AI coding tools before? (e.g. "ask for the whole
feature in one prompt, then debug what came back")*

*Explore: what did Claude find during exploration that changed the plan?*

*Plan: what did you push back on in Plan mode, and why? Did the plan catch
an edge case early that would have been a bug later?*

*Implement + Commit: how did small, planned steps change the quality of the
code and the git history compared to one big change?*

*Cost: where did the workflow feel slow or like overkill? When would you
skip a phase?*

## 3. TDD through Claude Code
*Did Claude respect "tests only" during RED and "don't edit tests" during
GREEN? Describe a moment it tried to cut a corner, if any.*

*Did writing tests first surface ambiguity in the requirements (e.g. ordering
ties, rounding, what counts as a large commit)?*

*How useful were the REFACTOR steps? Were any skipped honestly?*

## 4. Context management: what worked best
*CLAUDE.md + @imports: did Claude follow the rules without being reminded?
What did /init get right or miss compared to your final version?*

*/clear: when did you use it, and what difference did it make?*

*/compact: what focus text did you give, and what did Claude still remember
afterwards?*

*--continue: did resuming preserve enough context to keep going mid-TDD?*

*Permissions vs. CLAUDE.md: what's the difference between a "don't" in
CLAUDE.md and a deny rule? (the denied git push is good evidence)*

## 5. What I'd do differently
*One or two concrete changes for P3 going forward.*

## Appendix
- Annotated session log: `docs/session-logs/annotated-session-log.md`
- Key commits: *paste `git log --oneline` here*
