export async function copyShareLink(shareUrl) {
  try {
    await navigator.clipboard.writeText(shareUrl);
    return true;
  } catch (error) {
    console.error('Could not copy link:', error);
    return false;
  }
}

export function shareToWhatsApp(shareUrl, sharePreview) {
  const text =
    `${sharePreview.title}\n\n` +
    `${sharePreview.userQuery}\n\n` +
    `${sharePreview.botAnswer}\n\n` +
    `Shared from IP-SAKTI Sahayak`;

  const whatsappUrl =
    `https://wa.me/?text=${encodeURIComponent(
      `${text}\n${shareUrl}`
    )}`;

  window.open(
    whatsappUrl,
    '_blank',
    'noopener,noreferrer'
  );
}

export function shareToLinkedIn(shareUrl) {
  const linkedInUrl =
    `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(
      shareUrl
    )}`;

  window.open(
    linkedInUrl,
    '_blank',
    'noopener,noreferrer'
  );
}

export function shareToReddit(shareUrl, sharePreview) {
  const redditUrl =
    `https://www.reddit.com/submit?url=${encodeURIComponent(
      shareUrl
    )}&title=${encodeURIComponent(
      sharePreview.title
    )}`;

  window.open(
    redditUrl,
    '_blank',
    'noopener,noreferrer'
  );
}