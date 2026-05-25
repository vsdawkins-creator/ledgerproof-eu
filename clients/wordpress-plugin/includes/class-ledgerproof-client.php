<?php
/**
 * Minimal LPR client for WordPress. Issues ai/article-50/v1 receipts.
 *
 * Note: this PHP client signs locally with an ephemeral Ed25519 key per request.
 * The signing key is stored in wp-content as ledgerproof-signing-key.bin with
 * file mode 0600. For high-volume sites, integrate with a dedicated key
 * management service.
 */

if (!defined('ABSPATH')) exit;

class LedgerProof_Client {
    private $options;

    public function __construct() {
        $this->options = get_option('ledgerproof_options', array());
    }

    public function is_configured(): bool {
        return !empty($this->options['api_key']) && !empty($this->options['publisher_id']);
    }

    /**
     * Issue an ai/article-50/v1 receipt for the given post content.
     *
     * Returns the receipt array on success, or WP_Error on failure.
     */
    public function publish_post_receipt($post_id, $content_text, $content_type = 'AI_ASSISTED_DOCUMENT') {
        if (!$this->is_configured()) {
            return new WP_Error('not_configured', 'LedgerProof is not configured.');
        }

        $artifact_hash = hash('sha256', $content_text);
        $artifact_bytes = strlen($content_text);

        $content = array(
            'ai_system_id' => 'wordpress/' . get_bloginfo('name') . '/v1',
            'deployer_id' => $this->options['publisher_id'],
            'deployer_name' => $this->options['deployer_name'],
            'deployer_country' => strtoupper($this->options['deployer_country']),
            'content_category' => $content_type,
            'artifact_hash' => $artifact_hash,
            'artifact_content_type' => 'text/html',
            'artifact_bytes' => $artifact_bytes,
            'generation_type' => 'AI_ASSISTED',
            'transparency_marker' => 'LPR-EU-AI-ACT-50',
            'is_public_interest' => $this->options['is_public_interest'] === '1',
            'enforcement_date' => '2026-08-02',
            'profile_version' => 'EU-AI-ACT-50-v1.1',
        );

        // Strip null/empty values for clean canonical JSON.
        $content = array_filter($content, function ($v) {
            return $v !== null && $v !== '';
        });

        // Get or generate signing key.
        $keypair = $this->load_or_generate_keypair();
        if (is_wp_error($keypair)) {
            return $keypair;
        }

        // Register key (idempotent).
        $register_result = $this->register_key($keypair);
        if (is_wp_error($register_result)) {
            // ON CONFLICT DO NOTHING on server — fine to continue.
        }

        // Discover chain tip.
        $tip = $this->discover_chain_tip();
        if (is_wp_error($tip)) {
            return $tip;
        }

        // Build canonical entry.
        $entry_timestamp = $this->iso_now_millis();
        $content_canonical = $this->canonical_json($content);
        $content_hash = hash('sha256', $content_canonical);

        $entry = array(
            'content' => $content,
            'content_hash' => $content_hash,
            'content_type' => 'ai/article-50/v1',
            'entry_timestamp' => $entry_timestamp,
            'key_id' => 'wordpress-default',
            'prev_hash' => $tip['prev_hash'],
            'protocol_version' => 'ledgerproof/1.0',
            'publisher_id' => $this->options['publisher_id'],
            'sequence' => $tip['sequence'],
        );
        $entry_canonical = $this->canonical_json($entry);
        $entry_hash = hash('sha256', $entry_canonical);

        // Sign the raw 32 bytes.
        $signature = sodium_crypto_sign_detached(hex2bin($entry_hash), $keypair['private']);
        $signature_hex = bin2hex($signature);

        // POST /v1/publish.
        $body = array(
            'publisher_id' => $this->options['publisher_id'],
            'key_id' => 'wordpress-default',
            'prev_hash' => $tip['prev_hash'],
            'entry_hash' => $entry_hash,
            'signature' => $signature_hex,
            'protocol_version' => 'ledgerproof/1.0',
            'content_type' => 'ai/article-50/v1',
            'content_hash' => $content_hash,
            'content' => $content,
            'entry_json_canonical' => $entry_canonical,
            'entry_timestamp' => $entry_timestamp,
        );

        $response = wp_remote_post($this->api_base() . '/v1/publish', array(
            'headers' => $this->auth_headers(),
            'body' => wp_json_encode($body),
            'timeout' => 30,
        ));

        return $this->parse_response($response);
    }

