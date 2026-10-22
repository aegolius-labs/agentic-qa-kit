# Newsletter sign-up widget

A dependency-free sign-up form embedded on the marketing site. Open
`index.html` in a browser; there is no build step.

Rules the form enforces before it submits:

- The email must have a local part, an `@`, and a domain containing a dot.
- The display name is optional, at most 40 characters.
- The consent box must be ticked.

The submit handler posts to `https://api.example.com/subscribe` in production;
locally it only logs the payload to the console.
