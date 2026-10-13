# Daemonarium

Daemonarium is a static, browser-run single page game served by Nginx. Its game systems are implemented in plain JavaScript, and the field journal saves to the browser's local storage.

From the repository root, start the public Nginx service and the game container:

```sh
docker compose up --build web
```

The game is served through the existing `web` service on port 80, so open [http://localhost](http://localhost) or your configured domain. To stop the site, run `docker compose stop web daemonarium` from the repository root.

The container serves the client only; each browser keeps its own save. Clearing browser storage or choosing **Begin a new journal** in the Satchel erases that save.
