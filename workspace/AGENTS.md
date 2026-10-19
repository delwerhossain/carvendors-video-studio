# Videos workspace (for any AI agent: Claude Code with Claude or GLM, Codex, opencode, ...)

Read these before any video work, in this order, and follow them:
1. `VIDEO_TEAM_CONTEXT.md` (this folder): tools, when to use local Whisper vs ElevenLabs, themes, workflows,
   setup, hard rules, QA.
2. `CARVENDORS_CONTEXT.md` (this folder): business facts.
3. `~/.claude/skills/video-studio/SKILL.md` (the rulebook), then for the chosen theme:
   - CarVendors story ads → `~/.claude/skills/video-studio/kit/frame.md` + `kit/playbook.md`
   - B&F TikTok re-edit series → `~/.claude/skills/video-studio/glass/series-brief-bnf.md` + `glass/README.md`
     (start from `glass/example-v001/index.html`).
Never open or print `~/.config/video-studio/*.env`. Each video is its own folder made with
`~/.claude/skills/video-studio/scripts/new_project.sh`.
