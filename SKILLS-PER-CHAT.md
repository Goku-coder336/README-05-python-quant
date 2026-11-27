# Skills per chat

One block per chat. Open that chat and paste its block as a message. Each chat installs only what it needs, inside its own project, and commits it, so every later chat on that project already has them.

All commands were tested on 27 Nov 2026. Skill names after `-s` are separated by spaces.

---

## 1. Cartoon reels (French word-song reels, this repo)

```
Install these skills for this project, then commit and push them:

npx skills add heygen-com/hyperframes -s hyperframes hyperframes-cli hyperframes-registry media-use -a claude-code -y --copy
npx skills add Jakeschincariol/youtube-agent-skill -s yt-package yt-seo yt-script yt-shorts yt-viral yt-comment yt-retention yt-edit yt-plan yt-audit -a claude-code -y --copy
npx skills add cloveric/claude-drawing-skill -s 'claude绘图' --rename claude-drawing -a claude-code -y --copy -g

What each is for:
- hyperframes: builds and renders the reels (HTML and animation to MP4)
- hyperframes-cli: check, snapshot and render commands
- hyperframes-registry: ready-made transitions, titles and captions
- media-use: music, sound effects, voice and captions for a video
- yt-package / yt-seo: title, thumbnail, description and tags
- yt-script / yt-shorts: hooks, on-screen text and loop points
- yt-viral: what is working in the niche right now
- yt-comment: pinned comment and replies
- yt-retention / yt-edit: where viewers leave, and what to cut
- yt-plan / yt-audit: weekly upload plan and channel review
- claude-drawing: hand-drawn cartoon pictures made with code (installed with -g because the demo scripts look for it in ~/.claude/skills)
```

## 2. Run of the Champions (football analysis episodes)

```
Install these skills and plugins for this project, then commit and push the skills:

npx skills add heygen-com/hyperframes -s hyperframes hyperframes-cli hyperframes-registry media-use -a claude-code -y --copy
npx skills add Jakeschincariol/youtube-agent-skill -s yt-script yt-package yt-seo yt-chapters yt-shorts yt-retention yt-plan -a claude-code -y --copy
claude plugin marketplace add lemomo-ai/lemo-opuscar && claude plugin install lemo-opuscar@lemolab
claude plugin marketplace add bangtutorial/bang-motion && claude plugin install bang-motion@bang-motion

What each is for:
- hyperframes, hyperframes-cli, hyperframes-registry, media-use: animated stat graphics, leaderboards, maps and clips
- yt-script: scripts with scored hooks for long videos
- yt-package / yt-seo: title, thumbnail, description, tags
- yt-chapters: chapters for 6 to 8 minute videos
- yt-shorts: cut Shorts out of each long episode
- yt-retention / yt-plan: where viewers leave; upload plan
- lemo-opuscar (plugin): full video pipeline with its own styles
- bang-motion (plugin): motion-design techniques
```

## 3. Malayalam faceless shorts

```
Install these skills for this project, then commit and push them:

npx skills add heygen-com/hyperframes -s hyperframes hyperframes-cli media-use -a claude-code -y --copy
npx skills add Jakeschincariol/youtube-agent-skill -s yt-script yt-shorts yt-package yt-seo yt-viral yt-comment -a claude-code -y --copy

What each is for:
- hyperframes, hyperframes-cli: build and render clips and text cards
- media-use: voiceover, music, captions and sound effects
- yt-script / yt-shorts: hooks and Short scripts
- yt-package / yt-seo: title, thumbnail, description, tags
- yt-viral: what is working in the niche
- yt-comment: replies and the pinned comment
```

## 4. Scottish and Spanish ladies animation (Kling anime reel)

```
Install these skills for this project, then commit and push them:

npx skills add heygen-com/hyperframes -s hyperframes media-use -a claude-code -y --copy
npx skills add alchaincyf/huashu-art-motion -s huashu-art-motion -a claude-code -y --copy
npx skills add Jakeschincariol/youtube-agent-skill -s yt-shorts yt-package yt-seo yt-viral -a claude-code -y --copy

What each is for:
- hyperframes: titles, captions and editing on top of the Kling clips
- media-use: music, sound effects and voice
- huashu-art-motion: art-style animation recipes and recreating a reference animation
- yt-shorts / yt-package / yt-seo / yt-viral: hook, title, description and niche research
(Kling itself is a connector, not a skill: keep it connected.)
```

## 5. Utsella marketplace (web app)

```
Install these skills for this project, then commit and push them:

npx skills add addyosmani/agent-skills -s spec-driven-development planning-and-task-breakdown incremental-implementation frontend-ui-engineering api-and-interface-design test-driven-development debugging-and-error-recovery code-review-and-quality security-and-hardening shipping-and-launch -a claude-code -y --copy
npx skills add vercel-labs/agent-skills -s web-design-guidelines vercel-react-best-practices deploy-to-vercel -a claude-code -y --copy
claude plugin marketplace add DietrichGebert/ponytail && claude plugin install ponytail@ponytail

What each is for:
- spec-driven-development / planning-and-task-breakdown: write the spec, split it into tasks
- incremental-implementation: build in small, tested steps
- frontend-ui-engineering: pages and components that look professional and work on phones
- api-and-interface-design: clean backend APIs
- test-driven-development / debugging-and-error-recovery: tests first; find the real cause of bugs
- code-review-and-quality: review before merging
- security-and-hardening: logins, payments and user data done safely
- shipping-and-launch: pre-launch checklist
- web-design-guidelines: accessibility and UI review
- vercel-react-best-practices / deploy-to-vercel: only if the app is React/Next.js on Vercel (skip otherwise)
- ponytail (plugin): smallest working code, fewer tokens
```

## 6. EventKompany platform analysis (research and planning)

```
Install these skills for this project, then commit and push them:

npx skills add addyosmani/agent-skills -s idea-refine interview-me spec-driven-development documentation-and-adrs -a claude-code -y --copy

What each is for:
- idea-refine: turn a rough idea into a sharp concept
- interview-me: questions that pin down what you actually want
- spec-driven-development: write the requirements before building
- documentation-and-adrs: record decisions and why they were made
(If this becomes a build, add the Utsella list.)
```

## 7. Triad Verdict trading system (Python)

```
Install these skills for this project, then commit and push them:

npx skills add addyosmani/agent-skills -s test-driven-development debugging-and-error-recovery code-review-and-quality code-simplification performance-optimization doubt-driven-development -a claude-code -y --copy
claude plugin marketplace add DietrichGebert/ponytail && claude plugin install ponytail@ponytail

What each is for:
- test-driven-development: prove each rule works before trusting it
- debugging-and-error-recovery: find the real cause of wrong results
- code-review-and-quality / code-simplification: cleaner, safer code
- performance-optimization: faster backtests
- doubt-driven-development: a second check on decisions where money is at stake
- ponytail (plugin): smallest working code, fewer tokens
```

---

## Optional in any chat: check your usage

```
Install CodeBurn and show where my tokens go:

claude plugin marketplace add getagentseal/codeburn && claude plugin install codeburn@codeburn
npx -y codeburn overview
npx -y codeburn optimize
```
