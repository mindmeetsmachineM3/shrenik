# Auto-post setup (new GitHub repo, new Instagram page)
1. Instagram account must be Professional (Business/Creator). Create the token + IG_USER_ID the same way as for your other pages (Meta app, Instagram API with Instagram Login).
2. New repo, PUBLIC (free Actions minutes). Upload everything from the zip. Keep the folder structure: autopost.py + make.py + config.json next to the kit/ folder; workflow at .github/workflows/post.yml (repo root).
3. Settings > Secrets and variables > Actions > Secrets: IG_USER_ID, IG_ACCESS_TOKEN, CLOUDINARY_CLOUD_NAME, CLOUDINARY_UPLOAD_PRESET, GEMINI_API_KEY (optional: SARVAM_API_KEY, ELEVEN_API_KEY, ELEVEN_VOICE). Variables (optional): VOICE_RATE, VOICE_PITCH.
4. Edit config.json: handle, page_name.
5. Actions > Biz auto-post > Run workflow: (a) diagnose ticked; (b) force=reel + dry_run ticked, download the "output" artifact and watch/listen; (c) force=poster, dry_run unticked = first real post.
6. Then it runs by itself: every 20 min it checks, posts when one of today's 4 random slots is due.
