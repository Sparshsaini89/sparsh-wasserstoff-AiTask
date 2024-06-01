<?php
/*
Plugin Name: RAG-based Query Suggestion Chatbot
Description: A chatbot that uses Retrieval-Augmented Generation with a Chain of Thought strategy for WordPress sites.
Version: 1.0
Author: Your Name
*/

function chatbot_enqueue_scripts() {
    wp_enqueue_script('chatbot-script', plugin_dir_url(__FILE__) . 'chatbot.js', array('jquery'), null, true);
    wp_enqueue_style('chatbot-style', plugin_dir_url(__FILE__) . 'chatbot.css');
}
add_action('wp_enqueue_scripts', 'chatbot_enqueue_scripts');

function chatbot_display() {
    echo '
    <div class="chat-container">
        <div class="chat-box" id="chat-box"></div>
        <input type="text" id="user-input" class="user-input" placeholder="Type your query here...">
        <button id="send-button" class="send-button">Send</button>
    </div>';
}
add_shortcode('chatbot', 'chatbot_display');
?>
