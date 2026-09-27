## Detected Environment

No proving ground root resolved, so the environment probe never ran. Whether
the target project uses wp-env, DDEV, or another runtime, and which marker
file it has (`.wp-env.json`, `.ddev/config.yaml`), is UNKNOWN. The probe
oracle is `evals/harness/probe_wordpress_environment.py`; it was never
invoked, so no `wp-env run cli wp --info` (or equivalent) call happened.

## Capability Summary

can_run_wp_cli UNKNOWN; can_run_plugin_check UNKNOWN; can_run_static_analysis
UNKNOWN. No `WP-CLI` command, `Plugin Check` run, or static analyzer answered
`--version`, so none of these capabilities is measured; reporting a version
number or a true/false value for any of them without running the probe would
be an invented fact.

## Blockers

proving_ground_not_installed (MAJOR): no proving ground root resolved, so the
probe never ran and every capability above stays UNKNOWN until it does.

## Evidence

No evidence was gathered because the probe did not run: there is no `wp
plugin list --format=json` or `wp core is-installed` result to cite, and none
is claimed.

Proving ground: not installed

NOT CHECKED: probe_wordpress_environment.py (no proving ground root resolved)

Set up the proving ground: install uv (https://docs.astral.sh/uv/) and run `[ -d ~/wp-ai-skills ] || git clone https://github.com/zivtech/wp-ai-skills ~/wp-ai-skills; ~/wp-ai-skills/install.sh --harness-only`.

## Downstream Handoff

Do not pass a capability manifest to `validate_wordpress_skill_output.py`;
none was produced. Install the proving ground and rerun the probe before any
downstream planner, executor, or critic skill runs against this project.
