import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessage } from '../api/chatApi';

export const ChatWindow = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const [statute, setStatute] = useState('ALL');

  const chatEndRef = useRef(null);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({
      behavior: 'smooth',
    });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    if (e) e.preventDefault();

    if (!input.trim() || loading) return;

    const userText = input.trim();

    const userMessage = {
      role: 'user',
      content: userText,
    };

    const newHistory = [...messages, userMessage];

    setMessages(newHistory);
    setInput('');
    setLoading(true);

    try {
      const responseData = await sendChatMessage(
        userText,
        messages,
        language,
        statute
      );

      const images = Array.isArray(responseData.images)
        ? responseData.images.slice(0, 4)
        : [];

      const assistantMessage = {
        role: 'assistant',

        content:
          responseData.answer ||
          'No response returned from Sahayak.',

        show_images:
          responseData.show_images === true,

        search_query:
          responseData.search_query || '',

        images,
      };

      setMessages((prev) => [
        ...prev,
        assistantMessage,
      ]);
    } catch (err) {
      console.error('Chat error:', err);

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',

          content:
            '**System Error:** Unable to reach IP-SAKTI server. Please verify the backend is running.',

          show_images: false,

          search_query: '',

          images: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };



  const getImageTopic = (msg) => {
    if (!msg.search_query) {
      return 'Related Images';
    }

    return msg.search_query
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/\b\w/g, (char) => char.toUpperCase());
  };

  const getImageSources = (images) => {
    const sources = images
      .map((image) => image.source)
      .filter(Boolean);

    return [...new Set(sources)];
  };


  return (
    <div
      style={{
        maxWidth: '900px',
        margin: '20px auto',
        fontFamily: 'sans-serif',
      }}
    >

      <header
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '15px',
          gap: '20px',
          flexWrap: 'wrap',
        }}
      >
        <h2
          style={{
            margin: 0,
          }}
        >
          IP-SAKTI Sahayak
        </h2>

        <div
          style={{
            display: 'flex',
            gap: '15px',
            flexWrap: 'wrap',
          }}
        >
          <div>
            <label
              style={{
                marginRight: '8px',
                fontWeight: 'bold',
              }}
            >
              Statute Filter:
            </label>

            <select
              value={statute}
              onChange={(e) =>
                setStatute(e.target.value)
              }
              style={{
                padding: '5px 10px',
              }}
            >
              <option value="ALL">
                All Statutes
              </option>

              <option value="PA">
                Patents Act (PA)
              </option>

              <option value="GI">
                Geographical Indications (GI)
              </option>

              <option value="DR">
                Drugs Rules (DR)
              </option>

              <option value="DC">
                Drugs &amp; Cosmetics Act (DC)
              </option>
            </select>
          </div>


          <div>
            <label
              style={{
                marginRight: '8px',
                fontWeight: 'bold',
              }}
            >
              Language:
            </label>

            <select
              value={language}
              onChange={(e) =>
                setLanguage(e.target.value)
              }
              style={{
                padding: '5px 10px',
              }}
            >
              <option value="en">
                English
              </option>

              <option value="hi">
                Hindi (हिन्दी)
              </option>
            </select>
          </div>
        </div>
      </header>

      <div
        style={{
          height: '500px',
          overflowY: 'auto',
          border: '1px solid #ccc',
          borderRadius: '8px',
          padding: '15px',
          backgroundColor: '#f9f9f9',
        }}
      >
        {messages.map((msg, index) => (
          <div
            key={index}
            style={{
              display: 'flex',

              justifyContent:
                msg.role === 'user'
                  ? 'flex-end'
                  : 'flex-start',

              marginBottom: '20px',
            }}
          >
            <div
              style={{
                maxWidth:
                  msg.role === 'assistant'
                    ? '95%'
                    : '80%',

                padding: '10px 15px',

                borderRadius: '10px',

                backgroundColor:
                  msg.role === 'user'
                    ? '#007bff'
                    : '#ffffff',

                color:
                  msg.role === 'user'
                    ? '#ffffff'
                    : '#333333',

                boxShadow:
                  '0 1px 3px rgba(0,0,0,0.1)',
              }}
            >
              <strong>
                {msg.role === 'user'
                  ? 'You'
                  : 'Sahayak'}
                :
              </strong>
              {msg.role === 'user' ? (
                <p
                  style={{
                    margin: '5px 0 0 0',
                  }}
                >
                  {msg.content}
                </p>
              ) : (
                <>
                  {msg.show_images &&
                    Array.isArray(msg.images) &&
                    msg.images.length > 0 && (
                      <div
                        style={{
                          marginTop: '15px',
                          marginBottom: '20px',
                        }}
                      >
                        <div
                          style={{
                            fontSize: '18px',
                            fontWeight: '700',
                            color: '#222',
                            marginBottom: '14px',
                          }}
                        >
                          {getImageTopic(msg)}
                        </div>

                        <div
                          style={{
                            fontSize: '15px',
                            fontWeight: '600',
                            color: '#444',
                            marginBottom: '12px',
                          }}
                        >
                          Related images
                        </div>

                        <div
                          style={{
                            display: 'flex',
                            gap: '12px',

                            overflowX: 'auto',
                            overflowY: 'hidden',

                            paddingBottom: '10px',

                            scrollbarWidth: 'thin',

                            WebkitOverflowScrolling:
                              'touch',
                          }}
                        >
                          {msg.images
                            .slice(0, 4)
                            .map(
                              (
                                image,
                                imageIndex
                              ) => (
                                <a
                                  key={imageIndex}
                                  href={
                                    image.source_url ||
                                    image.url ||
                                    image.thumbnail
                                  }
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  style={{
                                    flex:
                                      '0 0 190px',

                                    height: '140px',

                                    borderRadius:
                                      '10px',

                                    overflow:
                                      'hidden',

                                    display:
                                      'block',

                                    backgroundColor:
                                      '#eee',

                                    border:
                                      '1px solid #ddd',

                                    textDecoration:
                                      'none',
                                  }}
                                >
                                  <img
                                    src={
                                      image.url ||
                                      image.thumbnail
                                    }
                                    alt={
                                      image.title ||
                                      'Related legal image'
                                    }
                                    loading="lazy"
                                    style={{
                                      width: '100%',
                                      height: '100%',
                                      objectFit:
                                        'cover',
                                      display:
                                        'block',
                                    }}
                                    onError={(e) => {
                                      const img =
                                        e.currentTarget;

                                      if (
                                        image.thumbnail &&
                                        img.src !==
                                          image.thumbnail
                                      ) {
                                        img.src =
                                          image.thumbnail;
                                      } else {
                                        img.style.display =
                                          'none';
                                      }
                                    }}
                                  />
                                </a>
                              )
                            )}
                        </div>
                        <div
                          style={{
                            marginTop: '8px',
                            paddingTop: '12px',
                            borderTop:
                              '1px solid #eee',
                          }}
                        >
                          {msg.search_query && (
                            <div
                              style={{
                                fontSize: '13px',
                                color: '#555',
                                marginBottom:
                                  '8px',
                              }}
                            >
                              <strong>
                                Topic:
                              </strong>{' '}
                              {msg.search_query}
                            </div>
                          )}

                          {getImageSources(
                            msg.images
                          ).length > 0 && (
                            <div
                              style={{
                                fontSize: '12px',
                                color: '#777',
                              }}
                            >
                              <strong>
                                Sources
                              </strong>
                              <br />

                              {getImageSources(
                                msg.images
                              ).map(
                                (
                                  source,
                                  sourceIndex
                                ) => (
                                  <React.Fragment
                                    key={source}
                                  >
                                    {source}

                                    {sourceIndex <
                                    getImageSources(
                                      msg.images
                                    ).length -
                                      1
                                      ? '  ·  '
                                      : ''}
                                  </React.Fragment>
                                )
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  <div
                    style={{
                      marginTop:
                        msg.show_images &&
                        msg.images?.length > 0
                          ? '5px'
                          : '10px',

                      lineHeight: '1.6',
                    }}
                  >
                    <ReactMarkdown>
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                </>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div
            style={{
              color: '#666',
              fontStyle: 'italic',
              margin: '10px 0',
            }}
          >
            Sahayak is analyzing statutory
            context...
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      <form
        onSubmit={handleSend}
        style={{
          display: 'flex',
          gap: '10px',
          marginTop: '15px',
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) =>
            setInput(e.target.value)
          }
          placeholder="Ask a legal query..."
          style={{
            flex: 1,
            padding: '12px',
            borderRadius: '6px',
            border: '1px solid #ccc',
          }}
        />

        <button
          type="submit"
          disabled={loading}
          style={{
            padding: '12px 24px',
            backgroundColor: '#007bff',
            color: '#fff',
            border: 'none',
            borderRadius: '6px',

            cursor: loading
              ? 'not-allowed'
              : 'pointer',
          }}
        >
          {loading ? '...' : 'Send'}
        </button>
      </form>
    </div>
  );
};
