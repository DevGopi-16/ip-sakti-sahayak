import {
  collection,
  doc,
  addDoc,
  onSnapshot,
  updateDoc,
  deleteDoc,
  serverTimestamp,
  query,
  orderBy,
} from "firebase/firestore";

import { db } from "./firebase";

const getChatsCollection = (userId) => {
  if (!userId) {
    throw new Error("User ID is required.");
  }

  return collection(
    db,
    "users",
    userId,
    "chats"
  );
};

const normalizeChat = (chatDoc) => {
  const data = chatDoc.data();

  return {
    id: chatDoc.id,

    title:
      data.title ||
      "New Chat",

    pinned:
      Boolean(data.pinned),

    messages:
      Array.isArray(data.messages)
        ? data.messages
        : [],

    createdAt:
      data.createdAt?.toDate?.() ||
      null,

    updatedAt:
      data.updatedAt?.toDate?.() ||
      null,
  };
};

const sortChats = (chats) => {
  return [...chats].sort((a, b) => {
    if (a.pinned !== b.pinned) {
      return a.pinned ? -1 : 1;
    }

    const aTime =
      a.updatedAt?.getTime?.() || 0;

    const bTime =
      b.updatedAt?.getTime?.() || 0;

    return bTime - aTime;
  });
};

export const createChat = async (
  userId,
  title,
  messages = []
) => {
  if (!userId) {
    throw new Error("User ID is required.");
  }

  const chatsRef =
    getChatsCollection(userId);

  const trimmedTitle =
    title?.trim() ||
    "New Chat";

  const safeMessages =
    Array.isArray(messages)
      ? messages
      : [];

  const chatData = {
    title: trimmedTitle,
    pinned: false,
    messages: safeMessages,
    createdAt: serverTimestamp(),
    updatedAt: serverTimestamp(),
  };

  const chatDoc = await addDoc(
    chatsRef,
    chatData
  );

  return {
    id: chatDoc.id,
    title: trimmedTitle,
    pinned: false,
    messages: safeMessages,
    createdAt: new Date(),
    updatedAt: new Date(),
  };
};

export const subscribeToUserChats = (
  userId,
  onChats,
  onError
) => {
  if (!userId) {
    throw new Error("User ID is required.");
  }

  if (typeof onChats !== "function") {
    throw new Error(
      "onChats callback is required."
    );
  }

  const chatsRef =
    getChatsCollection(userId);

  const chatsQuery = query(
    chatsRef,
    orderBy("updatedAt", "desc")
  );

  const unsubscribe = onSnapshot(
    chatsQuery,
    (snapshot) => {
      const chats = snapshot.docs.map(
        normalizeChat
      );

      onChats(sortChats(chats));
    },
    (error) => {
      console.error(
        "Chat history subscription failed:",
        error
      );

      if (typeof onError === "function") {
        onError(error);
      }
    }
  );

  return unsubscribe;
};

export const getUserChats = async (
  userId
) => {

  if (!userId) {
    throw new Error("User ID is required.");
  }

  return [];
};

export const getChat = async (
  userId,
  chatId
) => {
  if (!userId || !chatId) {
    throw new Error(
      "User ID and Chat ID are required."
    );
  }

  const { getDoc } = await import(
    "firebase/firestore"
  );

  const chatRef = doc(
    db,
    "users",
    userId,
    "chats",
    chatId
  );

  const snapshot =
    await getDoc(chatRef);

  if (!snapshot.exists()) {
    return null;
  }

  return normalizeChat(snapshot);
};


export const updateChat = async (
  userId,
  chatId,
  updates
) => {
  if (!userId || !chatId) {
    throw new Error(
      "User ID and Chat ID are required."
    );
  }

  if (
    !updates ||
    typeof updates !== "object"
  ) {
    throw new Error(
      "Chat updates are required."
    );
  }

  const chatRef = doc(
    db,
    "users",
    userId,
    "chats",
    chatId
  );

  await updateDoc(chatRef, {
    ...updates,
    updatedAt: serverTimestamp(),
  });
};


export const updateChatMessages = async (
  userId,
  chatId,
  messages
) => {
  if (!Array.isArray(messages)) {
    throw new Error(
      "Messages must be an array."
    );
  }

  await updateChat(
    userId,
    chatId,
    {
      messages,
    }
  );
};

export const renameChat = async (
  userId,
  chatId,
  title
) => {
  const trimmedTitle =
    title?.trim();

  if (!trimmedTitle) {
    throw new Error(
      "Chat title cannot be empty."
    );
  }

  await updateChat(
    userId,
    chatId,
    {
      title: trimmedTitle,
    }
  );
};

export const togglePinChat = async (
  userId,
  chatId,
  pinned
) => {
  await updateChat(
    userId,
    chatId,
    {
      pinned: Boolean(pinned),
    }
  );
};


export const deleteChat = async (
  userId,
  chatId
) => {
  if (!userId || !chatId) {
    throw new Error(
      "User ID and Chat ID are required."
    );
  }

  const chatRef = doc(
    db,
    "users",
    userId,
    "chats",
    chatId
  );

  await deleteDoc(chatRef);
};