    private function api_base(): string {
        return rtrim($this->options['api_base'] ?? LEDGERPROOF_API_BASE_DEFAULT, '/');
    }

    private function auth_headers(): array {
        return array(
            'Content-Type' => 'application/json',
            'X-Api-Key' => $this->options['api_key'],
            'X-Publisher-Id' => $this->options['publisher_id'],
        );
    }

    private function iso_now_millis(): string {
        $micro = microtime(true);
        $sec = (int) floor($micro);
        $ms = (int) (($micro - $sec) * 1000);
        return gmdate('Y-m-d\TH:i:s', $sec) . sprintf('.%03dZ', $ms);
    }

    private function canonical_json($data): string {
        return $this->sort_canonical($data);
    }

    private function sort_canonical($v): string {
        if (is_array($v)) {
            // Detect associative vs sequential.
            if (array_keys($v) === range(0, count($v) - 1)) {
                $parts = array_map([$this, 'sort_canonical'], $v);
                return '[' . implode(',', $parts) . ']';
            }
            ksort($v);
            $pairs = array();
            foreach ($v as $k => $val) {
                $pairs[] = json_encode((string) $k) . ':' . $this->sort_canonical($val);
            }
            return '{' . implode(',', $pairs) . '}';
        }
        return json_encode($v, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
    }

    private function load_or_generate_keypair() {
        $key_path = WP_CONTENT_DIR . '/ledgerproof-signing-key.bin';
        if (file_exists($key_path)) {
            $seed = file_get_contents($key_path);
            if ($seed === false || strlen($seed) !== SODIUM_CRYPTO_SIGN_SEEDBYTES) {
                return new WP_Error('bad_key', 'Existing signing key is corrupt.');
            }
        } else {
            $seed = random_bytes(SODIUM_CRYPTO_SIGN_SEEDBYTES);
            if (file_put_contents($key_path, $seed, LOCK_EX) === false) {
                return new WP_Error('save_key', 'Could not save signing key.');
            }
            chmod($key_path, 0600);
        }
        $keypair = sodium_crypto_sign_seed_keypair($seed);
        return array(
            'private' => sodium_crypto_sign_secretkey($keypair),
            'public' => sodium_crypto_sign_publickey($keypair),
            'public_b64' => base64_encode(sodium_crypto_sign_publickey($keypair)),
        );
    }

    private function register_key($keypair) {
        return wp_remote_post($this->api_base() . '/v1/keys', array(
            'headers' => $this->auth_headers(),
            'body' => wp_json_encode(array(
                'key_id' => 'wordpress-default',
                'verifying_key_b64' => $keypair['public_b64'],
            )),
            'timeout' => 15,
        ));
    }

    private function discover_chain_tip() {
        $probe = 0;
        while ($probe < 10000) {
            $response = wp_remote_get($this->api_base() . '/v1/entries/' . $probe, array('timeout' => 10));
            $code = wp_remote_retrieve_response_code($response);
            if ($code === 404) {
                if ($probe === 0) {
                    return array('sequence' => 0, 'prev_hash' => str_repeat('0', 64));
                }
                $prev_resp = wp_remote_get($this->api_base() . '/v1/entries/' . ($probe - 1), array('timeout' => 10));
                $prev = json_decode(wp_remote_retrieve_body($prev_resp), true);
                return array('sequence' => $probe, 'prev_hash' => $prev['entry_hash']);
            }
            if ($code !== 200) {
                return new WP_Error('chain_tip', 'Chain tip probe failed at sequence ' . $probe);
            }
            $probe++;
        }
        return new WP_Error('chain_tip', 'Chain too long for probe loop');
    }

    private function parse_response($response) {
        if (is_wp_error($response)) {
            return $response;
        }
        $code = wp_remote_retrieve_response_code($response);
        $body = wp_remote_retrieve_body($response);
        if ($code !== 201 && $code !== 200) {
            return new WP_Error('publish_failed', "API returned $code: $body");
        }
        return json_decode($body, true);
    }
}
