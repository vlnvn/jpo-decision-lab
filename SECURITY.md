# Security boundary

The current server is intended for one trusted local machine (`127.0.0.1:8000`). It is **not** ready for Internet-facing use. No authentication, role permissions, CSRF defense, access control, secure multiuser storage, or durable audit protections exist.

Never store personally identifiable data, private surveillance footage, identifiable license plates, or secrets in the public repository or in sample data. The API accepts aggregated counts only. SQLite `data/*.sqlite3*` is excluded by `.gitignore`; exported JSON is portable and may contain user-entered observations, so review it before sharing.

Do not start the server with `--host 0.0.0.0` on a shared or public network. Production work must add authentication and authorization, protected database storage and backups, abuse limits, input size bounds, audit immutability, and a camera privacy review. External map tiles/Leaflet load from the network and must be governed by service terms, browser security policy, and supply-chain review.

For responsible vulnerability reports, create a private communication channel with the maintainer instead of publishing exploit details in a public issue.