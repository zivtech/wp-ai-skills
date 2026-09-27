# Review target: Acme Theme Block Styling Enqueue

Review this WordPress block theme's block-styling enqueue with
`wordpress-theme-critic`. Report the issues you find. For each, give a file
and line reference, explain how it is reached, and propose a concrete fix.

**functions.php** (excerpt)

```php
<?php
/**
 * Theme block styling.
 */
function acme_enqueue_block_styles() {
	wp_enqueue_style(
		'acme-block-styles',
		get_theme_file_uri( 'assets/css/blocks.css' ),
		array(),
		wp_get_theme()->get( 'Version' )
	);
}
add_action( 'wp_enqueue_scripts', 'acme_enqueue_block_styles' );
```

**assets/css/blocks.css** (excerpt)

```css
.wp-block-button__link {
	border-radius: 0;
	text-transform: uppercase;
}

.wp-block-quote {
	border-left: 4px solid var( --wp--preset--color--accent );
	padding-left: 1.5rem;
}
```

## Scope

Static review of the files shown. Name any Site Editor check that would
still be needed to confirm a finding. Do not claim the exact rendered pixel
difference without loading the Site Editor to compare, and do not claim
editorial content or accessibility issues beyond what the files show.
