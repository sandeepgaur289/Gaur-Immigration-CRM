GAUR PORTAL — SCIC | WWIC IMMIGRATION CRM v2.0 FINAL CANDIDATE

CORE MODULES INCLUDED
- Neutral GAUR secure login (company/role hidden until credentials are verified)
- MD combined access
- Smart Choice GM and White Wave GM isolated company access
- Reception visitor register
- Employee Information + photograph + documents
- Employee Performance: weekly/monthly/yearly, enrollment/revenue ranking, top 3, WhatsApp and Print/PDF
- Excel .xls/.xlsx Lead Upload
- Duplicate highlighting: same-company / cross-company / invalid mobile
- GM/MD quantity-wise lead allocation to AM
- Dynamic AM creation, deactivate/reactivate, and complete lead handover
- AM My Leads status/follow-up/remarks
- Enrollment / Payment / Filing client-case register
- LAN access for multiple office PCs using one shared server computer

FINAL LOGIN CREDENTIALS
MD
  Login ID: md.sandeep
  Password: Sandeep@2026

SMART CHOICE GM
  Login ID: gm.smartchoice
  Password: SCIC@GM2026#

WHITE WAVE GM
  Login ID: gm.whitewave
  Password: WWIC@GM2026#

SMART CHOICE RECEPTION
  Login ID: reception.scic
  Password: Welcome@123

WHITE WAVE RECEPTION
  Login ID: reception.wwic
  Password: Welcome@123

START
1. Extract folder.
2. Double-click START_CRM.bat.
3. Local browser: http://127.0.0.1:5050

OTHER OFFICE COMPUTERS
1. On server PC run ENABLE_OTHER_COMPUTERS.bat once as Administrator.
2. Run SHOW_SHARED_URL.bat.
3. Open the shown 192.168.x.x:5050 URL on other PCs on the same Wi-Fi/LAN.
4. Do NOT run another copy of the CRM on each computer if you want shared live data.

DATA SAFETY
- Database file: mini_crm.db
- Employee uploads: uploads/employees/
- Before replacing versions, copy mini_crm.db and uploads folder into the new application folder.


v2.0.1 START FIX
- Uses a separate v2 runtime so an old v1.6.3 dependency marker cannot skip installation.
- Keeps the Flask process in the visible server window so startup exceptions no longer disappear in a minimized child window.
- Browser opens after server launch; if startup fails, the exact Python error stays visible.
- If needed, run RESET_RUNTIME_IF_NEEDED.bat and then START_CRM.bat.
