---
name: web-design-guidelines
description: Review UI code for Web Interface Guidelines compliance. Use when asked to "review my UI", "check accessibility", "audit design", "review UX", or "check my site against best practices".
metadata:
  author: vercel
  version: "1.0.0"
  argument-hint: <file-or-pattern>
---

# Web Interface Guidelines

Review files for compliance with Web Interface Guidelines.

## How It Works

1. Read `guidelines.md` in this skill's folder
2. Read the specified files (or prompt user for files/pattern)
3. Check against all rules in the guidelines
4. Output findings in the terse `file:line` format

## Guidelines Source

Read `.claude/skills/web-design-guidelines/guidelines.md` (copy of vercel-labs/web-interface-guidelines@434b7f91364665f2f733b310ec54809bf8f37937, command.md, MIT, see LICENSE). Never fetch rules from the internet. If a rule conflicts with CLAUDE.md, CLAUDE.md wins.

## Nemi notes (from the security review, 25 Oct 2026)

- Client texts are German: ignore the Title Case rule, the “ ” quotes rule and "avoid first person" for German copy (use „ “ quotes).
- For guest forms, `autocomplete` with `name`/`email`/`tel` applies; ignore the conflicting `autocomplete="off"` rule.
- New versions of the guidelines go through `bezbednost` first.

## Usage

When a user provides a file or pattern argument:
1. Read the guidelines from the local file above
2. Read the specified files
3. Apply all rules from the guidelines
4. Output findings using the format specified in the guidelines

If no files specified, ask the user which files to review.

Source: vercel-labs/agent-skills@063bee94c3f4df8453406c830b0a7df0f2860278 (skills/web-design-guidelines/SKILL.md), adapted to read the rules locally.
