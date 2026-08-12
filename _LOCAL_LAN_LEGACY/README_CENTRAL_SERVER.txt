GAUR | SCIC | WWIC Immigration CRM v2.1
CENTRAL SHARED SERVER EDITION

WHY YOUR DATA WAS NOT SYNCING
--------------------------------
If MD computer and GM computer both run their own START file,
each computer creates/uses its OWN mini_crm.db database.
Therefore:
- AM created on MD computer stays in MD computer's database.
- Visitor created on GM computer stays in GM computer's database.
They cannot see each other's records.

CORRECT FINAL ARCHITECTURE
--------------------------------
ONE MAIN COMPUTER = SERVER + DATABASE
ALL OTHER COMPUTERS = BROWSER CLIENTS ONLY

MAIN SERVER COMPUTER - FIRST TIME
--------------------------------
1. Extract this ZIP on ONE selected main/server computer.
2. Run 0_SERVER_ENABLE_NETWORK.bat once as instructed.
3. Run 1_SERVER_START.bat.
4. Keep that black server window OPEN.
5. Note the address shown, e.g.:
   http://192.168.1.4:5050

OTHER COMPUTERS (MD / GM / Reception / AM)
--------------------------------
1. They DO NOT run the CRM server.
2. They only run 2_CLIENT_CONNECT.bat.
3. First time, enter the main server URL:
   http://192.168.1.4:5050
4. Their browser opens the same GAUR login page.
5. Login credentials determine MD / SCIC / WWIC / AM permissions.

RESULT
--------------------------------
Every user reads and writes ONE central mini_crm.db.
So a visitor entered by SCIC GM appears to MD immediately after refresh.
An AM created by MD appears to the correct GM immediately after refresh.

NETWORK REQUIREMENTS
--------------------------------
- Server and client PCs must be on the same Wi-Fi/LAN for this edition.
- Main server PC must remain ON.
- 1_SERVER_START.bat must remain running.
- If server IP changes, run 3_CHANGE_SERVER_ADDRESS.bat on clients.

DATABASE SAFETY
--------------------------------
- SQLite now uses WAL mode and a 30-second busy timeout.
- One central server process handles all database access.
- Do NOT place mini_crm.db separately on each PC.

IMPORTANT
--------------------------------
If users must connect from different cities/networks, this LAN edition
must be moved to a cloud-hosted database/server. Do not run separate local copies.
