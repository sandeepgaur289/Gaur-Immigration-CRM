SCIC | WWIC Mini Immigration CRM v1.0.1 — Login Fixed

DAILY START
1. Extract the ZIP.
2. Double-click START_CRM.bat.
3. Browser opens at http://127.0.0.1:5050
4. Keep the black CRM window open while using the app.

FIX IN THIS VERSION
- Core MD/GM/Reception accounts are automatically repaired on every app start.
- Core passwords are reset to the known credentials below on startup.
- Login IDs are case-insensitive.
- No need to delete mini_crm.db.

LOGIN DETAILS
MD:
  md.sandeep
  Sandeep@2026

Smart Choice GM:
  gm.scic
  SCIC@123

White Wave GM:
  gm.wwic
  WWIC@123

Smart Choice Reception:
  reception.scic
  Welcome@123

White Wave Reception:
  reception.wwic
  Welcome@123

Existing CRM data in mini_crm.db remains preserved.


NEW IN v1.1
- Employee Information menu for MD and GM
- Automatic Employee Code: SCIC-EMP-0001 / WWIC-EMP-0001
- Personal, employment and emergency-contact information
- Company / designation / department
- Joining date and employment status
- Limited ID/bank reference fields (last 4 digits for Aadhaar/account)
- Employee directory
- Edit employee information
- GM sees only own-company employees
- MD sees both companies


NEW IN v1.2
- Employee photograph upload
- Photograph preview in Employee Directory
- Employee document vault
- Educational certificates / degree / diploma uploads
- ID proof / address proof / PAN / Aadhaar / passport copies
- Bank documents / resume / experience certificates
- PDF, JPG, PNG, WEBP, DOC, DOCX support
- Documents are stored inside uploads/employees/<employee-code>/
- MD can access both companies; GM only own-company employee files
- Existing v1.1 employee data is automatically migrated


NEW IN v1.3
- Individual Performance Page for every employee
- Weekly, Monthly and Yearly reports
- Daily performance entries
- Leads assigned, calls, follow-ups, office visits
- Interested clients and enrollments
- Collection amount and target amount
- Conversion percentage and target-achievement percentage
- Manager rating and feedback
- Attendance status
- Performance progress bars
- WhatsApp-ready performance summary
- Copy Report Text button
- Share on WhatsApp button (user selects the official group in WhatsApp)


IMPORTANT v1.3.1 VISIBILITY FIX
- New top-level menu: Employee Performance
- Employee Performance Dashboard lists every employee
- Each employee has Open Performance button
- Employee Information page shows a Performance Module Active banner
- Performance page shows v1.3.1 ACTIVE banner
- App sidebar visibly shows v1.3.1 so you can confirm the correct build is running

If you do not see "v1.3.1" in the left sidebar, the old folder/version is still running.


NEW IN v1.4
- Top 3 Employee Performance Ranking: 1st / 2nd / 3rd
- Performance ranking line graph
- Weekly, Monthly and Yearly ranking views
- Transparent Performance Score formula:
  40% target achievement + 30% conversion + 20% call completion + 10% manager rating
- All Employee Rankings table
- Global WhatsApp Share button on every portal/page
- Global Print / Save PDF button on every portal/page
- Individual Employee Performance page also has dedicated WhatsApp and Print buttons
- Print-friendly CSS hides sidebar and action buttons


NEW IN v1.5 PREMIUM PERFORMANCE
- Premium Employee Performance Dashboard matching the approved dark navy/gold design direction
- KPI cards: total enrollments, total revenue, averages, active employees, top performer
- Top 3 premium ranking cards with crown / 1st / 2nd / 3rd
- Monthly trend graph for top 3 performers
- Enrollment-based and revenue-based donut visuals
- Employee Performance ranking table with score bars
- Ranking formula is now business-focused:
  40% Enrollment Weightage
  40% Revenue Weightage
  10% Target Achievement
  10% Manager Rating
- Weekly / Monthly / Yearly filters
- WhatsApp Share and Print / Save PDF remain available on all portals


NEW IN v1.6 — FINAL LOGIN STRUCTURE
- Separate premium Smart Choice login page
- Separate premium White Wave login page
- Dedicated Sandeep Gaur Managing Director portal
- MD portal accepts only md.sandeep
- Smart Choice login accepts only SCIC GM / Reception / AM users
- White Wave login accepts only WWIC GM / Reception / AM users
- New premium portal-selection landing screen
- Times New Roman, dark navy/gold executive styling retained


v1.6.1 — GAUR UNIVERSAL LOGIN (CORRECTED)
- Public/main page has ONE login only: GAUR PORTAL
- No Smart Choice logo/name on login page
- No White Wave logo/name on login page
- No company-selection cards
- No role-selection cards
- No indication before login which company the user belongs to
- Dramatic executive/cyber-security background artwork
- After valid credentials, database determines role + company automatically
- MD credential opens combined MD access
- SCIC credential opens permitted SCIC role/dashboard
- WWIC credential opens permitted WWIC role/dashboard
- Invalid credentials reveal no company information


v1.6.2 — FAST START FIX
Problem found from the screen recording:
- Every extracted version was creating a brand-new .venv
- pip was reinstalling packages at every first launch of that folder
- Browser was opening BEFORE Flask was ready, causing ERR_CONNECTION_REFUSED

Fixed:
- One shared runtime is reused from %LOCALAPPDATA%\GaurCRM\venv
- Packages install only once, not on every CRM version
- Browser opens only AFTER http://127.0.0.1:5050 responds
- Normal later launches should be much faster
- START_CRM.bat now automatically uses the fast starter
- STOP_CRM.bat closes the minimized server
- REPAIR_RUNTIME.bat resets runtime only if ever needed; CRM data is preserved

IMPORTANT:
The very first launch can still take longer because Python packages must be installed once.
After that, future launches and future builds that use this shared runtime should start quickly.


v1.6.3 — LAN SHARED ACCESS
- The red Flask development-server text is only a warning, not an app error.
- 127.0.0.1 works only on the computer running the CRM.
- The server now listens on all LAN interfaces.
- Run ENABLE_OTHER_COMPUTERS.bat once on the main/server computer.
- Run SHOW_SHARED_URL.bat to get the address for the second computer.
- Example: http://192.168.1.25:5050
- Both computers must be on the same Wi-Fi/LAN.
- The main/server computer must stay ON while others use the CRM.
