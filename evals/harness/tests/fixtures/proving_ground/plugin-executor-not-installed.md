## Spec Conformance
Implements the approved wordpress-plugin-planner spec for the editorial review
plugin exactly; no deviations from Delivery unit: client-custom-plugin.

## Generated File Map
client-custom-plugin.php, includes/class-admin-settings.php,
includes/class-rest-controller.php

## Implementation Packets
The bootstrap file calls `register_post_type()` and `register_setting()`. The
REST controller calls `register_rest_route()` and gates access with
`check_admin_referer()`.

## Security Notes
Input passes through `sanitize_text_field()`; nonce verification uses
`wp_verify_nonce()`. This does not claim coverage of third-party integrations
outside this plugin's boundary.

## Deviation Log
No deviations from the approved plan.

## Verification Notes
Run PHPUnit and a Playwright admin smoke before release.

Proving ground: not installed

NOT CHECKED: validate_wordpress_executor_packet.py (no proving ground root resolved)
NOT CHECKED: materialize_wordpress_executor_packet.py (no proving ground root resolved)
NOT CHECKED: validate_wordpress_artifact.py (no proving ground root resolved)

Set up the proving ground: install uv (https://docs.astral.sh/uv/) and run `[ -d ~/wp-ai-skills ] || git clone https://github.com/zivtech/wp-ai-skills ~/wp-ai-skills; ~/wp-ai-skills/install.sh --harness-only`.

## Critic Handoff
Send the packet to wordpress-critic and wordpress-security-critic.
