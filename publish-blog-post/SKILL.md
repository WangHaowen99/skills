---
name: publish-blog-post
description: Use when adding, uploading, publishing, editing, or troubleshooting Markdown articles for the WangHaowen99.github.io Hugo blog deployed on GitHub Pages, including content/posts files, front matter, local preview, Git commits, pushes, and GitHub Actions deployment.
---

# Publish Blog Post

## Overview

Use this workflow for the `WangHaowen99/WangHaowen99.github.io` Hugo static blog. Publish by committing Markdown source files to the repository; do not edit generated files in `public/` or the deployed website directly.

## Repository Check

Work in the existing repository when possible:

```bash
git rev-parse --show-toplevel
git remote -v
```

Confirm the remote points to `WangHaowen99/WangHaowen99.github.io`. If the repo is absent and the user wants actual publication, clone it first:

```bash
git clone https://github.com/WangHaowen99/WangHaowen99.github.io.git
cd WangHaowen99.github.io
```

Before editing, inspect the worktree:

```bash
git status --short --branch
```

Never overwrite unrelated user changes. Work with dirty files only when they are relevant.

## Choose The Content Path

Use these source locations:

- Main technical articles: `content/posts/YYYY/slug.md`
- Life notes: `content/life/slug.md`
- Project pages: `content/projects/slug.md`
- About page: `content/about.md`

Use lowercase English slugs with hyphens, such as `hugo-guide.md` or `ai-notes.md`. If the user gives only a Chinese title, choose a short descriptive English slug unless the user specifies one.

## Create Or Edit An Article

If Hugo is installed, prefer:

```bash
hugo new posts/2026/example-post.md
```

If Hugo is unavailable, create the Markdown file manually using this front matter:

```markdown
---
title: "文章标题"
date: 2026-06-24T10:00:00+08:00
draft: false
categories:
  - 技术
tags:
  - Hugo
series:
  - 建站笔记
description: "文章摘要"
toc: true
---

这里开始写正文。
```

Rules:

- Set `draft: false` for anything meant to publish.
- Use the current Asia/Shanghai date and time unless the user supplies a date.
- Keep `categories`, `tags`, and `series` as YAML lists.
- Use `toc: true` for long posts and `toc: false` for short notes.
- Put body content after the closing `---`.
- Keep Markdown headings structured from `##` downward inside the article body.

For images, place source assets under `static/images/YYYY/` and reference them as:

```markdown
![图片说明](/images/2026/example.png)
```

## Preview And Verify

Check Hugo first:

```bash
hugo version
```

The project expects Hugo Extended `0.161.1`. On Linux, install it with:

```bash
bash scripts/install-hugo.sh
```

Preview drafts and published posts locally:

```bash
hugo server -D
```

Build production output:

```bash
hugo --minify
```

When available, run the repository verification script:

```bash
bash scripts/verify-site.sh
```

If Hugo is not installed and the task is only drafting Markdown, complete the source edit and clearly report that local build verification was not run.

## Commit And Publish

Only commit relevant source files, usually `content/...` and any `static/images/...` assets. Use Conventional Commits:

```bash
git status --short
git add content/posts/2026/example-post.md
git commit -m "feat: add example post"
git push origin main
```

Pushing to `main` triggers GitHub Actions via `.github/workflows/hugo.yml`. The deployed URL for a post normally becomes:

```text
https://wanghaowen99.github.io/posts/YYYY/slug/
```

If `gh` is authenticated, check deployment status with:

```bash
gh run list --workflow hugo.yml --limit 3
```

Otherwise, tell the user to check the repository Actions tab.

## Safety Notes

- Do not print, commit, or store tokens, passwords, server credentials, or GitHub credentials.
- Do not edit `public/`; it is generated output.
- Do not push unless the user asked to upload, publish, or deploy, or explicitly approved the push.
- If content appears unfinished, ask before publishing; otherwise save as `draft: true` and do not push unless requested.
