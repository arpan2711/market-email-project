# Deployment plan - Streamlit Community Cloud

Not deployed yet. This is a checklist to make that a 10-minute job
instead of a research project when I'm ready to do it. Streamlit
Community Cloud is the natural fit - `chatbot_app.py` is a plain
Streamlit app, the free tier is enough for a personal project, and it
deploys straight from this GitHub repo with no Dockerfile or server
to manage.

## Prerequisites

- [ ] Repo pushed to GitHub and accessible to Streamlit Cloud: `https://github.com/<GITHUB_USERNAME>/<REPO_NAME>`
- [ ] Streamlit Community Cloud account, signed in with GitHub: https://share.streamlit.io
- [ ] A DeepSeek API key: https://platform.deepseek.com/api_keys - `<YOUR_DEEPSEEK_API_KEY>`

## Steps

1. Push the branch you want deployed (`main` recommended) to GitHub - already done.
2. Go to https://share.streamlit.io -> **New app**.
3. Fill in:
   - Repository: `<GITHUB_USERNAME>/<REPO_NAME>`
   - Branch: `main`
   - Main file path: `chatbot_app.py`
   - App URL (optional custom subdomain): `<APP_NAME>.streamlit.app`
4. Under **Advanced settings -> Secrets**, paste:
   ```toml
   DEEPSEEK_API_KEY = "<YOUR_DEEPSEEK_API_KEY>"
   ```
   (This is the hosted equivalent of the local `.env` file - `load_dotenv()`
   in `chatbot_app.py` is a no-op on Streamlit Cloud, but `os.environ`
   still gets `DEEPSEEK_API_KEY` from the secrets store, so nothing else
   needs to change.)
5. Deploy. First build installs everything in `requirements.txt` and
   takes a couple of minutes; later pushes to the tracked branch
   redeploy automatically.
6. Smoke test once it's live: ask a question with the seed data loaded
   (see below) and confirm an answer with a `Sources:` line comes back.

## Loading demo data on the hosted app

`seed_demo_data.py` is a local CLI script, not something Streamlit
Cloud runs for you. Options, easiest first:

- Paste a few articles and holdings by hand through the sidebar once
  the app is live.
- Or add a one-time "Load demo data" button in `chatbot_app.py` that
  calls `seed_demo_data.seed()` - not built yet, placeholder for later
  if a populated demo instance is worth keeping.

## Known limitation: storage is not persistent

`RagStore` writes to `data/rag_documents.json` on local disk
(`rag_store.py`). Streamlit Cloud's filesystem is ephemeral - it
resets on every redeploy and after the app sleeps from inactivity. For
local use this is fine (that's the whole point of the JSON file), but
a hosted instance will silently lose everything you saved.

Not fixing this now since it means swapping `RagStore`'s storage layer
for something external. If it's worth doing later:

- [ ] Pick a persistence target: `<PERSISTENT_STORAGE_CHOICE>`
      (e.g. a hosted Postgres/SQLite instance, or Streamlit Cloud's
      built-in secrets-backed connection to something like Supabase)
- [ ] Point `RagStore._load`/`_save` at it instead of the local JSON file
- [ ] Add the connection string/credentials to the Secrets block above

## Rollback

Streamlit Cloud redeploys on every push to the tracked branch, so a
bad deploy is a `git revert` + push away. To go back further, use the
app's **Manage app -> Reboot app** option, or point the deployed
branch at an older commit temporarily.

## Custom domain (optional, not needed to get this live)

- Streamlit Cloud gives you `<APP_NAME>.streamlit.app` for free.
- For a fully custom domain, front the app with a reverse proxy (e.g.
  Cloudflare) pointed at the `.streamlit.app` URL - `<CUSTOM_DOMAIN>`.

## If this outgrows Streamlit Cloud's free tier

Options if this ever needs more than Streamlit Cloud gives for free
(always-on, more memory, real persistent storage): Render, Railway, or
Fly.io, all of which can run this from a `Dockerfile` that doesn't
exist yet. Placeholder, not needed for the current scope:

- [ ] `Dockerfile` (base image, `pip install -r requirements.txt`, `streamlit run chatbot_app.py --server.port $PORT --server.address 0.0.0.0`)
- [ ] Host/service: `<RENDER_OR_FLY_OR_RAILWAY_SERVICE_URL>`
- [ ] Env var: `DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>`
- [ ] Persistent volume mounted at `/app/data` so `rag_documents.json` survives restarts
