jQuery(document).ready(function($) {
    $('#send-button').on('click', function() {
        const userInput = $('#user-input').val();
        const chatBox = $('#chat-box');

        chatBox.append(`<p><strong>You:</strong> ${userInput}</p>`);

        $.ajax({
            url: 'http://your-flask-server-address/chain_of_thought',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ query: userInput }),
            success: function(data) {
                const chainOfThought = data.chain_of_thought;
                chainOfThought.forEach(thought => {
                    chatBox.append(`<p>${thought}</p>`);
                });
                chatBox.scrollTop(chatBox[0].scrollHeight);
            }
        });
    });
});
