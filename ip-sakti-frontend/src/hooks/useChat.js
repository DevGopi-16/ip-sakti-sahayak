import { useEffect, useRef, useState } from 'react';

import {
  sendChatMessage,
} from '../api/chatApi';

import {
  createChat,
  updateChatMessages,
} from '../firestore';

export default function useChat({
  user,
  language,
  activeStatute,
  activeChatId,
  setActiveChatId,
  refreshChatHistory,
  initialBotMessage,

  
}) {
  const [messages, setMessages] = useState([
    initialBotMessage,
  ]);

  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const saveChatToFirestore = async (
    chatId,
    chatMessages
  ) => {
    if (!user || !chatId) {
      return false;
    }

    try {
      await updateChatMessages(
        user.uid,
        chatId,
        chatMessages
      );

      return true;
    } catch (error) {
      console.error(
        'Failed to save chat messages:',
        error
      );

      return false;
    }
  };

  const handleSend = async (
    textToSend = query
  ) => {
    const activeQuery =
      String(textToSend || '').trim();

    if (
      !activeQuery ||
      loading ||
      !user
    ) {
      return;
    }

    const userMsg = {
      sender: 'user',
      text: activeQuery,
    };

    const messagesBeforeResponse = [
      ...messages,
      userMsg,
    ];

    setMessages(
      messagesBeforeResponse
    );

    setQuery('');
    setLoading(true);

    try {

      const response =
        await sendChatMessage(
          activeQuery,
          messages,
          language,
          activeStatute
        );

      const botAnswer =
        response?.answer ||
        response?.response ||
        response?.message ||
        'No response received.';

      const botSources =
        response?.source
          ? [response.source]
          : Array.isArray(
              response?.sources
            )
          ? response.sources
          : [];

      const botMessage = {
        sender: 'bot',
        text: botAnswer,
        sources: botSources,

        show_images:
          response?.show_images === true,

        search_query:
          response?.search_query || '',

        images:
          Array.isArray(
            response?.images
          )
            ? response.images
            : [],
      };

      const updatedMessages = [
        ...messagesBeforeResponse,
        botMessage,
      ];

      setMessages(updatedMessages);
      setLoading(false);

      if (!activeChatId) {
        createChat(
          user.uid,
          activeQuery,
          updatedMessages
        )
          .then(async (newChat) => {
            if (!newChat?.id) {
              throw new Error(
                'Chat was created but no chat ID was returned.'
              );
            }

            setActiveChatId(
              newChat.id
            );

            await refreshChatHistory(
              user.uid
            );
          })
          .catch((error) => {
            console.error(
              'Background chat creation failed:',
              error
            );
          });
      } else {

        saveChatToFirestore(
          activeChatId,
          updatedMessages
        )
          .then(async (saved) => {
            if (!saved) {
              throw new Error(
                'Failed to persist chat messages.'
              );
            }
            await refreshChatHistory(
              user.uid
            );
          })
          .catch((error) => {
            console.error(
              'Background chat persistence failed:',
              error
            );
          });
      }
    } catch (err) {
      console.error(
        'Chat request failed:',
        err
      );

      const errorMessage = {
        sender: 'bot',
        text:
          '**Connection error:** Could not reach the IP-SAKTI backend.',
        isError: true,
      };

      const updatedMessages = [
        ...messagesBeforeResponse,
        errorMessage,
      ];

      setMessages(updatedMessages);
      setLoading(false);
    }
  };

  return {
    messages,
    setMessages,

    query,
    setQuery,

    loading,
    setLoading,

    handleSend,

    chatEndRef,
  };
}