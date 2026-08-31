
import React, { useEffect, useState } from 'react';

import ReactMarkdown from 'react-markdown';

import {
  RefreshCw,
  BookOpen,
  X,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

export default function MessageList({
  messages,
  loading,
  chatEndRef,
}) {

  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedImageIndex, setSelectedImageIndex] =
    useState(0);
  const [previewImages, setPreviewImages] = useState([]);

  const openImagePreview = (images, index) => {
    setPreviewImages(images.slice(0, 4));
    setSelectedImageIndex(index);
    setSelectedImage(images[index]);
  };

  const closeImagePreview = () => {
    setSelectedImage(null);
    setPreviewImages([]);
    setSelectedImageIndex(0);
  };

  const showPreviousImage = (event) => {
    event.stopPropagation();

    if (previewImages.length === 0) {
      return;
    }

    const newIndex =
      selectedImageIndex === 0
        ? previewImages.length - 1
        : selectedImageIndex - 1;

    setSelectedImageIndex(newIndex);
    setSelectedImage(previewImages[newIndex]);
  };

  const showNextImage = (event) => {
    event.stopPropagation();

    if (previewImages.length === 0) {
      return;
    }

    const newIndex =
      selectedImageIndex ===
      previewImages.length - 1
        ? 0
        : selectedImageIndex + 1;

    setSelectedImageIndex(newIndex);
    setSelectedImage(previewImages[newIndex]);
  };

  useEffect(() => {
    if (!selectedImage) {
      return;
    }

    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        closeImagePreview();
      }

      if (event.key === 'ArrowLeft') {
        showPreviousImage(event);
      }

      if (event.key === 'ArrowRight') {
        showNextImage(event);
      }
    };

    document.addEventListener(
      'keydown',
      handleKeyDown
    );

    return () => {
      document.removeEventListener(
        'keydown',
        handleKeyDown
      );
    };
  }, [
    selectedImage,
    selectedImageIndex,
    previewImages,
  ]);


  const getImageTopic = (msg) => {
    if (!msg.search_query) {
      return 'Related Images';
    }

    return msg.search_query
      .replace(/\s+/g, ' ')
      .trim()
      .replace(/\b\w/g, (char) =>
        char.toUpperCase()
      );
  };

  const getImageSources = (images) => {
    if (!Array.isArray(images)) {
      return [];
    }

    return [
      ...new Set(
        images
          .map((image) => image.source)
          .filter(Boolean)
      ),
    ];
  };

  return (
    <>
      <main
        className="
          flex-1
          overflow-y-auto
          px-4
          py-5
          md:px-6
          md:py-6
        "
      >
        <div
          className="
            max-w-4xl
            mx-auto
            space-y-5
          "
        >
          {messages.map((msg, idx) => {
            const isUser =
              msg.sender === 'user';

            const hasImages =
              !isUser &&
              msg.show_images === true &&
              Array.isArray(msg.images) &&
              msg.images.length > 0;

            const imageSources =
              getImageSources(msg.images);

            return (
              <div
                key={idx}
                className={`
                  flex
                  ${
                    isUser
                      ? 'justify-end'
                      : 'justify-start'
                  }
                `}
              >
                <div
                  className={`
                    ${
                      isUser
                        ? 'max-w-[85%]'
                        : 'w-full max-w-[900px]'
                    }

                    rounded-2xl
                    shadow-sm

                    ${
                      isUser
                        ? `
                          bg-slate-700
                          text-slate-100
                          rounded-tr-none
                          px-4
                          py-3
                        `
                        : msg.isError
                        ? `
                          bg-rose-950/80
                          border
                          border-rose-800
                          text-rose-200
                          rounded-tl-sm
                          p-5
                        `
                        : `
                          bg-[#111A2B]
                          border
                          border-slate-800
                          border-l-2
                          border-l-amber-500
                          text-slate-200
                          rounded-tl-sm
                          p-5
                        `
                    }
                  `}
                >
                  {isUser ? (
                    <div
                      className="
                        text-sm
                        md:text-[15px]
                        leading-relaxed
                        whitespace-pre-wrap
                      "
                    >
                      {msg.text}
                    </div>
                  ) : (
                    <>
                      {hasImages && (
                        <div className="mb-5">
                          <div
                            className="
                              text-lg
                              text-slate-300
                              mb-3
                            "
                          >
                            <span className="font-semibold text-slate-200">
                              Topic:
                            </span>{' '}
                            {getImageTopic(msg)}
                          </div>
          
                          <div
                            className="
                              text-sm
                              font-semibold
                              text-slate-300
                              mb-3
                            "
                          >
                            Related Images
                          </div>
                          <div
                            className="
                              grid
                              grid-cols-2
                              sm:grid-cols-4
                              gap-3
                            "
                          >
                            {msg.images
                              .slice(0, 4)
                              .map((image, imageIndex) => (
                                <button
                                  key={imageIndex}
                                  type="button"
                                  onClick={() =>
                                    openImagePreview(
                                      msg.images,
                                      imageIndex
                                    )
                                  }
                                  className="
                                    group
                                    relative
                                    block
                                    w-full
                                    h-[125px]
                                    md:h-[135px]
                                    overflow-hidden
                                    rounded-xl
                                    border
                                    border-slate-700
                                    bg-slate-900
                                    transition
                                    duration-200
                                    hover:border-slate-500
                                    hover:shadow-lg
                                    cursor-zoom-in
                                    p-0
                                    text-left
                                  "
                                  aria-label={`View ${
                                    image.title ||
                                    'related legal image'
                                  }`}
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
                                    className="
                                      w-full
                                      h-full
                                      object-cover
                                      block
                                      transition
                                      duration-300
                                      group-hover:scale-105
                                    "
                                    onError={(event) => {
                                      const img =
                                        event.currentTarget;

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

                                  <div
                                    className="
                                      absolute
                                      inset-0
                                      bg-black/0
                                      group-hover:bg-black/20
                                      transition
                                      duration-200
                                    "
                                  />
                                </button>
                              ))}
                          </div>

                          {imageSources.length > 0 && (
                            <div
                              className="
                                mt-3
                                pt-3
                                border-t
                                border-slate-800
                              "
                            >
                              <div
                                className="
                                  flex
                                  items-center
                                  gap-2
                                  text-xs
                                  text-slate-400
                                "
                              >
                                <BookOpen
                                  className="
                                    w-3.5
                                    h-3.5
                                    text-emerald-400
                                  "
                                />

                                <span
                                  className="
                                    font-semibold
                                    text-slate-300
                                  "
                                >
                                  Sources
                                </span>

                                <span className="text-slate-600">
                                  •
                                </span>

                                <span>
                                  {imageSources.join(
                                    '  •  '
                                  )}
                                </span>
                              </div>
                            </div>
                          )}

                        </div>
                      )}

                      <div
                        className="
                          text-sm
                          md:text-base
                          max-w-none
                          leading-7
                          text-slate-300
                        "
                      >
                        <ReactMarkdown
                          components={{
                            p: ({ children }) => (
                              <p className="mb-5 leading-7 text-slate-300 last:mb-0">
                                {children}
                              </p>
                            ),

                            h1: ({ children }) => (
                              <h1 className="text-2xl font-bold text-slate-100 mt-6 mb-4">
                                {children}
                              </h1>
                            ),

                            h2: ({ children }) => (
                              <h2 className="text-xl font-semibold text-slate-100 mt-6 mb-4">
                                {children}
                              </h2>
                            ),

                            h3: ({ children }) => (
                              <h3 className="text-lg font-semibold text-slate-100 mt-5 mb-3">
                                {children}
                              </h3>
                            ),

                            ul: ({ children }) => (
                              <ul className="list-disc pl-6 mb-5 space-y-2">
                                {children}
                              </ul>
                            ),

                            ol: ({ children }) => (
                              <ol className="list-decimal pl-6 mb-5 space-y-2">
                                {children}
                              </ol>
                            ),

                            li: ({ children }) => (
                              <li className="leading-7 text-slate-300">
                                {children}
                              </li>
                            ),

                            strong: ({ children }) => (
                              <strong className="font-semibold text-slate-100">
                                {children}
                              </strong>
                            ),

                            em: ({ children }) => (
                              <em className="text-slate-200">
                                {children}
                              </em>
                            ),

                            blockquote: ({ children }) => (
                              <blockquote className="my-5 border-l-2 border-amber-500 pl-4 italic text-slate-400">
                                {children}
                              </blockquote>
                            ),

                            hr: () => (
                              <hr className="my-6 border-slate-700" />
                            ),

                            a: ({ href, children }) => (
                              <a
                                href={href}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-amber-400 hover:text-amber-300 underline"
                              >
                                {children}
                              </a>
                            ),
                          }}
                        >
                          {msg.text}
                        </ReactMarkdown>
                      </div>

                      {msg.sources &&
                        msg.sources.length > 0 && (
                          <div
                            className="
                              mt-5
                              pt-3
                              border-t
                              border-slate-800
                              flex
                              items-start
                              gap-2
                              text-xs
                              text-emerald-400/90
                            "
                          >
                            <BookOpen
                              className="
                                w-3.5
                                h-3.5
                                mt-0.5
                                shrink-0
                              "
                            />

                            <span>
                              <span
                                className="
                                  font-semibold
                                  text-emerald-300
                                "
                              >
                                Legal Sources:
                              </span>{' '}

                              {msg.sources.join(', ')}
                            </span>
                          </div>
                        )}
                    </>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex justify-start">
              <div
                className="
                  bg-[#111A2B]
                  border
                  border-slate-800
                  border-l-2
                  border-l-amber-500
                  text-slate-400
                  rounded-2xl
                  rounded-tl-sm
                  px-4
                  py-3
                  flex
                  items-center
                  gap-3
                "
              >
                <RefreshCw
                  className="
                    w-4
                    h-4
                    animate-spin
                    text-amber-400
                  "
                />

                <span className="text-sm">
                  Searching statutory context & verifying laws...
                </span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </main>

      {selectedImage && (
        <div
          className="
            fixed
            inset-0
            z-50
            flex
            items-center
            justify-center
            bg-black/85
            backdrop-blur-sm
            p-4
            md:p-8
          "
          onClick={closeImagePreview}
        >

          <button
            type="button"
            onClick={closeImagePreview}
            className="
              absolute
              top-4
              right-4
              md:top-6
              md:right-6
              z-20
              flex
              items-center
              justify-center
              w-10
              h-10
              rounded-full
              bg-slate-900/90
              border
              border-slate-700
              text-slate-200
              hover:bg-slate-800
              hover:text-white
              transition
            "
            aria-label="Close image preview"
          >
            <X className="w-5 h-5" />
          </button>

          {previewImages.length > 1 && (
            <div
              className="
                absolute
                top-5
                left-1/2
                -translate-x-1/2
                z-20
                px-3
                py-1
                rounded-full
                bg-slate-900/80
                border
                border-slate-700
                text-xs
                text-slate-300
              "
            >
              {selectedImageIndex + 1} /{' '}
              {previewImages.length}
            </div>
          )}

          {previewImages.length > 1 && (
            <button
              type="button"
              onClick={showPreviousImage}
              className="
                absolute
                left-3
                md:left-6
                top-1/2
                -translate-y-1/2
                z-20
                flex
                items-center
                justify-center
                w-11
                h-11
                md:w-12
                md:h-12
                rounded-full
                bg-slate-900/90
                border
                border-slate-700
                text-slate-200
                hover:bg-slate-800
                hover:text-white
                transition
                shadow-xl
              "
              aria-label="Previous image"
            >
              <ChevronLeft className="w-6 h-6" />
            </button>
          )}

          {previewImages.length > 1 && (
            <button
              type="button"
              onClick={showNextImage}
              className="
                absolute
                right-3
                md:right-6
                top-1/2
                -translate-y-1/2
                z-20
                flex
                items-center
                justify-center
                w-11
                h-11
                md:w-12
                md:h-12
                rounded-full
                bg-slate-900/90
                border
                border-slate-700
                text-slate-200
                hover:bg-slate-800
                hover:text-white
                transition
                shadow-xl
              "
              aria-label="Next image"
            >
              <ChevronRight className="w-6 h-6" />
            </button>
          )}

          <div
            className="
              relative
              max-w-6xl
              max-h-[90vh]
              flex
              items-center
              justify-center
            "
            onClick={(event) =>
              event.stopPropagation()
            }
          >
            <img
              src={
                selectedImage.url ||
                selectedImage.thumbnail
              }
              alt={
                selectedImage.title ||
                'Related legal image'
              }
              className="
                max-w-[85vw]
                max-h-[82vh]
                object-contain
                rounded-xl
                shadow-2xl
              "
            />
          </div>
        </div>
      )}
    </>
  );
}

