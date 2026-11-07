# Daemonarium

Daemonarium is a static, browser-run single page game served by Nginx. Its game systems are implemented in plain JavaScript, and the field journal saves to the browser's local storage.

From the repository root, start the public Nginx service and the game container:

```sh
docker compose up --build web
```

The game is served through the existing `web` service on port 80, so open [http://localhost](http://localhost) or your configured domain. To stop the site, run `docker compose stop web daemonarium` from the repository root.

The container serves the client only; each browser keeps its own save. Clearing browser storage or choosing **Begin a new journal** in the Satchel erases that save.

## Creature Generator

The Creature Generator is part of the single-page app and is available from the left navigation. It calls same-origin `/generator-api/` routes; Nginx forwards only the supported generation endpoints and supplies Cloudflare Access headers from the daemonarium container environment. This path avoids the repository's existing `/api/` routing to the Pokémon API.

For a fresh checkout, copy `website/.env.example` to `website/.env` and set `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET`. Keep `website/.env` out of Git. The Compose service passes it to Nginx at runtime, while `website/.dockerignore` prevents it from entering the image build context.

Rebuild and restart the website service after changing the Nginx configuration:

```sh
docker compose up --build -d daemonarium
```
