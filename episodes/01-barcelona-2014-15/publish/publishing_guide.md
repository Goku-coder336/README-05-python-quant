# How to publish Episode 1

Everything you need is in this folder (`publish/`) and the episode folder above it. Do it in this
order: video first, then the blog post that embeds it, then share the links.

| what | file |
|---|---|
| Edit guide | `../capcut_guide.md` |
| Title, description, chapters | `../youtube.md` |
| Thumbnail (1280x720, ready to upload) | `thumbnail.png` |
| Blog post | `blog_post.md` |
| Blog images | `blog-images/` (6 PNGs, numbered in the order they appear in the post) |

## Part 1: YouTube

### One-off setup (first episode only)

1. Go to youtube.com, sign in, click your profile picture, then **Create a channel**. A name like
   "Run of the Champions" works.
2. In **YouTube Studio** (studio.youtube.com), open **Settings > Channel > Feature eligibility** and
   verify your phone number. This unlocks custom thumbnails and videos over 15 minutes.
3. Create a playlist called **Run of the Champions** (Studio > Content > Playlists > New playlist).

### Upload the episode

1. Studio > **Create > Upload videos**, and pick your CapCut export.
2. **Details**
   - Title: copy from `youtube.md`.
   - Description: copy the block between the lines in `youtube.md`. Update the chapter times to your
     final edit first.
   - Thumbnail: upload `thumbnail.png`.
   - Playlist: Run of the Champions.
   - Audience: **No, it's not made for kids**.
   - **Show more**: language English; category Sports. Tags are optional (for example: Champions League,
     Barcelona, Messi, Neymar, Suárez, Luis Enrique, 2015 final).
   - **Altered or synthetic content**: YouTube asks whether the video contains realistic altered or
     synthetic content. Read the examples it shows. Clearly animated charts and a narrator voice that
     does not imitate a real person usually do not need the label; if you are unsure, tick Yes. It does
     no harm.
3. **Video elements**: add an **End screen** (last 5 to 20 seconds, over the "Next: 2015/16" card) with
   a Subscribe button and your latest video or the playlist.
4. **Checks**: wait for the copyright check to finish. Everything in the video is your own work, so it
   should come back clear.
5. **Visibility**: choose **Public** now, or **Schedule** a time. Weekend evenings in the UK suit
   football content.
6. After publishing, open the video and check the chapters appear on the progress bar. If they do not,
   one chapter time is wrong (the first must be 0:00, each at least 10 seconds).

## Part 2: the blog

### Which platform

**Recommended: Substack** (substack.com). It is free, needs no code, gives you a web page *and* an email
list, and turns a pasted YouTube link into a video player. Readers can subscribe for every new episode,
which suits a series.

Other options if you prefer:
- **Medium**: easy, has built-in readers, but many articles sit behind its paywall.
- **WordPress.com** or **Blogger**: more control over the look, slightly more setup.
- **Your own site later**: I can build one (for example on GitHub Pages) once there are a few episodes.

### Set up Substack (first time)

1. Go to substack.com, **Start writing**, and sign up with your email.
2. Publication name: "Run of the Champions". Short description: "Every Champions League winner's full
   run, from the group stage to the final, told through the data."
3. Skip importing contacts and paid subscriptions for now (you can add them later).

### Publish the post

1. Click **New post**. Copy the title and the italic line under it from `blog_post.md`.
2. Paste the body section by section. Where the post says **[VIDEO: ...]**, paste your YouTube link on
   its own line: Substack turns it into a player.
3. Where it says **[IMAGE: blog-images/...]**, delete that line and insert the matching PNG from
   `blog-images/` (the + button, then Image). Paste the italic line under it as the caption.
4. The `##` lines are headings: select the text and choose **Heading** in the toolbar. The `**bold**`
   bits become bold.
5. Check the source links at the bottom still work, then **Continue > Publish** (or schedule it for an
   hour after the video).

Tip: open `blog_post.md` on GitHub (or any Markdown viewer) to see it formatted, and copy from there.
Formatting then pastes across cleanly.

## Part 3: share it

- Post the YouTube link where football fans talk data: football subreddits such as r/soccer and r/Barca,
  football forums, and X/Twitter or Threads with the thumbnail.
- Put the blog link in the YouTube description (add a line at the end: "Written version: <link>"), and
  the YouTube link at the top of the blog. Each sends readers to the other.
- Check the rules of each community before posting: some ban self-promotion or only allow it on set
  days.

## Every new episode after this

Same order: edit in CapCut with that episode's guide, upload with its `youtube.md`, publish its blog
post, share. I will make the files for each episode in the same layout.
