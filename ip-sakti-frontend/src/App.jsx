import React, { useEffect, useState } from 'react';

import {
  X,
  Link as LinkIcon,
  MessageCircle,
  Check,
  Share2,
  Scale,
  Globe,
  RefreshCw,
  Sparkles,
  Send,
} from 'lucide-react';

import ReactMarkdown from 'react-markdown';

import Sidebar from './components/Sidebar';
import MessageList from './components/MessageList';
import Login from './components/Login';

import {
  STATUTE_GROUPS,
  INITIAL_BOT_MESSAGE,
  QUICK_PROMPTS,
} from './constants/statutes';

import { logoutUser } from './firebase';

import useAuth from './hooks/useAuth';
import useChat from './hooks/useChat';
import useChatHistory from './hooks/useChatHistory';

import { uploadDocument } from './api/chatApi';

import {
  copyShareLink,
  shareToWhatsApp,
  shareToLinkedIn,
  shareToReddit,
} from './utils/share';

export default function App() {

  const { user, authLoading } = useAuth();

  const [language, setLanguage] = useState('en');
  const [activeStatute, setActiveStatute] = useState('ALL');

  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [expandedGroups, setExpandedGroups] = useState({
    GLOBAL: true,
    'INTELLECTUAL PROPERTY': false,
    'DRUGS & TRADITIONAL KNOWLEDGE': false,
  });

  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [uploadError, setUploadError] = useState(false);

  const [showShareModal, setShowShareModal] = useState(false);
  const [shareItem, setShareItem] = useState(null);
  const [linkCopied, setLinkCopied] = useState(false);


  const [openHistoryMenu, setOpenHistoryMenu] = useState(null);

  const getActiveStatute = () => {
    for (const group of STATUTE_GROUPS) {
      const found = group.items.find(
        (item) => item.code === activeStatute
      );

      if (found) {
        return found;
      }
    }

    return STATUTE_GROUPS[0].items[0];
  };

  const activeStatuteInfo = getActiveStatute();

  const {
    chatHistoryList,
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
  } = useChatHistory({
    user,
    authLoading,
  });

  const {
    messages,
    setMessages,
    query,
    setQuery,
    loading,
    handleSend,
    chatEndRef,
  } = useChat({
    user,
    language,
    activeStatute,
    activeChatId,
    setActiveChatId,
    refreshChatHistory,
    initialBotMessage: INITIAL_BOT_MESSAGE,
  });

  const handleStartNewChat = () => {
    setMessages([INITIAL_BOT_MESSAGE]);
    setActiveChatId(null);
    setQuery('');
    setOpenHistoryMenu(null);
    setShareItem(null);
    setShowShareModal(false);
  };


  const handleLoadHistoryItem = (item) => {
    if (!item) {
      return;
    }

    setOpenHistoryMenu(null);
    setActiveChatId(item.id);
    setQuery('');

    const savedMessages = Array.isArray(item.messages)
      ? item.messages
      : [];

    setMessages(
      savedMessages.length > 0
        ? savedMessages
        : [INITIAL_BOT_MESSAGE]
    );
  };

  const toggleGroup = (title) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [title]: !prev[title],
    }));
  };


  useEffect(() => {
    const handleOutsideClick = () => {
      setOpenHistoryMenu(null);
    };

    if (openHistoryMenu !== null) {
      document.addEventListener('click', handleOutsideClick);
    }

    return () => {
      document.removeEventListener('click', handleOutsideClick);
    };
  }, [openHistoryMenu]);


  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape' && showShareModal) {
        setShowShareModal(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showShareModal]);


  const shareChat = (event, item) => {
    event.stopPropagation();

    setShareItem(item);
    setLinkCopied(false);
    setShowShareModal(true);
    setOpenHistoryMenu(null);
  };

  const getSharePreview = () => {
    if (!shareItem) {
      return {
        title: '',
        userQuery: '',
        botAnswer: '',
      };
    }

    const conversationMessages = Array.isArray(
      shareItem.messages
    )
      ? shareItem.messages
      : [];

    const userIndex = conversationMessages.findIndex(
      (message) => message.sender === 'user'
    );

    const userMessage =
      userIndex >= 0
        ? conversationMessages[userIndex]
        : null;

    let botMessage = null;

    if (userIndex >= 0) {
      botMessage = conversationMessages
        .slice(userIndex + 1)
        .find(
          (message) => message.sender === 'bot'
        );
    }

    return {
      title: shareItem.title || 'IP-SAKTI Sahayak',

      userQuery:
        userMessage?.text ||
        shareItem.title ||
        '',

      botAnswer:
        botMessage?.text ||
        'This conversation was created using IP-SAKTI Sahayak.',
    };
  };

  const sharePreview = getSharePreview();

  const handleFileSelect = (event) => {
    if (
      !event.target.files ||
      !event.target.files[0]
    ) {
      return;
    }

    const file = event.target.files[0];

    const validTypes = [
      'application/pdf',
      'text/plain',
    ];

    if (
      !validTypes.includes(file.type) &&
      !file.name.match(/\.(pdf|txt)$/i)
    ) {
      setUploadStatus(
        'Please select a valid PDF (.pdf) or Text (.txt) file.'
      );

      setUploadError(true);
      setSelectedFile(null);

      return;
    }

    setSelectedFile(file);
    setUploadStatus('');
    setUploadError(false);
  };

  const handleUploadSubmit = async (event) => {
    event.preventDefault();

    if (!selectedFile || uploading) {
      return;
    }

    setUploading(true);
    setUploadStatus('Uploading file...');
    setUploadError(false);

    try {
      const response = await uploadDocument(selectedFile);

      setUploadStatus(
        response?.message ||
          'Uploaded! Indexing running in background.'
      );

      setUploadError(false);
      setSelectedFile(null);

      setTimeout(() => {
        setShowUploadModal(false);
        setUploadStatus('');
      }, 1500);
    } catch (error) {
      setUploadStatus(
        `Upload failed: ${
          error?.message || 'Error uploading file'
        }`
      );

      setUploadError(true);
    } finally {
      setUploading(false);
    }
  };


  if (authLoading) {
    return (
      <div className="flex h-screen w-screen bg-[#0A101C] items-center justify-center text-slate-400 font-sans">
        <div className="flex items-center gap-3">
          <RefreshCw className="w-5 h-5 animate-spin text-amber-400" />

          <span>
            Authenticating IP-SAKTI...
          </span>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return (
    <div className="flex h-screen bg-[#0A101C] text-slate-100 font-sans overflow-hidden relative">
      <Sidebar
        user={user}
        sidebarOpen={sidebarOpen}
        setSidebarOpen={setSidebarOpen}
        chatHistoryList={chatHistoryList}
        activeChatId={activeChatId}
        historyLoading={historyLoading}
        expandedGroups={expandedGroups}
        setExpandedGroups={setExpandedGroups}
        activeStatute={activeStatute}
        setActiveStatute={setActiveStatute}
        startNewChat={handleStartNewChat}
        loadHistoryItem={handleLoadHistoryItem}
        togglePinChat={togglePinChat}
        renameChat={renameChat}
        deleteChat={deleteChat}
        shareChat={shareChat}
        setShowUploadModal={setShowUploadModal}
        logoutUser={logoutUser}
        openHistoryMenu={openHistoryMenu}
        setOpenHistoryMenu={setOpenHistoryMenu}
        STATUTE_GROUPS={STATUTE_GROUPS}
        requestDeleteChat={requestDeleteChat}
        cancelDeleteChat={cancelDeleteChat}
        chatPendingDelete={chatPendingDelete}
      />

      <div
        className={`
          flex
          flex-col
          flex-1
          min-w-0
          transition-all
          duration-300
          ease-in-out
          ${sidebarOpen ? 'ml-72' : 'ml-16'}
        `}
      >
        <header className="flex items-center justify-between px-5 md:px-6 py-3.5 border-b border-slate-800/80 shrink-0">

          <div className="flex items-center gap-3 min-w-0">

            <div className="flex items-center gap-2 min-w-0">

              <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center shrink-0">
                {React.createElement(
                  activeStatuteInfo.icon,
                  {
                    className:
                      'w-4 h-4 text-amber-400',
                  }
                )}
              </div>

              <div className="min-w-0">

                <div className="text-sm font-semibold text-slate-100 truncate">
                  {activeStatuteInfo.label}
                </div>

                <div className="text-[10px] text-slate-500 font-mono uppercase tracking-wider">
                  {activeStatute}

                  {activeStatute === 'ALL'
                    ? ' · Global Knowledge Base'
                    : ' · Statutory Context'}
                </div>

              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 bg-slate-900/60 px-3 py-1.5 rounded-lg border border-slate-800 shrink-0">

            <Globe className="w-4 h-4 text-slate-400" />

            <select
              value={language}
              onChange={(event) =>
                setLanguage(event.target.value)
              }
              className="bg-transparent text-sm text-slate-200 focus:outline-none cursor-pointer"
            >
              <option
                value="en"
                className="bg-slate-800"
              >
                English
              </option>

              <option
                value="hi"
                className="bg-slate-800"
              >
                Hindi (हिंदी)
              </option>
            </select>

          </div>

        </header>
        <MessageList
          messages={messages}
          loading={loading}
          chatEndRef={chatEndRef}
        />
        <div className="max-w-4xl mx-auto px-4 pb-2 w-full flex flex-wrap gap-2">

          {QUICK_PROMPTS.map((prompt, index) => (
            <button
              key={index}
              onClick={() =>
                handleSend(prompt.text)
              }
              disabled={loading}
              className="
                flex
                items-center
                gap-2
                text-xs
                bg-[#111A2B]
                hover:bg-slate-800
                hover:border-amber-700/50
                text-slate-300
                border
                border-slate-800
                rounded-lg
                px-3
                py-2
                transition-colors
                disabled:opacity-50
                text-left
              "
            >

              <span
                className="
                  font-mono
                  text-[10px]
                  text-emerald-400
                  border
                  border-emerald-800/60
                  px-1.5
                  py-0.5
                  rounded
                  shrink-0
                "
              >
                {prompt.cite}
              </span>

              <Sparkles className="w-3 h-3 text-amber-400 shrink-0" />

              <span>
                {prompt.text}
              </span>

            </button>
          ))}

        </div>

        <footer className="p-4 border-t border-slate-800/80 shrink-0">
          <form
            onSubmit={(event) => {
              event.preventDefault();
              handleSend();
            }}
            className="
              max-w-4xl
              mx-auto
              flex
              items-end
              gap-2
              bg-[#111A2B]
              border
              border-slate-800
              rounded-2xl
              p-1.5
              pl-4
              focus-within:border-amber-600/60
              transition-colors
            "
          >

            <input
              type="text"
              value={query}
              onChange={(event) =>
                setQuery(event.target.value)
              }
              placeholder="Ask a legal query regarding Patents, Trademarks, Biodiversity..."
              className="
                flex-1
                bg-transparent
                py-2.5
                text-sm
                text-slate-100
                placeholder-slate-500
                focus:outline-none
              "
            />

            <button
              type="submit"
              disabled={
                loading || !query.trim()
              }
              className="
                bg-amber-500
                hover:bg-amber-400
                text-slate-950
                font-semibold
                w-10
                h-10
                rounded-full
                transition-colors
                disabled:opacity-40
                disabled:cursor-not-allowed
                flex
                items-center
                justify-center
                shrink-0
              "
            >
              <Send className="w-4 h-4" />
            </button>

          </form>

          <p className="text-center text-[11px] text-slate-600 mt-2">
            IP-SAKTI Sahayak provides statutory reference,
            not legal advice. Verify with a registered agent.
          </p>

        </footer>

      </div>
      {showUploadModal && (
        <div
          className="
            fixed
            inset-0
            z-50
            bg-black/70
            backdrop-blur-sm
            flex
            items-center
            justify-center
            p-4
          "
          onClick={() =>
            !uploading &&
            setShowUploadModal(false)
          }
        >

          <div
            className="
              bg-[#111A2B]
              border
              border-slate-800
              rounded-2xl
              max-w-md
              w-full
              p-6
              shadow-2xl
              relative
            "
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <h3 className="text-lg font-bold text-amber-400 mb-2">
              Upload Legal Document
            </h3>

            <p className="text-xs text-slate-400 mb-4">
              Upload PDF or TXT statutory documents
              to dynamically re-index the knowledge base.
            </p>

            <form
              onSubmit={handleUploadSubmit}
              className="space-y-4"
            >

              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileSelect}
                disabled={uploading}
                className="
                  w-full
                  text-xs
                  text-slate-300
                  file:mr-3
                  file:py-2
                  file:px-4
                  file:rounded-xl
                  file:border-0
                  file:text-xs
                  file:font-semibold
                  file:bg-amber-500/10
                  file:text-amber-400
                  hover:file:bg-amber-500/20
                  cursor-pointer
                "
              />

              {uploadStatus && (
                <div
                  className={`
                    p-3
                    rounded-lg
                    text-xs
                    font-medium
                    border
                    ${
                      uploadError
                        ? 'bg-rose-950/60 border-rose-800 text-rose-300'
                        : 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
                    }
                  `}
                >
                  {uploadStatus}
                </div>
              )}

              <div className="flex justify-end gap-3 pt-2">

                <button
                  type="button"
                  onClick={() => {
                    setShowUploadModal(false);
                    setUploadStatus('');
                    setSelectedFile(null);
                  }}
                  disabled={uploading}
                  className="
                    px-4
                    py-2
                    text-xs
                    font-semibold
                    text-slate-400
                    hover:text-slate-200
                    transition
                  "
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={!selectedFile || uploading}
                  className="
                    px-4
                    py-2
                    bg-amber-500
                    hover:bg-amber-400
                    disabled:opacity-50
                    text-slate-950
                    text-xs
                    font-bold
                    rounded-xl
                    transition
                    flex
                    items-center
                    gap-2
                  "
                >

                  {uploading && (
                    <RefreshCw
                      className="
                        w-3.5
                        h-3.5
                        animate-spin
                      "
                    />
                  )}

                  <span>
                    {uploading
                      ? 'Indexing...'
                      : 'Upload & Re-index'}
                  </span>

                </button>

              </div>

            </form>

          </div>
        </div>
      )}

      {showShareModal && shareItem && (
        <div
          className="
            fixed
            inset-0
            z-[100]
            bg-black/70
            backdrop-blur-md
            flex
            items-center
            justify-center
            p-4
          "
          onClick={() =>
            setShowShareModal(false)
          }
        >

          <div
            className="
              w-full
              max-w-lg
              bg-[#111A2B]
              border
              border-slate-700/80
              rounded-2xl
              shadow-2xl
              overflow-hidden
            "
            onClick={(event) =>
              event.stopPropagation()
            }
          >

            <div
              className="
                flex
                items-center
                justify-between
                px-5
                py-4
                border-b
                border-slate-800
              "
            >

              <div>

                <h2
                  className="
                    text-base
                    font-semibold
                    text-slate-100
                  "
                >
                  {sharePreview.title}
                </h2>

                <p
                  className="
                    text-[11px]
                    text-slate-500
                    mt-0.5
                  "
                >
                  Share this conversation
                </p>

              </div>

              <button
                type="button"
                onClick={() =>
                  setShowShareModal(false)
                }
                className="
                  w-8
                  h-8
                  rounded-full
                  flex
                  items-center
                  justify-center
                  text-slate-400
                  hover:text-slate-100
                  hover:bg-slate-800
                  transition
                "
                title="Close"
              >
                <X className="w-4 h-4" />
              </button>

            </div>

            {/* PREVIEW */}

            <div className="px-5 pt-5">

              <div
                className="
                  rounded-2xl
                  border
                  border-slate-700
                  bg-[#0B1220]
                  overflow-hidden
                "
              >

                <div
                  className="
                    px-4
                    pt-4
                    pb-3
                  "
                >
                  <div className="flex justify-end">

                    <div
                      className="
                        max-w-[88%]
                        bg-slate-700
                        text-slate-100
                        text-sm
                        leading-relaxed
                        px-4
                        py-3
                        rounded-2xl
                        rounded-tr-sm
                      "
                    >
                      {sharePreview.userQuery}
                    </div>

                  </div>

                </div>

                <div className="px-4 pb-4">

                  <div
                    className="
                      bg-[#111A2B]
                      border
                      border-slate-800
                      border-l-2
                      border-l-amber-500
                      rounded-2xl
                      rounded-tl-sm
                      p-4
                      relative
                    "
                  >

                    <div
                      className="
                        prose
                        prose-invert
                        prose-sm
                        max-w-none
                        leading-relaxed
                        text-slate-300
                        max-h-40
                        overflow-hidden
                      "
                    >
                      <ReactMarkdown>
                        {sharePreview.botAnswer}
                      </ReactMarkdown>
                    </div>

                    <div className="flex justify-end mt-3">

                      <div
                        className="
                          flex
                          items-center
                          gap-1.5
                          text-[10px]
                          font-medium
                          text-slate-500
                          bg-slate-800/70
                          border
                          border-slate-700
                          px-2
                          py-1
                          rounded-full
                        "
                      >

                        <Sparkles
                          className="
                            w-3
                            h-3
                            text-amber-400
                          "
                        />

                        <span>
                          IP-SAKTI Sahayak
                        </span>

                      </div>

                    </div>

                  </div>

                </div>

              </div>

            </div>

            <div
              className="
                grid
                grid-cols-4
                gap-3
                px-5
                py-5
              "
            >

              {/* COPY */}

              <button
                type="button"
                onClick={async () => {
                  const copied =
                    await copyShareLink(
                      window.location.href
                    );

                  if (copied) {
                    setLinkCopied(true);

                    setTimeout(() => {
                      setLinkCopied(false);
                    }, 2000);
                  }
                }}
                className="
                  flex
                  flex-col
                  items-center
                  justify-center
                  gap-2
                  group
                "
              >

                <div
                  className="
                    w-12
                    h-12
                    rounded-full
                    bg-slate-800
                    border
                    border-slate-700
                    flex
                    items-center
                    justify-center
                    text-slate-300
                    group-hover:bg-slate-700
                    group-hover:text-slate-100
                    group-hover:border-slate-600
                    transition-all
                  "
                >

                  {linkCopied ? (
                    <Check className="w-5 h-5 text-emerald-400" />
                  ) : (
                    <LinkIcon className="w-5 h-5" />
                  )}

                </div>

                <span
                  className="
                    text-[11px]
                    text-slate-400
                    group-hover:text-slate-200
                  "
                >
                  {linkCopied
                    ? 'Copied'
                    : 'Copy link'}
                </span>

              </button>

              {/* WHATSAPP */}

              <button
                type="button"
                onClick={() =>
                  shareToWhatsApp(
                    window.location.href,
                    sharePreview
                  )
                }
                className="
                  flex
                  flex-col
                  items-center
                  justify-center
                  gap-2
                  group
                "
              >

                <div
                  className="
                    w-12
                    h-12
                    rounded-full
                    bg-slate-800
                    border
                    border-slate-700
                    flex
                    items-center
                    justify-center
                    text-slate-300
                    group-hover:bg-emerald-500/15
                    group-hover:text-emerald-400
                    group-hover:border-emerald-500/30
                    transition-all
                  "
                >
                  <MessageCircle className="w-5 h-5" />
                </div>

                <span
                  className="
                    text-[11px]
                    text-slate-400
                    group-hover:text-slate-200
                  "
                >
                  WhatsApp
                </span>

              </button>

              {/* LINKEDIN */}

              <button
                type="button"
                onClick={() =>
                  shareToLinkedIn(
                    window.location.href
                  )
                }
                className="
                  flex
                  flex-col
                  items-center
                  justify-center
                  gap-2
                  group
                "
              >

                <div
                  className="
                    w-12
                    h-12
                    rounded-full
                    bg-slate-800
                    border
                    border-slate-700
                    flex
                    items-center
                    justify-center
                    text-slate-300
                    group-hover:bg-blue-500/15
                    group-hover:text-blue-400
                    group-hover:border-blue-500/30
                    transition-all
                  "
                >
                  <Share2 className="w-5 h-5" />
                </div>

                <span
                  className="
                    text-[11px]
                    text-slate-400
                    group-hover:text-slate-200
                  "
                >
                  LinkedIn
                </span>

              </button>

              {/* REDDIT */}

              <button
                type="button"
                onClick={() =>
                  shareToReddit(
                    window.location.href,
                    sharePreview
                  )
                }
                className="
                  flex
                  flex-col
                  items-center
                  justify-center
                  gap-2
                  group
                "
              >

                <div
                  className="
                    w-12
                    h-12
                    rounded-full
                    bg-slate-800
                    border
                    border-slate-700
                    flex
                    items-center
                    justify-center
                    text-slate-300
                    group-hover:bg-orange-500/15
                    group-hover:text-orange-400
                    group-hover:border-orange-500/30
                    transition-all
                  "
                >
                  <MessageCircle className="w-5 h-5" />
                </div>

                <span
                  className="
                    text-[11px]
                    text-slate-400
                    group-hover:text-slate-200
                  "
                >
                  Reddit
                </span>

              </button>

            </div>

            {/* FOOTER */}

            <div className="px-5 pb-5">

              <div
                className="
                  flex
                  items-center
                  justify-center
                  gap-2
                  text-[10px]
                  text-slate-600
                "
              >

                <Scale className="w-3 h-3" />

                <span>
                  IP-SAKTI Sahayak
                </span>

                <span>•</span>

                <span>
                  AI Legal Research Assistant
                </span>

              </div>

            </div>

          </div>

        </div>
      )}

    </div>
  );
}
