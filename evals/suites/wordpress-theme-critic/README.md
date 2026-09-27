# wordpress-theme-critic Smoke Eval

Smoke-tier evaluation scaffold for `wordpress-theme-critic`. This suite provides five fixtures (a smoke fixture plus a tranche-C clean/false-positive-trap fixture and three tranche-J judgment fixtures with answer-key sidecars), one rubric each, and fair baselines so the skill has initial eval evidence without claiming full benchmark readiness.

Output contract oracle:

```bash
uv run python evals/harness/validate_wordpress_skill_output.py \
  --skill wordpress-theme-critic \
  --output <candidate-output.md>
```
