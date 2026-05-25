<?php
/**
 * Plugin Name: LedgerProof
 * Plugin URI: https://ledgerproofhq.io
 * Description: EU AI Act Article 50 compliance for WordPress. Auto-issues an LPR receipt when you publish AI-assisted content.
 * Version: 1.0.0
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Author: LedgerProof Foundation
 * Author URI: https://ledgerproofhq.io
 * License: Apache-2.0
 * License URI: https://www.apache.org/licenses/LICENSE-2.0
 * Text Domain: ledgerproof
 */

if (!defined('ABSPATH')) {
    exit; // No direct access.
}

define('LEDGERPROOF_VERSION', '1.0.0');
define('LEDGERPROOF_API_BASE_DEFAULT', 'https://api-eu.ledgerproofhq.io');

require_once __DIR__ . '/includes/class-ledgerproof-client.php';
require_once __DIR__ . '/includes/class-ledgerproof-settings.php';
require_once __DIR__ . '/includes/class-ledgerproof-publisher.php';

// Initialize on plugins_loaded so WP core is ready.
add_action('plugins_loaded', function () {
    new LedgerProof_Settings();
    new LedgerProof_Publisher();
});

// Activation: ensure the default option set exists.
register_activation_hook(__FILE__, function () {
    add_option('ledgerproof_options', array(
        'api_key'           => '',
        'publisher_id'      => '',
        'deployer_country'  => 'DE',
        'deployer_name'     => get_bloginfo('name'),
        'api_base'          => LEDGERPROOF_API_BASE_DEFAULT,
        'auto_issue'        => '1',
        'is_public_interest' => '0',
    ));
});

// Uninstall: remove plugin options. (Triggered by uninstall.php in production.)
