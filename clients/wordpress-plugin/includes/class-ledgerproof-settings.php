<?php
/**
 * Admin settings page for the LedgerProof plugin.
 */

if (!defined('ABSPATH')) exit;

class LedgerProof_Settings {
    public function __construct() {
        add_action('admin_menu', array($this, 'add_menu'));
        add_action('admin_init', array($this, 'register_settings'));
    }

    public function add_menu(): void {
        add_options_page(
            'LedgerProof Settings',
            'LedgerProof',
            'manage_options',
            'ledgerproof',
            array($this, 'render_page')
        );
    }

    public function register_settings(): void {
        register_setting('ledgerproof_group', 'ledgerproof_options', array(
            'sanitize_callback' => array($this, 'sanitize'),
        ));

        add_settings_section(
            'ledgerproof_main',
            'LedgerProof configuration',
            function () {
                echo '<p>Configure your publisher credentials. The API key is provisioned by your LedgerProof operator.</p>';
            },
            'ledgerproof'
        );

        $fields = array(
            'api_key'           => array('label' => 'API key (lp_…)',      'type' => 'password'),
            'publisher_id'      => array('label' => 'Publisher ID',        'type' => 'text'),
            'deployer_country'  => array('label' => 'Deployer country',    'type' => 'text', 'hint' => 'ISO 3166-1 alpha-2, e.g., DE'),
            'deployer_name'     => array('label' => 'Deployer name',       'type' => 'text'),
            'api_base'          => array('label' => 'API base URL',        'type' => 'text', 'hint' => 'Defaults to https://api-eu.ledgerproofhq.io'),
            'auto_issue'        => array('label' => 'Auto-issue on publish', 'type' => 'checkbox'),
            'is_public_interest' => array('label' => 'Public-interest content', 'type' => 'checkbox', 'hint' => 'Tags receipts as Article 50(4) public-interest text'),
        );
        foreach ($fields as $key => $config) {
            add_settings_field(
                'ledgerproof_' . $key,
                $config['label'],
                array($this, 'render_field'),
                'ledgerproof',
                'ledgerproof_main',
                array_merge(array('name' => $key), $config)
            );
        }
    }

    public function render_field($args): void {
        $opts = get_option('ledgerproof_options', array());
        $name = $args['name'];
        $value = $opts[$name] ?? '';
        if ($args['type'] === 'checkbox') {
            $checked = $value === '1' ? 'checked' : '';
            echo "<input type='checkbox' name='ledgerproof_options[$name]' value='1' $checked />";
        } else {
            $escaped = esc_attr($value);
            echo "<input type='{$args['type']}' name='ledgerproof_options[$name]' value='$escaped' class='regular-text' />";
        }
        if (!empty($args['hint'])) {
            echo "<p class='description'>{$args['hint']}</p>";
        }
    }

    public function sanitize($input) {
        $output = array();
        $output['api_key'] = sanitize_text_field($input['api_key'] ?? '');
        $output['publisher_id'] = sanitize_text_field($input['publisher_id'] ?? '');
        $output['deployer_country'] = strtoupper(substr(sanitize_text_field($input['deployer_country'] ?? ''), 0, 2));
        $output['deployer_name'] = sanitize_text_field($input['deployer_name'] ?? '');
        $output['api_base'] = esc_url_raw($input['api_base'] ?? LEDGERPROOF_API_BASE_DEFAULT);
        $output['auto_issue'] = !empty($input['auto_issue']) ? '1' : '0';
        $output['is_public_interest'] = !empty($input['is_public_interest']) ? '1' : '0';
        return $output;
    }

    public function render_page(): void {
        ?>
        <div class="wrap">
            <h1>LedgerProof</h1>
            <p>EU AI Act Article 50 compliance receipts for AI-assisted content on your WordPress site.</p>
            <form method="post" action="options.php">
                <?php
                settings_fields('ledgerproof_group');
                do_settings_sections('ledgerproof');
                submit_button();
                ?>
            </form>
        </div>
        <?php
    }
}
