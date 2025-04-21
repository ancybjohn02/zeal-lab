document.getElementById("send-btn").addEventListener("click", async function() {
    const queryInput = document.getElementById("query-input");
    const query = queryInput.value.trim();

    if (!query) return;

    // Append the user's message to the chatbox
    appendMessage(query, "user-message");

    // Clear the input field
    queryInput.value = "";

    // Send the query to the FastAPI backend
    try {
        const response = await fetch('http://127.0.0.1:5000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query: query })
        });

        // Check if the response is ok
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Ensure the bot's response exists in the data object
        if (data && data.response) {
            const botResponse = data.response;

            // Append the bot's response to the chatbox
            appendMessage(botResponse, "bot-message");
        } else {
            throw new Error('Bot response is missing');
        }
    } catch (error) {
        console.error('Error:', error);
        appendMessage("Sorry, something went wrong. Please try again later.", "bot-message");
    }
});

function appendMessage(message, messageType) {
    const chatBoxContent = document.getElementById("chat-box-content");

    const messageElement = document.createElement("div");
    messageElement.classList.add(messageType);
    messageElement.textContent = message;

    chatBoxContent.appendChild(messageElement);

    // Scroll to the bottom of the chatbox
    chatBoxContent.scrollTop = chatBoxContent.scrollHeight;
}
