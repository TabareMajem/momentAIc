# Google MCP Server Setup

To enable the AI to access your Gmail, Calendar, and Drive, you need to provide Google OAuth credentials.

## Steps
1.  Go to [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new Project (e.g., "MomentAIc MCP").
3.  **Enable APIs:**
    *   Gmail API
    *   Google Calendar API
    *   Google Drive API
4.  **Configure OAuth Consent Screen:**
    *   User Type: External (or Internal if you have a Workspace org).
    *   Scopes: `https://www.googleapis.com/auth/gmail.readonly`, `https://www.googleapis.com/auth/calendar`, `https://www.googleapis.com/auth/drive.readonly`.
    *   Add your email as a Test User.
5.  **Create Credentials:**
    *   Create OAuth Client ID -> **Desktop App**.
    *   Download the JSON file.
6.  **Upload:**
    *   Rename the file to `client_secret.json`.
    *   Upload it to this directory: `/root/momentaic/momentaic-backend/servers/google/client_secret.json`.

Once uploaded, the AI will use this file to authenticate.
