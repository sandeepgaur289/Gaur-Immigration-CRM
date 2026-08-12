THE GAUR CRM v3.18 — CHAT MEDIA + SECURE OFFICIAL DATA

NEW
• WhatsApp-style Browse Photo / Document option in Internal Chat.
• Employees can send JPG, JPEG, PNG, WEBP, PDF, DOC, DOCX, XLS, XLSX and TXT.
• Maximum attachment size: 10 MB.
• Employee-uploaded chat photos/docs can be viewed/downloaded by sender and recipient.
• Official CRM Lead Share remains a separate locked CRM object.
• Official lead/client data is NOT converted into a downloadable chat file.
• Chat attachment endpoint checks sender/recipient authorization before serving a file.
• Private/no-store headers used for chat attachments.

IMPORTANT SECURITY LIMIT
A browser cannot guarantee that information visible on screen can never be copied, photographed, screenshotted or captured.
Therefore v3.18 prevents normal official-data file download/export through chat, but no web application can promise absolute anti-theft once a user is allowed to view data.

RECOMMENDED NEXT SECURITY LAYER
• Watermark official client screens with employee name/login ID/date-time.
• Disable Print/Save PDF for non-management roles on official-data pages.
• Add audit log for client profile views and sensitive actions.
• Optional masking of phone/email/passport fields by role.

DEPLOY
Replace only root app.py from this ZIP, commit, wait for Railway success, then Ctrl+F5.
Do not change DATABASE_URL/PostgreSQL.
