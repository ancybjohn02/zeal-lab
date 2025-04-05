document.addEventListener("DOMContentLoaded", () => {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.querySelector(".chat-box");
  
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const message = userInput.value.trim();
      if (!message) return;
  
      // Show user message
      appendMessage("You", message, "user");
  
      // Send to server
      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message }),
      });
  
      const data = await response.json();
  
      // Format bot response (replace \n with <br>)
      const botResponse = marked.parse(data.response);

      appendMessage("Zeal", botResponse, "bot");
  
      userInput.value = "";
    });
  
    function appendMessage(sender, message, type) {
      const bubble = document.createElement("div");
      bubble.classList.add("chat-bubble", type);
  
      bubble.innerHTML = `
        <div class="text">${message}</div>
      `;
      chatBox.appendChild(bubble);
      chatBox.scrollTop = chatBox.scrollHeight;
    }
  });
  