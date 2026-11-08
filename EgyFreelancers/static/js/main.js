/* Site-wide behaviour: mobile menu + hero video controls. Smooth anchor scrolling is handled in CSS. */
document.addEventListener("DOMContentLoaded", () => {
  /* ---- Mobile navigation ---- */
  const header = document.getElementById("site-header");
  const toggle = document.querySelector("[data-nav-toggle]");
  if (header && toggle) {
    const setOpen = (open) => {
      header.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.textContent = open ? "Close" : "Menu";
    };
    toggle.addEventListener("click", () => setOpen(!header.classList.contains("is-open")));
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && header.classList.contains("is-open")) { setOpen(false); toggle.focus(); } });
    document.addEventListener("click", (e) => { if (header.classList.contains("is-open") && !header.contains(e.target)) setOpen(false); });
    header.querySelectorAll(".site-menu a").forEach((a) => a.addEventListener("click", () => setOpen(false)));
    window.matchMedia("(min-width: 961px)").addEventListener("change", (e) => { if (e.matches) setOpen(false); });
  }

  /* ---- Hero video: fallback, pause control, reduced motion ---- */
  const media = document.querySelector("[data-hero-media]");
  const video = media && media.querySelector("video");
  if (video) {
    const button = media.querySelector("[data-video-toggle]");
    const useFallback = () => { media.classList.add("is-fallback"); if (button) button.hidden = true; };
    // 'error' does not bubble from <source>, so listen in the capture phase.
    video.addEventListener("error", useFallback, true);

    const setPlaying = (play) => {
      if (play) { const p = video.play(); if (p && p.catch) p.catch(() => {}); }
      else video.pause();
    };
    if (button) {
      button.hidden = false;
      // keep the label truthful even when the browser pauses/resumes the video itself
      const sync = () => { button.textContent = video.paused ? "Play video" : "Pause video"; };
      video.addEventListener("play", sync);
      video.addEventListener("pause", sync);
      button.addEventListener("click", () => setPlaying(video.paused));
    }
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      video.removeAttribute("autoplay");
      setPlaying(false);
    }
  }
});
