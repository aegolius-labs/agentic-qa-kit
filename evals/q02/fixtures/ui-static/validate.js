// Shared with the server-side handler; keep free of DOM access.
function validateSignup(input) {
  const errors = [];
  const email = (input.email || "").trim();
  if (!/^[^@\s]+@[^@\s]+$/.test(email)) errors.push("Enter a valid email address.");
  if ((input.name || "").length > 40) errors.push("Display name is too long.");
  if (!input.consent) errors.push("Please tick the consent box.");
  return errors;
}

if (typeof module !== "undefined") module.exports = { validateSignup };
