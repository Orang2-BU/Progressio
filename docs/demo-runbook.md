# Local Progressio demo runbook

This runbook uses synthetic seeded data in an in-memory SQLite database. It
does not touch the project database or call paid AI/blockchain providers. Each
backend process starts empty and loses all accounts, progress, submissions, and
credentials when stopped.

## Prerequisites

- Python 3.12 and Node.js 20.19 or newer.
- Run commands from the repository root in PowerShell.

Bootstrap a fresh checkout once:

```powershell
python -m venv back-end/.venv
back-end/.venv/Scripts/python.exe -m pip install -r back-end/requirements.txt
Push-Location front-end
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency install failed ($LASTEXITCODE)" }
} finally {
    Pop-Location
}
```

On POSIX, use `back-end/.venv/bin/python` for the backend interpreter. The
runtime script starts its own disposable SQLite database; it does not use the
venv's default database or the project database.

## Clean start

1. Start the disposable backend in terminal 1:

   ```powershell
   back-end/.venv/Scripts/python.exe front-end/tests/backend_server.py --catalog
   ```

   Wait for `Disposable backend: http://127.0.0.1:8011 (in-memory DB)`. The
   `--catalog` flag imports the repository curriculum and creates synthetic demo
   users, including `student`; account setup is defined in
   `back-end/apps/common/management/commands/seed_demo.py`.

   On POSIX, run `back-end/.venv/bin/python front-end/tests/backend_server.py --catalog`.

2. Start Next.js in terminal 2:

   ```powershell
   cd front-end
   $env:API_PROXY_TARGET = 'http://127.0.0.1:8011'
   npm run dev
   ```

   Wait for the ready message on `http://127.0.0.1:3000`. Set the proxy target
   before starting Next.js.

3. Open `http://127.0.0.1:3000/login` and sign in as the synthetic `student`
   account. The disposable backend seeds the demo password; refer to
   `seed_demo.py` rather than copying it into notes or screenshots.

## Rehearsal path

1. Choose **Backend Engineering** in the catalog and select **Backend and Web
   Foundations**. The competency contains **Client-Server Model** (rules quiz)
   and **HTTP Messages and Semantics** (mock AI evidence assessment).
2. Open the diagnostic and review its questions, then open the roadmap.
   Diagnostic scores measure a starting point and do not award XP or prove
   assessment eligibility.
3. Open a Client-Server Model lesson. Review its source link on the publisher's
   site, answer the checkpoint, and mark the lesson complete. Completion reports
   learning activity; it is not assessment evidence. Repeating a completion
   must not add XP again.
4. Open each skill assessment. Complete the Client-Server Model rules quiz and
   submit substantive HTTP debugging evidence for HTTP Messages and Semantics.
   The demo label and draft curriculum status remain visible in results. Do not
   describe either as a final credential.
5. Open the competency's credential eligibility page. Confirm both skills are
   present, create one draft demo, and follow its public verification link.
   Log out and return to the public verification URL. The public record must
   say it is not a final verified credential and must not claim confirmed
   blockchain proof. A draft is invalid for final credential verification.

## Shutdown and reset

Stop each server with `Ctrl+C`. Stopping the backend discards its in-memory
database. Start it again with `--catalog` for a clean account and empty
progress; assessment evidence and the draft must be prepared again through the
UI. Stop Next.js before changing `API_PROXY_TARGET`.

## Test evidence boundaries

Node tests exercise client helpers and contracts. Django tests and the API
probe exercise backend behavior. Neither proves browser rendering, navigation,
or user interaction. Browser-run evidence is recorded separately in
`docs/demo-test-matrix.md`; source-link status and licensing are separate claims
recorded in `docs/source-review.md`. A link checker does not verify reuse rights.

The local mock setup does not validate an external credential provider. Live
provider behavior and final issuance require separate authorized review.
