const API_BASE_URL = "http://127.0.0.1:8000";

export const sendChatMessage = async (
  query,
  chatHistory = [],
  language = "en",
  statute = "ALL"
) => {
  try {
    const formattedHistory = Array.isArray(chatHistory)
      ? chatHistory.map((msg) => ({
          role: msg.role === "user" ? "user" : "assistant",
          content: String(msg.content || msg.text || ""),
        }))
      : [];

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query: query,
        language: language,
        statute: statute,
        chat_history: formattedHistory,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error connecting to IP-SAKTI Backend:", error);
    throw error;
  }
};

export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(
        errorData.detail || `HTTP error! status: ${response.status}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error("Error uploading document to IP-SAKTI Backend:", error);
    throw error;
  }
};