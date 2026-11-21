// Click a screenshot to see it full size. Arrow keys or the side buttons step through the
// screenshots on the page; Esc, the ✕ or a click outside the image closes it. Without
// JavaScript the page simply shows the thumbnails.
(() => {
  const shots = [...document.querySelectorAll(".shots img, .shots-wide img, .steps img")];
  if (!shots.length || !window.HTMLDialogElement) return;

  const box = document.createElement("dialog");
  box.className = "lightbox";
  box.innerHTML = `
    <button class="lb-close" aria-label="Close">✕</button>
    <button class="lb-prev" aria-label="Previous screenshot">‹</button>
    <figure><img alt=""><figcaption></figcaption></figure>
    <button class="lb-next" aria-label="Next screenshot">›</button>`;
  document.body.append(box);
  const img = box.querySelector("img");
  const caption = box.querySelector("figcaption");
  let current = 0;

  const show = (i) => {
    current = (i + shots.length) % shots.length;
    const s = shots[current];
    img.src = s.currentSrc || s.src;
    img.alt = s.alt;
    caption.textContent = s.alt;
  };
  const open = (i) => { show(i); box.showModal(); };

  shots.forEach((s, i) => {
    s.tabIndex = 0;
    s.setAttribute("role", "button");
    s.setAttribute("aria-label", `Enlarge: ${s.alt}`);
    s.addEventListener("click", () => open(i));
    s.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); open(i); }
    });
  });

  box.querySelector(".lb-close").addEventListener("click", () => box.close());
  box.querySelector(".lb-prev").addEventListener("click", () => show(current - 1));
  box.querySelector(".lb-next").addEventListener("click", () => show(current + 1));
  // A click on the dark area (the dialog itself, not its contents) closes it.
  box.addEventListener("click", (e) => { if (e.target === box || e.target.tagName === "FIGURE") box.close(); });
  box.addEventListener("keydown", (e) => {
    if (e.key === "ArrowLeft") show(current - 1);
    if (e.key === "ArrowRight") show(current + 1);
  });
  // Return focus to the thumbnail that was open, for keyboard users.
  box.addEventListener("close", () => shots[current].focus({ preventScroll: true }));
})();
