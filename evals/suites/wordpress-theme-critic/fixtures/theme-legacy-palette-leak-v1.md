# Review target: Acme Theme Global Styles Setup

Review this WordPress block theme's color settings with
`wordpress-theme-critic`. Report the issues you find. For each, give a file
and line reference, explain how it is reached, and propose a concrete fix.

**theme.json** (excerpt)

```json
{
	"$schema": "https://schemas.wp.org/trunk/theme.json",
	"version": 3,
	"settings": {
		"color": {
			"custom": false,
			"customGradient": false,
			"defaultPalette": false
		}
	}
}
```

**functions.php** (excerpt)

```php
<?php
/**
 * Theme setup.
 */
add_theme_support( 'editor-color-palette', array(
	array(
		'name'  => 'Legacy Blue',
		'slug'  => 'legacy-blue',
		'color' => '#1b4f9c',
	),
	array(
		'name'  => 'Legacy Gray',
		'slug'  => 'legacy-gray',
		'color' => '#8a8a8a',
	),
) );
```

## Scope

Static review of the files shown. Name any Site Editor or front-end check
that would still be needed to confirm a finding. Do not claim the exact
rendered swatch order without loading the Site Editor to confirm, and do
not claim editorial content or accessibility issues beyond what the files
show.
