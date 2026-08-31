import React from 'react';

import {
  Scale,
  Plus,
  LogOut,
  PanelLeftClose,
  PanelLeftOpen,
  History,
  MessageSquare,
  Upload,
  ChevronDown,
  MoreHorizontal,
  Pin,
  Share2,
  Pencil,
  Trash2,
} from 'lucide-react';

import { STATUTE_GROUPS } from '../constants/statutes';

export default function Sidebar({
  user,
  imgError,
  setImgError,

  sidebarOpen,
  setSidebarOpen,

  activeStatute,
  setActiveStatute,

  expandedGroups,
  setExpandedGroups,

  chatHistoryList,
  historyLoading,
  activeChatId,

  startNewChat,
  setShowUploadModal,

  loadHistoryItem,

  openHistoryMenu,
  setOpenHistoryMenu,

  shareChat,
  renameChat,
  togglePinChat,
  deleteChat,

  requestDeleteChat,
  cancelDeleteChat,
  chatPendingDelete,

  logoutUser,
}) {

  const toggleGroup = (title) => {
    setExpandedGroups((prev) => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  const safeHistory = Array.isArray(chatHistoryList)
    ? chatHistoryList.filter(Boolean)
    : [];

  const safeGroups = Array.isArray(STATUTE_GROUPS)
    ? STATUTE_GROUPS.filter(Boolean)
    : [];

  const safeExpandedGroups =
    expandedGroups &&
    typeof expandedGroups === 'object'
      ? expandedGroups
      : {};

  return (
    <aside
      className={`
        fixed
        z-20
        top-0
        bottom-0
        left-0
        bg-[#111A2B]
        border-r
        border-slate-800/80
        flex
        flex-col
        py-4
        transition-all
        duration-300
        ease-in-out
        ${
          sidebarOpen
            ? 'w-72 px-4'
            : 'w-16 items-center px-2'
        }
      `}
    >
      <div
        className={`
          flex
          items-center
          mb-6
          w-full
          ${
            sidebarOpen
              ? 'justify-between pb-3 border-b border-slate-800'
              : 'justify-center'
          }
        `}
      >
        {sidebarOpen ? (
          <>
            <div
              className="
                flex
                items-center
                gap-2.5
                min-w-0
              "
            >
              <div
                className="
                  flex
                  h-9
                  w-9
                  items-center
                  justify-center
                  rounded-lg
                  border
                  border-amber-500/30
                  bg-amber-500/10
                  shrink-0
                  overflow-hidden
                "
              >
                <img
                  src="/logo.png"
                  alt="IP-SAKTI"
                  className="h-7 w-7 object-contain"
                />
              </div>

              <div className="min-w-0">
                <h1
                  className="
                    text-xs
                    font-bold
                    tracking-wide
                    text-amber-400
                    truncate
                  "
                >
                  IP-SAKTI Sahayak
                </h1>

                <p
                  className="
                    text-[9px]
                    text-slate-500
                    mt-0.5
                    truncate
                  "
                >
                  AI Legal Research Assistant
                </p>
              </div>
            </div>

            <div className="relative group">
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="
                  p-1.5
                  text-slate-400
                  hover:text-slate-100
                  hover:bg-slate-800
                  rounded-lg
                  transition
                "
                title="Close sidebar"
              >
                <PanelLeftClose className="w-5 h-5" />
              </button>

              <div
                className="
                  absolute
                  left-full
                  top-1/2
                  -translate-y-1/2
                  ml-2
                  hidden
                  group-hover:flex
                  items-center
                  bg-slate-200
                  text-slate-900
                  text-xs
                  font-medium
                  px-3
                  py-1.5
                  rounded-full
                  shadow-lg
                  whitespace-nowrap
                  z-30
                  pointer-events-none
                "
              >
                Close sidebar
              </div>
            </div>
          </>
        ) : (
          <div className="relative group">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="
                p-2
                text-slate-400
                hover:text-slate-100
                hover:bg-slate-800
                rounded-lg
                transition
              "
              title="Open sidebar"
            >
              <PanelLeftOpen className="w-5 h-5" />
            </button>

            <div
              className="
                absolute
                left-full
                top-1/2
                -translate-y-1/2
                ml-2
                hidden
                group-hover:flex
                items-center
                bg-slate-200
                text-slate-900
                text-xs
                font-medium
                px-3
                py-1.5
                rounded-full
                shadow-lg
                whitespace-nowrap
                z-30
                pointer-events-none
              "
            >
              Open sidebar
            </div>
          </div>
        )}
      </div>


      <div className="w-full mb-5 space-y-2">

        <button
          type="button"
          onClick={startNewChat}
          title={!sidebarOpen ? 'New Chat' : ''}
          className={`
            flex
            items-center
            gap-2
            text-sm
            font-medium
            text-amber-300
            border
            border-amber-700/50
            hover:bg-amber-500/10
            hover:border-amber-500
            rounded-xl
            transition-all
            ${
              sidebarOpen
                ? 'w-full px-3 py-2.5'
                : 'w-10 h-10 justify-center mx-auto'
            }
          `}
        >
          <Plus className="w-4 h-4 shrink-0" />

          {sidebarOpen && (
            <span>New Chat</span>
          )}
        </button>

        <button
          type="button"
          onClick={() => setShowUploadModal(true)}
          title={!sidebarOpen ? 'Upload Document' : ''}
          className={`
            flex
            items-center
            gap-2
            text-sm
            font-medium
            text-emerald-300
            border
            border-emerald-700/50
            hover:bg-emerald-500/10
            hover:border-emerald-500
            rounded-xl
            transition-all
            ${
              sidebarOpen
                ? 'w-full px-3 py-2.5'
                : 'w-10 h-10 justify-center mx-auto'
            }
          `}
        >
          <Upload className="w-4 h-4 shrink-0" />

          {sidebarOpen && (
            <span>Upload Document</span>
          )}
        </button>
      </div>

      <div
        className="
          w-full
          mb-4
          overflow-y-auto
          min-h-0
          pr-1
        "
      >
        {sidebarOpen && (
          <div
            className="
              flex
              items-center
              gap-2
              px-1
              mb-3
            "
          >
            <Scale
              className="
                w-3.5
                h-3.5
                text-amber-400
              "
            />

            <span
              className="
                text-[10px]
                font-mono
                tracking-widest
                uppercase
                text-slate-400
              "
            >
              Statutes
            </span>
          </div>
        )}

        {safeGroups.map((group, groupIndex) => {
          const isExpanded =
            safeExpandedGroups[group.title] ?? false;

          const safeItems = Array.isArray(group.items)
            ? group.items.filter(Boolean)
            : [];

          return (
            <div
              key={group.title || groupIndex}
              className={
                groupIndex === 0
                  ? 'mb-3'
                  : 'mb-4'
              }
            >

              {sidebarOpen && (
                <button
                  type="button"
                  onClick={() =>
                    toggleGroup(group.title)
                  }
                  className="
                    w-full
                    text-left
                    group
                    rounded-lg
                    hover:bg-slate-800/40
                    transition-colors
                    px-1
                    py-1
                    mb-1
                  "
                >
                  <div
                    className="
                      flex
                      items-center
                      justify-between
                      gap-2
                    "
                  >
                    <div className="min-w-0">
                      <div
                        className="
                          text-[9px]
                          font-bold
                          tracking-[0.14em]
                          text-slate-400
                          group-hover:text-slate-300
                          transition-colors
                        "
                      >
                        {group.title}
                      </div>

                      <div
                        className="
                          text-[9px]
                          text-slate-600
                          mt-0.5
                        "
                      >
                        {group.subtitle}
                      </div>
                    </div>

                    <ChevronDown
                      className={`
                        w-3.5
                        h-3.5
                        text-slate-500
                        shrink-0
                        transition-transform
                        duration-200
                        ${
                          isExpanded
                            ? 'rotate-0'
                            : '-rotate-90'
                        }
                      `}
                    />
                  </div>
                </button>
              )}

              {isExpanded && (
                <div className="space-y-0.5">
                  {safeItems.map((statute) => {
                    const Icon = statute.icon;

                    if (!Icon) {
                      return null;
                    }

                    const active =
                      statute.code === activeStatute;

                    return (
                      <button
                        key={statute.code}
                        type="button"
                        onClick={() =>
                          setActiveStatute(
                            statute.code
                          )
                        }
                        title={
                          !sidebarOpen
                            ? statute.label
                            : ''
                        }
                        className={`
                          flex
                          items-center
                          rounded-xl
                          transition-all
                          ${
                            sidebarOpen
                              ? 'w-full gap-2.5 text-[13px] px-2.5 py-2'
                              : 'w-10 h-10 justify-center mx-auto'
                          }
                          ${
                            active
                              ? 'bg-slate-800 text-slate-100 border border-slate-700'
                              : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200 border border-transparent'
                          }
                        `}
                      >
                        {sidebarOpen ? (
                          <>
                            <span
                              className={`
                                font-mono
                                text-[9px]
                                min-w-[30px]
                                text-center
                                px-1.5
                                py-0.5
                                rounded
                                ${
                                  active
                                    ? 'bg-amber-500 text-slate-900'
                                    : 'bg-slate-700/80 text-slate-300'
                                }
                              `}
                            >
                              {statute.code}
                            </span>

                            <Icon
                              className={`
                                w-3.5
                                h-3.5
                                shrink-0
                                ${
                                  active
                                    ? 'text-amber-400'
                                    : 'opacity-70'
                                }
                              `}
                            />

                            <span
                              className="
                                truncate
                                text-left
                              "
                            >
                              {statute.label}
                            </span>
                          </>
                        ) : (
                          <Icon
                            className={`
                              w-5
                              h-5
                              ${
                                active
                                  ? 'text-amber-400'
                                  : 'opacity-70'
                              }
                            `}
                          />
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      <div
        className="
          w-full
          flex-1
          overflow-y-auto
          min-h-0
          border-t
          border-slate-800/80
          pt-3
        "
      >
        {sidebarOpen ? (
          <>
            <div
              className="
                flex
                items-center
                gap-1
                text-[10px]
                font-mono
                tracking-widest
                uppercase
                text-slate-500
                mb-2
                px-1
              "
            >
              <History className="w-3 h-3" />

              <span>Recent History</span>
            </div>
            {historyLoading ? (
              <div
                className="
                  flex
                  items-center
                  gap-2
                  px-2
                  py-3
                  text-xs
                  text-slate-500
                "
              >
                <div
                  className="
                    w-3
                    h-3
                    rounded-full
                    border
                    border-slate-600
                    border-t-amber-400
                    animate-spin
                    shrink-0
                  "
                />

                <span>
                  Verifying consultations...
                </span>
              </div>
            ) : safeHistory.length === 0 ? (
              <div
                className="
                  px-2
                  py-3
                  text-[11px]
                  text-slate-600
                  leading-relaxed
                "
              >
                No previous consultations.
              </div>
            ) : (
              <div className="space-y-1">
                {safeHistory.map((item) => {
                  if (!item?.id) {
                    return null;
                  }

                  return (
                    <div
                      key={item.id}
                      className="
                        relative
                        w-full
                      "
                    >
                      <div
                        onClick={() =>
                          loadHistoryItem(item)
                        }
                        className={`
                          w-full
                          text-[12.5px]
                          hover:bg-slate-800/60
                          hover:text-slate-200
                          px-2.5
                          py-2
                          rounded-lg
                          transition-colors
                          flex
                          items-center
                          gap-2
                          cursor-pointer
                          group
                          ${
                            activeChatId === item.id
                              ? 'bg-slate-800/60 text-slate-200'
                              : 'text-slate-400'
                          }
                        `}
                      >
                        <MessageSquare
                          className="
                            w-3.5
                            h-3.5
                            shrink-0
                            text-amber-500/70
                          "
                        />

                        <span
                          className="
                            truncate
                            flex-1
                            min-w-0
                            text-left
                          "
                          title={
                            item.title ||
                            'Untitled consultation'
                          }
                        >
                          {item.title ||
                            'Untitled consultation'}
                        </span>

                        {item.pinned && (
                          <Pin
                            className="
                              w-3.5
                              h-3.5
                              shrink-0
                              text-amber-400
                              fill-amber-400
                              rotate-[-25deg]
                            "
                          />
                        )}

                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();

                            setOpenHistoryMenu(
                              (current) =>
                                current === item.id
                                  ? null
                                  : item.id
                            );
                          }}
                          className="
                            shrink-0
                            p-1
                            rounded-md
                            text-slate-500
                            hover:text-slate-200
                            hover:bg-slate-700
                            opacity-0
                            group-hover:opacity-100
                            focus:opacity-100
                            transition-all
                          "
                          title="Chat options"
                        >
                          <MoreHorizontal className="w-4 h-4" />
                        </button>
                      </div>

                      {openHistoryMenu === item.id && (
                        <div
                          onClick={(event) =>
                            event.stopPropagation()
                          }
                          className="
                            absolute
                            right-1
                            top-full
                            mt-1
                            z-50
                            w-44
                            bg-[#182235]
                            border
                            border-slate-700
                            rounded-xl
                            shadow-2xl
                            p-1
                          "
                        >

                          <button
                            type="button"
                            onClick={(event) =>
                              shareChat(
                                event,
                                item
                              )
                            }
                            className="
                              w-full
                              flex
                              items-center
                              gap-2.5
                              px-3
                              py-2
                              rounded-lg
                              text-xs
                              text-slate-300
                              hover:bg-slate-700
                              hover:text-slate-100
                              transition
                              text-left
                            "
                          >
                            <Share2 className="w-3.5 h-3.5" />

                            <span>Share</span>
                          </button>

                          <button
                            type="button"
                            onClick={(event) =>
                              renameChat(
                                event,
                                item
                              )
                            }
                            className="
                              w-full
                              flex
                              items-center
                              gap-2.5
                              px-3
                              py-2
                              rounded-lg
                              text-xs
                              text-slate-300
                              hover:bg-slate-700
                              hover:text-slate-100
                              transition
                              text-left
                            "
                          >
                            <Pencil className="w-3.5 h-3.5" />

                            <span>Rename</span>
                          </button>
                          <button
                            type="button"
                            onClick={(event) =>
                              togglePinChat(
                                event,
                                item
                              )
                            }
                            className="
                              w-full
                              flex
                              items-center
                              gap-2.5
                              px-3
                              py-2
                              rounded-lg
                              text-xs
                              text-slate-300
                              hover:bg-slate-700
                              hover:text-slate-100
                              transition
                              text-left
                            "
                          >
                            <Pin
                              className={`
                                w-3.5
                                h-3.5
                                ${
                                  item.pinned
                                    ? 'fill-amber-400 text-amber-400'
                                    : ''
                                }
                              `}
                            />

                            <span>
                              {item.pinned
                                ? 'Unpin chat'
                                : 'Pin chat'}
                            </span>
                          </button>

                          <div
                            className="
                              h-px
                              bg-slate-700
                              my-1
                            "
                          />

                          <button
                            type="button"
                            onClick={(event) =>
                              requestDeleteChat(
                                event,
                                item
                              )
                            }
                            className="
                              w-full
                              flex
                              items-center
                              gap-2.5
                              px-3
                              py-2
                              rounded-lg
                              text-xs
                              text-rose-400
                              hover:bg-rose-950/50
                              hover:text-rose-300
                              transition
                              text-left
                            "
                          >
                            <Trash2 className="w-3.5 h-3.5" />

                            <span>Delete</span>
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </>
        ) : (
          <div
            className="
              flex
              flex-col
              items-center
              gap-2
            "
          >
            {safeHistory.map((item) => {
              if (!item?.id) {
                return null;
              }

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() =>
                    loadHistoryItem(item)
                  }
                  title={
                    item.title ||
                    'Untitled consultation'
                  }
                  className="
                    w-10
                    h-10
                    flex
                    items-center
                    justify-center
                    rounded-xl
                    text-slate-400
                    hover:bg-slate-800
                    hover:text-amber-400
                    transition
                  "
                >
                  <MessageSquare className="w-4 h-4" />
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div
        className={`
          mt-auto
          pt-3
          border-t
          border-slate-800/80
          w-full
          flex
          flex-col
          ${
            sidebarOpen
              ? 'items-stretch'
              : 'items-center gap-3'
          }
        `}
      >
        <div
          className={`
            flex
            items-center
            ${
              sidebarOpen
                ? 'justify-between px-1'
                : 'flex-col gap-2'
            }
          `}
        >
          <div
            className="
              flex
              items-center
              gap-2
              min-w-0
            "
          >
            {user?.photoURL && !imgError ? (
              <img
                src={user.photoURL}
                alt={
                  user.displayName ||
                  'User Profile'
                }
                referrerPolicy="no-referrer"
                onError={() => setImgError(true)}
                className="
                  w-8
                  h-8
                  rounded-full
                  border
                  border-amber-500/40
                  shrink-0
                  object-cover
                "
              />
            ) : (
              <div
                className="
                  w-8
                  h-8
                  rounded-full
                  bg-amber-500/20
                  border
                  border-amber-500/40
                  text-amber-400
                  font-bold
                  text-xs
                  flex
                  items-center
                  justify-center
                  shrink-0
                "
              >
                {user?.displayName
                  ? user.displayName
                      .charAt(0)
                      .toUpperCase()
                  : 'U'}
              </div>
            )}

            {sidebarOpen && (
              <span
                className="
                  text-xs
                  font-medium
                  text-slate-300
                  truncate
                  max-w-[120px]
                "
              >
                {user?.displayName || 'User'}
              </span>
            )}
          </div>

          <button
            type="button"
            onClick={logoutUser}
            title="Sign out"
            className="
              p-2
              bg-slate-800/80
              hover:bg-slate-700
              text-slate-400
              hover:text-slate-200
              rounded-lg
              border
              border-slate-700
              transition
            "
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>

      {chatPendingDelete && (
        <div
          className="
            fixed
            inset-0
            z-[100]
            flex
            items-center
            justify-center
            bg-black/60
            backdrop-blur-sm
            px-4
          "
          onClick={cancelDeleteChat}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-chat-title"
            className="
              w-full
              max-w-[400px]
              rounded-2xl
              border
              border-slate-700/80
              bg-[#212121]
              p-6
              shadow-2xl
            "
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <h2
              id="delete-chat-title"
              className="
                text-[19px]
                font-semibold
                text-white
                mb-3
              "
            >
              Delete chat?
            </h2>

            <p
              className="
                text-sm
                leading-[1.5]
                text-slate-400
                mb-6
              "
            >
              This will delete{' '}
              <span className="font-semibold text-slate-200">
                {chatPendingDelete?.title || 'Untitled consultation'}
              </span>
              .
            </p>

            <div
              className="
                flex
                justify-end
                gap-2
              "
            >

              <button
                type="button"
                onClick={cancelDeleteChat}
                className="
                  h-10
                  px-4
                  rounded-full
                  bg-[#303030]
                  text-sm
                  font-medium
                  text-white
                  hover:bg-[#3a3a3a]
                  active:bg-[#404040]
                  transition
                "
              >
                Cancel
              </button>

              <button
                type="button"
                onClick={deleteChat}
                className="
                  h-10
                  px-4
                  rounded-full
                  bg-[#e53935]
                  text-sm
                  font-medium
                  text-white
                  hover:bg-[#d32f2f]
                  active:bg-[#c62828]
                  transition
                "
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

