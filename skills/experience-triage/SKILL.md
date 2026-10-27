---
name: experience-triage
description: "Use when a user correction or experience mention shows up and it must be routed into the library (rule / experience / lesson / wiki / skill)."
version: 1.0.0
author: The-BlueCrow
license: MIT
tags: [triage, rules, experience, retrospective, knowledge]
    related_skills: [retrospective-lesson, minnow-token-efficiency]
---

# Triage：把一次纠错分流到正确的库

## When to Use

When the user corrects you, points out a fact, drops a tip, or states a preference — anything that should survive this session. Route it before it evaporates.

The moment you notice something worth keeping, ask: **where should this live?** Not everything belongs in the same place, and putting it in the wrong store is worse than not recording it, because a buried rule never fires.

## The stores

| Store | What goes there |
|---|---|
| `<SKILLS_DIR>/<skill>/SKILL.md` | Operational rules: "next time you do X, follow these steps." Written as imperative sentences. |
| `~/experience/` | Domain knowledge and accumulated facts, organized by topic. |
| `<MEMORY_DIR>/lessons-learned.md` | Causal lessons: "this failed because Y." Mechanism-level, with self-check lines. |
| `~/wiki/` | Structured reference pages: entities, concepts, comparisons, sources. |
| `<SKILLS_DIR>/` (new skill) | A whole workflow that recurs and needs its own trigger + steps. |

Every record carries these fields, no matter which store it lands in:
- **name**: the skill's `name`, the lesson's number, or a short slug
- **description**: one line, written as a trigger ("Use when...")
- **content**: the actual rule / experience / lesson
- **file_path**: where it lives

## First time: write it in

If the experience has never been recorded:

1. Read the target store's `README.md` before writing anything — follow its append conventions exactly.
2. If it belongs in an existing topic file (e.g. an experience file on that subject), append it there rather than creating a new file. A new topic file is fine only when nothing existing covers the subject.
3. Write the record with all four fields. The description should let a future you recognize the trigger.

## Second time: formalize it

If the same experience has already been recorded informally and now proves its worth:

1. Look for the informal record — it might be in a wiki page, a chat log, or a scratch file.
2. Formalize it into the proper store: write the full record with all fields, including the trigger description.
3. Leave a pointer at the original location pointing to the formal record, so the informal note doesn't diverge.
4. If it's an operational rule that will load with a skill, write it into that skill's SKILL.md — that's where it actually fires. A lesson alone doesn't trigger; a rule in a skill does.

## Lesson format

For lessons in `<MEMORY_DIR>/lessons-learned.md`, follow the format in `references/lesson-formats.md`. The key structure: phenomenon → root cause (mechanism level, not "I forgot") → fix (executable, with commands) → self-check line. A lesson without a self-check line is just a log entry.

## Pitfalls

- **Don't let a good experience evaporate.** The single most common failure is: the user teaches you something, you apply it for the rest of the session, and it's gone next time. Triage the moment you notice it.
- **Don't put an operational rule in a lesson.** Lessons don't load with skills. If it's "next time do X," it belongs in a SKILL.md. If it's "this environment has quirk Y," it belongs in lessons.
- **Don't invent.** If you can't find the original experience file after a real search, ask the user rather than fabricating content that "was probably there."
- **Don't bury a new file in a subdirectory.** Top-level files get indexed; nested ones don't, and get silently orphaned.
- **When to ask**: after creating or updating a file, offer to formalize — "I found something interesting, want me to turn it into a rule?" Asking is cheap; an unrecorded lesson costs the same mistake twice.
- **Semantic dedup across stores**: the same insight written in both a lesson and a skill is a maintenance trap — pick the layer that fires (skill for "how next time", lesson for "why it broke", wiki for "how the thing works"), and cross-reference by pointer instead of copying paragraphs.
- **If a source is unfamiliar** (a platform, name, or term you don't recognize in a stored record), don't silently re-answer from your own memory — the stored record represents a deliberate judgment. Say the record exists, note your uncertainty, and ask before overwriting.
- **Tone discipline when relaying stored records**: relay facts and rules as-is; keep your own voice out of it. A stored "do X" stays "do X" — not "you might consider trying X sometime."
- **Don't treat "sent / delivered / done" as a real state.** If you handed a task to another agent, that agent's self-report is not evidence — verify the artifact on disk yourself before telling the user it's handled.
- **Don't answer from raw memory when a source of truth exists.** If a document, log, or record on disk describes the topic, read it first — memory of a tool's behavior drifts; the file doesn't.
- **先斩后奏式推销要警惕**：把「要不要我帮你配置 X？」和「已经帮你配好 X 了」合并成一句的推销（未经确认就动手）不是建议，是越权——该问的要真问。
