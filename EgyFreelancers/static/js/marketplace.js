/* Marketplace: loads gigs from GET /api/gigs and renders gig cards on the homepage and /explore. */
const cats = { design: "Graphic design", development: "Web development", writing: "Writing & translation", marketing: "Marketing", video: "Video editing", business: "Business" };
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

function gigCard(g, imgBase) {
  const id = Number(g.id);
  const label = cats[g.category] || g.category;
  const known = Object.prototype.hasOwnProperty.call(cats, g.category);
  const media = known
    ? `<a class="gig-media" href="/gig/${id}" tabindex="-1" aria-hidden="true"><img src="${esc(imgBase)}cat-${esc(g.category)}.webp" width="640" height="400" loading="lazy" decoding="async" alt=""></a>`
    : `<a class="gig-media" href="/gig/${id}" tabindex="-1" aria-hidden="true"></a>`;
  return `<article class="gig-card">${media}<div class="gig-body">
    <span class="gig-cat">${esc(label)}</span>
    <h3><a href="/gig/${id}">${esc(g.title)}</a></h3>
    <p class="gig-desc">${esc(g.description)}</p>
    <div class="gig-seller"><span class="seller-avatar" aria-hidden="true">${esc((g.seller_name || "F")[0].toUpperCase())}</span><div><b>${esc(g.seller_name)}</b><small>Egyptian freelancer</small></div></div>
    <div class="gig-footer"><span>Starting at</span><b>${Number(g.price).toLocaleString("en-EG")} <small>EGP</small></b></div>
  </div></article>`;
}

async function load(target, params = {}) {
  if (!target) return;
  const imgBase = target.dataset.imgBase || "/static/img/";
  target.setAttribute("aria-busy", "true");
  target.innerHTML = '<div class="loading-card">Loading services…</div>';
  try {
    const q = new URLSearchParams(params);
    const r = await fetch("/api/gigs?" + q);
    const data = await r.json();
    if (!r.ok) throw Error(data.error || "Request failed");
    target.innerHTML = data.gigs.length
      ? data.gigs.map((g) => gigCard(g, imgBase)).join("")
      : '<div class="empty-state"><b>No services found yet</b><p>Try another search or category.</p></div>';
    const caption = document.getElementById("results-caption");
    if (caption) caption.textContent = `${data.gigs.length} ${data.gigs.length === 1 ? "service" : "services"} available`;
  } catch {
    target.innerHTML = '<div class="empty-state"><b>Could not load services</b><p>Make sure the Flask server is running.</p></div>';
  } finally {
    target.removeAttribute("aria-busy");
  }
}

/* Homepage: latest services */
load(document.getElementById("featured-gigs"));

/* Explore: search + category filter (read from the URL, as before) */
const results = document.getElementById("explore-gigs");
if (results) {
  const params = new URLSearchParams(location.search);
  const input = document.getElementById("search-input");
  if (input) input.value = params.get("search") || "";
  load(results, { search: params.get("search") || "", category: params.get("category") || "" });
  document.getElementById("explore-form")?.addEventListener("submit", (e) => {
    e.preventDefault();
    const u = new URL(location.href);
    const v = input.value.trim();
    v ? u.searchParams.set("search", v) : u.searchParams.delete("search");
    location.href = u.pathname + u.search;
  });
}
