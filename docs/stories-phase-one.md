# Library Management System — Phase 1 API User Stories

## Authentication & Access Control

**As a** client application, **I want to** register, authenticate, and manage the lifecycle of user accounts through the API, **so that** I can build a secure, self-service authentication experience without staff involvement for routine account actions.

**Acceptance Criteria:**

*Sign-up*
- A new member can register with full name, email, password, and contact number (required fields configurable per library policy)
- Email addresses must be unique; attempting to register a duplicate email fails clearly and points toward the password-reset flow
- Passwords must meet minimum complexity requirements (e.g., 8+ characters, mix of letters/numbers)
- A confirmation email is sent on successful registration (optionally requiring verification before first login)
- New accounts default to "Member" role and "Active" status, with no admin approval needed

*Login*
- Valid credentials return an access token along with the user's role
- Invalid credentials fail with a generic error that doesn't reveal whether the email or password was wrong
- Repeated failed attempts (e.g., 5) temporarily lock the account, with an indication of when it will unlock

*Password reset*
- A user can request a password reset via email; the response doesn't reveal whether the email is registered
- The reset link/token expires after a configurable period (e.g., 30 minutes)
- Completing the reset requires a new password that meets complexity requirements

*Role-based access*
- Actions restricted to Admin or Librarian roles are rejected when attempted by a Member
- Actions restricted to Admin are rejected when attempted by a Librarian
- Permission failures are distinguishable from authentication failures (i.e., "you're logged in but not allowed" vs. "you're not logged in")

*Session management*
- Sessions/tokens expire after a configurable period of inactivity (e.g., 30 minutes)
- Requests made with an expired session fail with an indication that the session has expired, distinct from an invalid or missing session
- Users can obtain a new session without re-entering credentials, if a refresh mechanism is supported

*Login audit log*
- Admins can retrieve a history of login attempts, including timestamp, user, device/location info (if available), and success/failure
- The log can be filtered by date range and by user
- Only Admins can access this history

*Role updates*
- Admins can change a user's role; the change takes effect immediately, including for any active session
- Librarians cannot escalate their own or others' permissions
- The system prevents removing the last remaining Admin account
- Role changes are recorded in the audit log (who, when, old role, new role)

*Deactivation*
- Admins can deactivate a user account, optionally with a reason
- Deactivated users are blocked from logging in, with a message directing them to contact the library
- Any active session for a deactivated user ends immediately, not just on their next login attempt
- Deactivation preserves the user's borrowing history, fines, and profile data
- Deactivating a user with active loans or unresolved fines shows a warning but doesn't block the action
- Deactivation is recorded in the audit log

*Reactivation*
- Admins can reactivate a previously deactivated account, restoring login access with the user's existing credentials
- Reactivation is recorded in the audit log

<br>

## Catalog Management

**As a** Librarian client, **I want to** add, edit, remove, bulk-import, and tag catalog items through the API, **so that** the catalog stays accurate, searchable, and current for members.

**Acceptance Criteria:**

*Add item*
- A new item can be added with title, author, ISBN, category, and copy count; all required fields must be present before it's saved
- Adding an item with an ISBN that already exists is flagged, with the option to add it as an additional copy instead
- New items are searchable immediately after being added

*Edit item*
- An item's metadata can be updated, with changes reflected immediately in search results
- Edits are timestamped and retrievable as a history

*Remove item*
- An item can be archived (not permanently deleted) when lost, damaged, or withdrawn
- Archived items no longer appear in active search results but remain accessible for record-keeping
- Removing an item that's currently checked out requires an explicit override, with a warning shown first

*Bulk import*
- Items can be imported in bulk from a CSV/Excel file
- The file's format and required columns are validated before import
- Row-level errors (duplicates, missing fields) are reported individually without blocking the import of valid rows
- A successful import returns a summary of how many items were added, skipped, or failed

*Categorize and tag*
- An item can have one primary category and multiple tags
- Categories/tags can be selected from a predefined list or entered as free text, depending on configuration

<br>

## Search & Discovery

**As a** client application, **I want to** search, filter, paginate, and view catalog items through the API — with or without authentication — **so that** members and guests can find and evaluate items efficiently.

**Acceptance Criteria:**

*Keyword search*
- Items can be searched by title, author, or keyword, returning relevant results quickly (within ~2 seconds)
- Partial matches and common misspellings still return reasonable results

*Filtering*
- Search results can be filtered by availability, category, and format, with filters combinable (e.g., "Available" + "Fiction")
- The current filter/search state can be captured and shared (e.g., reproducible from a URL or equivalent reference)

*Item details*
- An item's detail view shows description, real-time availability, and copy count
- If unavailable, it shows an expected return date (if known) and an option to place a hold

*Guest access*
- Searching and viewing item details doesn't require login
- Borrowing history, holds, and checkout actions remain restricted to authenticated users

*Pagination*
- Search and browse results are paginated with a configurable page size (e.g., 20 items per page)
- Results indicate total count and current position (e.g., "Showing 21–40 of 128")
- Filters and search terms persist across page navigation
- Performance stays fast (under ~2 seconds) regardless of result set size

<br>

## Circulation Management

**As a** client application, **I want to** check items in and out, prevent invalid checkouts, list active loans, and renew loans through the API, **so that** the lending lifecycle of an item is tracked accurately from checkout through return.

**Acceptance Criteria:**

*Check out*
- An item can be checked out to a member by identifying the member and the item
- Checkout fails clearly if the member has reached their borrowing limit or has an unresolved suspension
- The due date is calculated automatically based on the item type's loan period
- Item availability updates immediately after checkout

*Check in*
- A returned item can be checked in, updating its availability immediately
- If the item was overdue, the return is flagged for fine calculation

*Prevent double checkout*
- Checkout is blocked when an item has no available copies
- In that case, placing a hold is offered as an alternative

*Active loans*
- A member's active loans and due dates can be retrieved
- Overdue items are clearly flagged

*Renewal*
- A borrowed item can be renewed if no one else is waiting on it
- Renewal is blocked once the item has a pending hold from another member, or once the maximum number of renewals has been reached
- The new due date is reflected immediately after a successful renewal