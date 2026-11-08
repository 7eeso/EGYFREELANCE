/* Form behaviour: gig submission (POST /api/gigs), project placeholder, auth placeholders. */
const toObject = (form) => Object.fromEntries(new FormData(form).entries());
const showMessage = (form, text, state) => {
  const el = form.querySelector(".form-message");
  if (!el) return;
  el.textContent = text;
  if (state) el.dataset.state = state; else delete el.dataset.state;
};

/* Freelancer: post a gig (stored as "pending" by the backend) */
const gigForm = document.getElementById("gig-form");
gigForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  const button = gigForm.querySelector("button[type=submit]");
  button.disabled = true;
  button.textContent = "Submitting…";
  try {
    const res = await fetch("/api/gigs", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(toObject(gigForm)),
    });
    const data = await res.json();
    if (!res.ok) throw Error(data.error || "Submission failed");
    showMessage(gigForm, `Submitted for review. Reference #${data.gig_id}. Your gig is pending approval.`, "ok");
    gigForm.reset();
  } catch (err) {
    showMessage(gigForm, err.message, "error");
  } finally {
    button.disabled = false;
    button.textContent = "Submit for review";
  }
});

/* Client: project form (publishing needs client accounts, which don't exist yet) */
const projectForm = document.getElementById("project-form");
projectForm?.addEventListener("submit", (e) => {
  e.preventDefault();
  showMessage(projectForm, "Project publishing is coming with client accounts. Your form is ready.");
});

/* Login / register: native validation runs first, then an honest in-page notice instead of a popup */
document.querySelectorAll("form[data-notice]").forEach((form) => {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    showMessage(form, form.dataset.notice);
  });
});
