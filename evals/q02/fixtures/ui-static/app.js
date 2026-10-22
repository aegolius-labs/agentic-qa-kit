document.getElementById("signup").addEventListener("submit", (event) => {
  event.preventDefault();
  const payload = {
    email: document.getElementById("email").value,
    name: document.getElementById("name").value,
    consent: document.getElementById("consent").checked,
  };
  const errors = validateSignup(payload);
  const box = document.getElementById("error");
  box.hidden = errors.length === 0;
  box.textContent = errors.join(" ");
  if (errors.length === 0) console.log("subscribe", payload);
});
