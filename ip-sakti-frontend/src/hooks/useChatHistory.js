import {
  useCallback,
  useEffect,
  useState,
} from 'react';

import {
  subscribeToUserChats,
  togglePinChat as toggleFirestorePinChat,
  renameChat as renameFirestoreChat,
  deleteChat as deleteFirestoreChat,
} from '../firestore';

export default function useChatHistory({
  user,
  authLoading,
}) {
  const [chatHistoryList, setChatHistoryList] =
    useState([]);

  const [activeChatId, setActiveChatId] =
    useState(null);

  const [historyLoading, setHistoryLoading] =
    useState(false);

  const [chatPendingDelete, setChatPendingDelete] =
    useState(null);

  const refreshChatHistory = useCallback(
    async (userId) => {
      if (!userId) {
        setChatHistoryList([]);
        return;
      }

      setHistoryLoading(true);
      try {

      } finally {
        setHistoryLoading(false);
      }
    },
    []
  );

  useEffect(() => {

    if (authLoading) {
      return;
    }

    if (!user?.uid) {
      setChatHistoryList([]);
      setActiveChatId(null);
      setHistoryLoading(false);

      return;
    }

    setHistoryLoading(true);

    let unsubscribe;

    try {
      unsubscribe = subscribeToUserChats(
        user.uid,
        (chats) => {
          setChatHistoryList(
            Array.isArray(chats)
              ? chats
              : []
          );

          setHistoryLoading(false);
        },
        (error) => {
          console.error(
            'Failed to subscribe to chat history:',
            error
          );

          setChatHistoryList([]);
          setHistoryLoading(false);
        }
      );
    } catch (error) {
      console.error(
        'Failed to start chat history subscription:',
        error
      );

      setChatHistoryList([]);
      setHistoryLoading(false);
    }

    return () => {
      if (typeof unsubscribe === 'function') {
        unsubscribe();
      }
    };
  }, [
    user?.uid,
    authLoading,
  ]);

  const togglePinChat = useCallback(
    async (event, item) => {
      event?.stopPropagation();

      if (!user || !item) {
        return;
      }

      const newPinned =
        !Boolean(item.pinned);
      setChatHistoryList(
        (currentChats) =>
          currentChats.map((chat) =>
            chat.id === item.id
              ? {
                  ...chat,
                  pinned: newPinned,
                }
              : chat
          )
      );

      try {
        await toggleFirestorePinChat(
          user.uid,
          item.id,
          newPinned
        );
      } catch (error) {
        console.error(
          'Failed to update pin:',
          error
        );

        setChatHistoryList(
          (currentChats) =>
            currentChats.map((chat) =>
              chat.id === item.id
                ? {
                    ...chat,
                    pinned: Boolean(
                      item.pinned
                    ),
                  }
                : chat
            )
        );
      }
    },
    [user]
  );

  const renameChat = useCallback(
    async (event, item) => {
      event?.stopPropagation();

      if (!user || !item) {
        return;
      }

      const newTitle =
        window.prompt(
          'Rename chat',
          item.title || ''
        );

      if (newTitle === null) {
        return;
      }

      const trimmedTitle =
        newTitle.trim();

      if (!trimmedTitle) {
        return;
      }

      try {
        await renameFirestoreChat(
          user.uid,
          item.id,
          trimmedTitle
        );
      } catch (error) {
        console.error(
          'Failed to rename chat:',
          error
        );
      }
    },
    [user]
  );

  const requestDeleteChat = useCallback(
    (event, item) => {
      event?.stopPropagation();

      if (!user || !item) {
        return;
      }

      setChatPendingDelete(item);
    },
    [user]
  );

  const deleteChat = useCallback(
    async () => {
      if (!user || !chatPendingDelete) {
        return;
      }

      const item = chatPendingDelete;

      try {
        await deleteFirestoreChat(
          user.uid,
          item.id
        );

        if (
          activeChatId === item.id
        ) {
          setActiveChatId(null);
        }
        setChatPendingDelete(null);
      } catch (error) {
        console.error(
          'Failed to delete chat:',
          error
        );
      }
    },
    [
      user,
      chatPendingDelete,
      activeChatId,
    ]
  );

  const cancelDeleteChat = useCallback(() => {
    setChatPendingDelete(null);
  }, []);
 
  return {
    chatHistoryList,
    setChatHistoryList,

    activeChatId,
    setActiveChatId,

    historyLoading,

    refreshChatHistory,

    togglePinChat,
    renameChat,
    deleteChat,
    requestDeleteChat,
    cancelDeleteChat,
    chatPendingDelete,
  };
}
