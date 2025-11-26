*Plan for Share Modal*

1. **Share service** – Create `frontend/src/services/shareService.ts` providing `createShare`, `listShares`, and `revokeShare` wrappers around the asset share APIs, reusing `apiService` and surfacing tokens, expiration, and permission payloads.
2. **Share types** – Add `frontend/src/types/share.ts` (or extend `api.ts`) with `ShareLink`, `SharePermissions`, `CreateSharePayload`, etc. so modal/service share a consistent contract.
3. **Share modal** – Implement `frontend/src/components/modals/ShareModal.vue` that loads existing shares, lets users generate a link with expiration/password/permissions, copies tokens/URLs to clipboard, lists active shares with revoke/copy actions, and handles loading/errors/access controls per the spec (ARIA, keyboard, notifications).

*Plan for AssetPreview modal*

1. **Media contexts** – Decide what metadata/exif fields will be shown (name, size, mime, dimensions, created date) and whether the modal will receive a list of `Asset` objects (e.g., via props) so it can navigate prev/next; map asset mime_types to preview strategies (image, video, pdf).
2. **Layout & structure** – Create `frontend/src/components/modals/AssetPreviewModal.vue` with a full-screen overlay (`Modal`), central viewer area (image/video/pdf embed), nav buttons, metadata column/footer, and download/share buttons; include accessible controls and ARIA labels per TZ.
3. **Interaction logic** – Manage zoom/pan state (wheel events, reset on click, drag when zoomed), keyboard shortcuts (arrows for navigation, +/- wheel, Esc close, Space for controlling video), touch swipe detection for prev/next, metadata toggles, download link, share copy, and ensure video/audio controls work; keep state sync with props and emit events for close/nav.

