# Password Reset Flow

Actors:

- User
- Web App
- Auth API
- Email Service
- Audit Log

Happy path:

1. The user submits an email address in the Web App.
2. The Web App sends `POST /password-reset` to the Auth API.
3. The Auth API validates the request without revealing whether the account exists.
4. If the account exists, the Auth API creates a reset token, stores only the hash, and asks the Email Service to send the reset link.
5. The Auth API writes a security event to the Audit Log.
6. The Auth API returns a generic success response to the Web App.
7. The user opens the link and the Web App later submits the new password to the Auth API.

Guidance:

- Keep the focus on the main flow.
- Preserve the security-sensitive generic response behavior.
