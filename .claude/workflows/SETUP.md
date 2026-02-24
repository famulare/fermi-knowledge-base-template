# Workflow: First-Use Setup

**Trigger:** First session, or `bin/validate-configure` reports unset tokens

---

## Purpose

Guide new users through initial configuration of their Fermi Knowledge Base instance.

---

## Process Steps

### Step 1: Welcome

Display:
```
Welcome to your Fermi Knowledge Base!

This is a durable knowledge capture system powered by an AI knowledge partner.
I'll help you configure it for your use.

This setup will:
1. Set your name (for origin attribution)
2. Optionally customize the persona name
3. Set your communication preferences
4. Validate the configuration
5. Create your first commit
```

### Step 2: User Name (REQUIRED)

Ask: "What name should I use for origin attribution? This appears in origin labels like 'Origin: [YourName]' and in commit messages."

Update:
- `config/system.yml` → `user.name`
- `context/knowledge_partner_profile.md` → replace `<!-- CONFIGURE:user_name -->`

### Step 3: Persona Name (Optional)

Ask: "Your knowledge partner is named 'Fermi' by default. Would you like to keep this name or choose a different one?"

If custom name:
- Update `config/system.yml` → `persona.name`
- Note: FERMI.md and CLAUDE.md references remain as "Fermi" in templates; the persona name is used in conversation

### Step 4: Communication Style (Optional)

Ask: "How should your knowledge partner communicate? The default is: 'Precision over politeness, depth over warmth, direct challenge welcome.' Would you like to adjust this?"

Options:
1. Keep default (precision, directness)
2. More collaborative (still rigorous but warmer)
3. Academic (formal, citation-heavy)
4. Custom (describe your preference)

Update `context/knowledge_partner_profile.md` → communication_style section

### Step 5: Review Configuration

Display all settings for confirmation:
```
Configuration Summary:
- User name: [name]
- Persona name: [Fermi or custom]
- Communication style: [style]
- Timezone: [timezone]

Everything look correct?
```

### Step 6: Validate

Run: `bin/validate-configure`

If validation passes: Continue
If validation fails: Show what needs fixing

### Step 7: Initial Commit

Stage all configuration changes and commit:
```
git add -A
git commit -m "Initial KB configuration

Configured knowledge base for [UserName].
Persona: [PersonaName]

Co-Authored-By: Claude ‹model› <noreply@anthropic.com>"
```

### Step 8: Next Steps

Display:
```
Your knowledge base is ready!

Try these to get started:
- "Ingest this note: [paste some text]" — capture knowledge
- "What do we know about [topic]?" — query the KB
- Look at examples/ for sample entries from a working instance
- Run /goodbye-kb at the end of each session to checkpoint

For detailed workflows, check .claude/workflows/README.md
```

---

## Post-Setup

After setup:
- FERMI.md session init should detect setup is complete (no [CONFIGURE] in system.yml)
- Normal operating modes activate
- User can re-run setup anytime by saying "Let's run the SETUP workflow"
