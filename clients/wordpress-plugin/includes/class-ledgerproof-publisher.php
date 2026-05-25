<?php
/**
 * Hook into save_post: if the post is flagged as AI-assisted, issue an LPR receipt.
 *
 * A post is considered AI-assisted if EITHER:
 * - The post has a custom field `ledgerproof_ai_assisted` set to "1", OR
 * - The post's category includes "AI-Generated" (case-insensitive).
 *
 * On successful publish, we store the receipt sequence and entry_hash as
 * post meta (`ledgerproof_receipt_sequence`, `ledgerproof_receipt_entry_hash`)
 * so the front-end theme can render a verification badge.
 */

if (!defined('ABSPATH')) exit;

class LedgerProof_Publisher {
    public function __construct() {
        add_action('save_post', array($this, 'maybe_issue_receipt'), 99, 3);
        add_action('the_content', array($this, 'maybe_append_disclosure'));
    }

    public function maybe_issue_receipt($post_id, $post, $update) {
        if (wp_is_post_revision($post_id) || wp_is_post_autosave($post_id)) {
            return;
        }
        if ($post->post_status !== 'publish') {
            return;
        }
        if (!$this->is_ai_assisted($post_id, $post)) {
            return;
        }
        // Avoid re-issuing on updates — only issue once per post.
        if (get_post_meta($post_id, 'ledgerproof_receipt_entry_hash', true)) {
            return;
        }

        $opts = get_option('ledgerproof_options', array());
        if (($opts['auto_issue'] ?? '1') !== '1') {
            return;
        }

        $client = new LedgerProof_Client();
        if (!$client->is_configured()) {
            return;
        }

        $content_text = wp_strip_all_tags($post->post_content);
        $receipt = $client->publish_post_receipt($post_id, $content_text);
        if (is_wp_error($receipt)) {
            error_log('[ledgerproof] receipt issuance failed for post ' . $post_id . ': ' . $receipt->get_error_message());
            return;
        }
        if (isset($receipt['sequence'])) {
            update_post_meta($post_id, 'ledgerproof_receipt_sequence', (int) $receipt['sequence']);
            update_post_meta($post_id, 'ledgerproof_receipt_entry_hash', sanitize_text_field($receipt['entry_hash']));
        }
    }

    private function is_ai_assisted($post_id, $post): bool {
        if (get_post_meta($post_id, 'ledgerproof_ai_assisted', true) === '1') {
            return true;
        }
        $categories = wp_get_post_categories($post_id, array('fields' => 'names'));
        foreach ($categories as $cat) {
            if (stripos($cat, 'ai-generated') !== false || stripos($cat, 'ai assisted') !== false) {
                return true;
            }
        }
        return false;
    }

    public function maybe_append_disclosure($content) {
        if (!is_singular()) return $content;
        $seq = get_post_meta(get_the_ID(), 'ledgerproof_receipt_sequence', true);
        if (!$seq) return $content;
        $verify_url = 'https://api-eu.ledgerproofhq.io/v1/verify/' . (int) $seq;
        $disclosure = sprintf(
            '<aside class="ledgerproof-disclosure" data-lpr-receipt="%d" style="margin:24px 0;padding:12px;border:1px solid #e5e7eb;border-radius:6px;background:#f9fafb;font-size:13px;">' .
                'This content was assisted by AI. EU AI Act Article 50 receipt: ' .
                '<a href="%s" target="_blank" rel="noopener">verify on LedgerProof</a> (sequence #%d).' .
            '</aside>',
            (int) $seq,
            esc_url($verify_url),
            (int) $seq
        );
        return $content . $disclosure;
    }
}
