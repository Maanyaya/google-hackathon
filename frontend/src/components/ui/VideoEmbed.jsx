/**
 * Embeds YouTube, Google Drive, Loom, or direct MP4/WebM URLs.
 */
function PlayIcon() {
  return (
    <svg width="64" height="64" viewBox="0 0 64 64" fill="none" aria-hidden>
      <circle cx="32" cy="32" r="31" stroke="currentColor" strokeWidth="1.5" opacity="0.3" />
      <circle cx="32" cy="32" r="24" stroke="currentColor" strokeWidth="1.5" opacity="0.5" />
      <path d="M26 20l20 12-20 12V20z" fill="currentColor" />
    </svg>
  );
}

function normalizeEmbedUrl(url) {
  if (!url) return { embedUrl: "", mode: "none" };

  const isYoutube = url.includes("youtube") || url.includes("youtu.be");
  const isDrive = url.includes("drive.google");
  const isLoom = url.includes("loom.com");

  if (isYoutube) {
    const ytId = url.match(/(?:v=|youtu\.be\/)([^&?/]+)/)?.[1];
    if (ytId) {
      return {
        embedUrl: `https://www.youtube.com/embed/${ytId}?rel=0&modestbranding=1`,
        mode: "iframe",
      };
    }
  }
  if (isDrive) {
    const fileId = url.match(/\/d\/([^/]+)/)?.[1];
    if (fileId) {
      return {
        embedUrl: `https://drive.google.com/file/d/${fileId}/preview`,
        mode: "iframe",
      };
    }
  }
  if (isLoom) {
    return {
      embedUrl: url.replace("/share/", "/embed/"),
      mode: "iframe",
    };
  }

  return { embedUrl: url, mode: "video" };
}

export function VideoEmbed({
  url = "",
  title = "MoDeX video",
  placeholderTitle = "Video coming soon",
  placeholderLead = "Upload to YouTube, Google Drive, or Loom, then set the video URL.",
  placeholderHint = null,
  className = "demo-video-wrap",
}) {
  const { embedUrl, mode } = normalizeEmbedUrl(url);
  const hasVideo = !!url;

  if (!hasVideo) {
    return (
      <div className={className}>
        <div className="demo-video-placeholder">
          <div className="demo-play-ring">
            <PlayIcon />
          </div>
          <div className="demo-placeholder-copy">
            <h3>{placeholderTitle}</h3>
            <p>{placeholderLead}</p>
            {placeholderHint && <div className="demo-upload-hint">{placeholderHint}</div>}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="demo-video-frame">
        {mode === "iframe" ? (
          <iframe
            src={embedUrl}
            title={title}
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
            loading="lazy"
          />
        ) : (
          /* eslint-disable-next-line jsx-a11y/media-has-caption */
          <video src={embedUrl} controls preload="metadata" />
        )}
      </div>
    </div>
  );
}
