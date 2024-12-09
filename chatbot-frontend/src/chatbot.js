import React, { useState } from "react";
import axios from "axios";
import "./chatbot.css";
import botIcon from "./images/bot-icon.png";
import userIcon from "./images/user-icon.png";

const QueryForm = () => {
  const [query, setQuery] = useState("");
  const [response, setResponse] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([]);

  const handleInputChange = (event) => setQuery(event.target.value);

  const sendQueryToBackend = async () => {
    if (!query) return;

    // Add user message to the chat history
    setMessages([...messages, { text: query, sender: "user" }]);
    setQuery("");
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/query", { query });
      const botResponse = res.data.response;

      // Add bot response to the chat history
      setMessages([
        ...messages,
        { text: query, sender: "user" },
        { text: botResponse, sender: "bot" },
      ]);
    } catch (error) {
      setMessages([
        ...messages,
        { text: query, sender: "user" },
        {
          text: "Sorry, there was an error processing your query.",
          sender: "bot",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-history">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-bubble ${msg.sender}`}>
            {msg.sender === "bot" && (
              <div
                className="avatar"
                style={{ backgroundImage: `url(${botIcon})` }}
              ></div>
            )}
            {msg.sender === "user" && (
              <div
                className="avatar"
                style={{ backgroundImage: `url(${userIcon})` }}
              ></div>
            )}
            <div className="message-text">{msg.text}</div>
          </div>
        ))}
      </div>

      <textarea
        value={query}
        onChange={handleInputChange}
        placeholder="Ask a question about stocks on the NYSE..."
        rows="2"
        className="query-input"
      />

      <button
        className="submit-button"
        onClick={sendQueryToBackend}
        disabled={loading}
      >
        {loading ? <div className="spinner"></div> : "Ask"}
      </button>
    </div>
  );
};

export default QueryForm;
