# Medha Social Media Playbook
**Objective:** Build reach and authority for Medha in construction tech / VDC / AI circles  
**Primary Platform:** LinkedIn  
**Secondary Platforms:** Twitter/X, YouTube (long-term)  
**Positioning:** Researcher-builder, not salesperson  
**Voice:** Curious, evidence-based, slightly irreverent about industry inefficiencies

---

## 1. Platform Strategy

### LinkedIn (Primary)
**Why:** Construction decision-makers, VDC coordinators, PMs, and investors are all on LinkedIn. Organic reach is still viable for founder stories and industry commentary.

**Best posting times (Dubai/GCC audience):**
- Tuesday–Thursday, 7:30–9:00 AM GST
- Sunday 7:30–9:00 AM GST (first workday in GCC)
- Avoid Friday (weekend in GCC)

**Post length:** 1,200–1,500 characters (LinkedIn cuts off after ~140 lines, but longer posts get more dwell time)

**Format mix:**
- 40% founder/research narrative posts
- 30% proof-of-work posts (screenshots, benchmarks, demo videos)
- 20% industry commentary / contrarian takes
- 10% personal behind-the-scenes

### Twitter/X (Secondary)
**Why:** AI researchers, VCs, and tech-forward construction people are here. Good for thread-style technical deep dives.

**Format:**
- Short single tweets for hot takes
- 5–10 tweet threads for technical explanations
- Quote-tweet construction industry news with your angle

### YouTube / Short-form (Future)
**Why:** "Day in the life of a VDC coordinator" and "AI reads construction drawings" content performs well.

**Start with:** 60-second screen recordings of Medha finding a contradiction in a document set.

---

## 2. Audience Targeting

### Tier 1: Direct Users (post for them)
- VDC coordinators / BIM managers
- Construction project managers
- Document controllers
- MEP coordinators

### Tier 2: Buyers (post near them)
- Construction directors
- VDC agency founders
- Digital transformation leads at general contractors

### Tier 3: Amplifiers (post to be shared by them)
- ConTech investors
- AI researchers working on domain-specific models
- IIT Madras alumni network
- Dubai/GCC construction community leaders

---

## 3. Content Pillars

### Pillar 1: The Problem is Real
Stories about how document errors cause rework, RFIs, and delays.

**Post angles:**
- "The $859K RFI problem"
- "Why VDC coordinators work 10-hour days"
- "The 'right version' problem in construction"

### Pillar 2: Proof of Work
Show the system actually working.

**Post angles:**
- Screenshot of Medha finding a contradiction
- Benchmark results (36 seconds for 17 chunks)
- Test report snippets
- Demo video of query → answer with citations

### Pillar 3: Research-Backed Authority
Connect Medha to cutting-edge research.

**Post angles:**
- "What is MeMo (Memory as a Model)?"
- "Why parametric memory beats RAG for construction"
- "Cognitive systems in construction AI"
- "Dubai DM compliance and AI"

### Pillar 4: Industry Commentary
Contrarian or insightful takes on construction tech.

**Post angles:**
- "We don't need another construction platform"
- "Why 'GitHub for construction' hasn't worked"
- "The real reason construction AI fails"
- "Addenda are design debt"

### Pillar 5: Builder's Journey
Personal posts about building Medha.

**Post angles:**
- "What I learned testing on real Army Corps specs"
- "From IIT Madras to construction AI"
- "The 25% contradiction detection problem"
- "Why I'm obsessed with construction documents"

---

## 4. 10 Ready-to-Post Templates

### Template 1: The Problem Hook
```
The most expensive mistakes in construction don't happen on site.

They happen in a PDF nobody read carefully enough.

A spec says 2-hour fire-rated duct.
A drawing shows 1-hour.
A subcontractor builds to the drawing.
An inspector fails it.
An RFI goes out.
3 weeks and $40K later, the duct is redone.

This is the document coordination problem. And it's why I've been building Medha — an intelligence layer that reads across your construction documents and catches contradictions before they reach site.

Not another platform. Not another login. Just the teammate who actually reads the drawings.

#Construction #VDC #BIM #ConTech #DocumentIntelligence
```

### Template 2: Proof of Work
```
We just ran Medha on real construction documents:

✅ Kentucky Division 23 HVAC standards
✅ UMD Division 23 HVAC specs  
✅ US Army Corps project specifications

Result: 463 reflection QA pairs extracted, 6 cross-document relationships surfaced automatically.

The pipeline found converging requirements across procurement, general conditions, and technical specs — the kind of cross-referencing that normally takes a VDC coordinator hours.

Still early. Still hard. But the thesis is holding.

If you work with construction documents, what's the one cross-reference check that eats your time?

#ConstructionAI #VDC #BIM #MeMo #DocumentManagement
```

### Template 3: Research Deep-Dive
```
Most construction AI tools use RAG: retrieve relevant chunks, then answer.

The problem? Retrieval breaks under noise. Add 50 documents, 8 versions, 3 addenda, and RAG starts hallucinating or missing things.

That's why Medha uses MeMo — Memory as a Model.

Instead of searching documents every time, we train a dedicated model on your project documents so the knowledge lives inside the model itself.

The result:
- No retrieval latency
- Corpus-size-independent performance
- Real cross-document reasoning

It's based on arXiv:2605.15156 by Quek et al. We adapted it for construction.

If you're building domain-specific AI, stop fighting retrieval. Start training memory.

#AI #MachineLearning #ConstructionTech #MeMo #RAG
```

### Template 4: Contrarian Take
```
"We need a GitHub for construction."

No, we don't.

We need construction tools to stop pretending they're the only source of truth.

Revit has the model.
Procore has the RFIs.
Bluebeam has the redlines.
Email has the change orders.
ACC has the latest drawings.

The problem isn't that we lack a central platform. The problem is that no one reads across them.

Medha doesn't replace your platforms. It reads them. All of them.

Because the person who actually understands the full picture shouldn't be a VDC coordinator with 12 tabs open at 7 PM.

#ConTech #VDC #BIM #ConstructionSoftware #DigitalTransformation
```

### Template 5: Personal Journey
```
Three years ago I watched a construction project fall behind because of a document error.

Not a design error. Not a construction error.
A document error.

Two specs contradicted each other. Nobody caught it. The MEP contractor built one version. The fire inspector wanted another. The delay cost 6 weeks.

I was still in school, but I couldn't stop thinking about it.

Why are the smartest people in construction still acting as human search engines?

That's the question behind Medha. We're not there yet. But after testing on real Army Corps specs and university standards, I finally believe the answer is possible.

If you're fighting this problem daily, I want to learn from you.

#Construction #IITMadras #StartupJourney #VDC #BIM
```

### Template 6: Benchmark/Technical
```
Speed update on the MeMo pipeline:

Sequential: ~11 minutes for 30 chunks
Parallel (20 workers): 35 seconds
Async (50 workers): 58 seconds

Plot twist: more workers isn't always better. We hit OpenAI's server-side limits at 50 workers. The sweet spot is 20.

For Phase 2 (Dubai corpus, 50-100 docs), we're moving to OpenAI's Batch API — 50% cheaper, no rate limits, overnight processing.

The real bottleneck isn't our code. It's model inference time. The fix for production: local vLLM on a GPU.

#MLOps #AI #ConstructionAI #Optimization #vLLM
```

### Template 7: Dubai/GCC Regional
```
Dubai builds faster than almost anywhere on earth.

But the document problem is the same everywhere:
- 8 versions of the same drawing
- Specs that contradict addenda
- RFIs that take weeks to answer
- Subcontractors building from outdated PDFs

I'm building Medha to help VDC teams and construction PMs in Dubai/GCC catch document conflicts before they become site problems.

The system is being validated against real construction specs. Next: Dubai DM Building Regulations.

If you're working on construction projects in Dubai, Abu Dhabi, or Riyadh, I'd love to hear about your document workflow. What's your biggest coordination headache?

#DubaiConstruction #GCCConstruction #VDC #BIM #DubaiDM
```

### Template 8: Ask for Help
```
I need help from construction people.

I'm validating Medha's contradiction detection on real construction document sets. The catch: I need documents from the SAME project, multiple disciplines (architectural, structural, MEP, fire protection).

University standards from different states don't produce real contradictions — they don't reference the same project elements.

If you have access to (or can point me toward) publicly available construction bid sets, addenda, or project manuals, please comment or DM.

Will credit contributors in the research report.

#Construction #OpenData #Research #VDC #BIM
```

### Template 9: Behind the Scenes
```
The unglamorous part of building AI for construction:

Yesterday I spent 4 hours trying to download real construction PDFs.

University sites block automated downloads.
Government portals require registrations.
Plan rooms charge $200 per set.
Some "PDFs" are just HTML Cloudflare blocks.

Meanwhile, the actual technical work — running the MeMo pipeline, finding cross-document relationships, validating contradictions — took 40 minutes.

Data acquisition is the real bottleneck in construction AI.

#AI #Data #ConstructionTech #StartupLife #Research
```

### Template 10: Vision Post
```
In 5 years, every VDC coordinator will have an AI teammate.

Not a chatbot. A teammate that:
- Reads every spec, drawing, RFI, and addendum
- Remembers version history
- Catches contradictions in seconds
- Drafts RFIs with proper citations
- Knows when to escalate to a human

The VDC coordinator doesn't get replaced. They get promoted to design optimization, team mentoring, and strategic coordination.

That's the future Medha is building toward. One contradiction at a time.

#FutureOfWork #Construction #AI #VDC #BIM
```

---

## 5. Hashtag Strategy

### Primary Hashtags (use on every post)
```
#Construction #VDC #BIM #ConTech #AI #DocumentIntelligence
```

### Secondary Hashtags (rotate based on content)
```
#DubaiConstruction #GCCConstruction #DubaiDM
#MLOps #RAG #MeMo #MachineLearning
#Startup #IITMadras #FounderJourney
#ProjectManagement #ConstructionManagement
#DigitalTransformation #AEC
```

### Niche Hashtags (for targeted reach)
```
#Navisworks #Revit #Procore #AutodeskConstructionCloud #Bluebeam
#FireProtection #MEP #StructuralEngineering #Architecture
```

**Rule:** 5-8 hashtags per post. Mix broad + niche. Put them at the end (not first comment — that myth is dead).

---

## 6. Engagement Playbook

### The First 60 Minutes
LinkedIn's algorithm heavily weights early engagement.

1. **Post at 7:30 AM GST** and stay online for 60 minutes
2. **Reply to every comment within 15 minutes** with a question or insight, not just "thanks"
3. **Share the post to your story** immediately after posting
4. **Send to 3-5 close connections** who will engage quickly
5. **Comment on 5 relevant posts** in the hour before/after your post to be "active"

### Comment Reply Templates

**When someone says "interesting":**
```
Thanks [Name]. What's your experience — do you see this problem more on the design side or the construction side?
```

**When someone asks for a demo:**
```
Happy to show you. DM me your worst document coordination story and I'll run it through the system.
```

**When someone is skeptical:**
```
Fair skepticism — that's why we're validating on real docs, not marketing claims. What would convince you?
```

**When someone shares their pain point:**
```
This is exactly why we're building this. Mind if I DM you to dig deeper?
```

### DM Strategy
Don't pitch in the first message. Use the 3-message approach:

1. **Message 1:** "Saw your comment about [specific pain point]. I'm researching this for Medha — mind if I ask one question?"
2. **Message 2:** Ask the question, actually listen
3. **Message 3:** "We're building exactly for this. Would you be open to a 15-minute call to see if our prototype fits your workflow?"

---

## 7. 14-Day Content Calendar

### Week 1: Establish Authority
| Day | Post | Pillar |
|-----|------|--------|
| Tue | Template 1: Problem Hook | Problem |
| Wed | Template 5: Personal Journey | Journey |
| Thu | Template 3: Research Deep-Dive | Research |

### Week 2: Show Proof
| Day | Post | Pillar |
|-----|------|--------|
| Sun | Template 2: Proof of Work | Proof |
| Tue | Template 4: Contrarian Take | Commentary |
| Wed | Template 6: Benchmark/Technical | Proof |
| Thu | Template 7: Dubai/GCC Regional | Regional |

### Week 3: Build Community
| Day | Post | Pillar |
|-----|------|--------|
| Sun | Template 8: Ask for Help | Community |
| Tue | Template 9: Behind the Scenes | Journey |
| Wed | Share someone else's ConTech post + add insight | Commentary |
| Thu | Template 10: Vision Post | Vision |

### Week 4: Convert Attention
| Day | Post | Pillar |
|-----|------|--------|
| Sun | Poll: "What's your biggest document pain point?" | Engagement |
| Tue | Carousel: "5 contradictions that cost projects millions" | Problem |
| Wed | Demo video: 60 seconds | Proof |
| Thu | Template 8 variant: Call for beta testers | Conversion |

---

## 8. Content Formats That Work

### LinkedIn Carousels
- "5 document errors that cause rework"
- "How MeMo works in 5 slides"
- "RAG vs Memory for construction AI"

### Screen Recordings
- 60 seconds: Upload docs → Ask question → Get cited answer
- 90 seconds: Finding a contradiction across two specs

### Polls
- "What's your biggest document pain point?"
  - Finding the right version
  - Cross-referencing specs and drawings
  - Catching contradictions
  - Drafting RFIs

### Single-Image Posts
- Screenshot of contradiction detection result
- Benchmark chart (sequential vs parallel vs async)
- Architecture diagram (7 systems)

---

## 9. Metrics to Track

### Weekly
- **Profile views** (LinkedIn shows this)
- **Post impressions**
- **Engagement rate** (likes + comments + shares / impressions)
- **Comments per post** (more valuable than likes)
- **Connection requests from target audience**

### Monthly
- **DM conversations** with potential users
- **Demo calls booked**
- **Beta tester signups**
- **Email list growth** (if you add a newsletter CTA)
- **Website/landing page clicks**

### Targets (Month 1)
- 3 posts per week
- 5,000+ impressions per post
- 3%+ engagement rate
- 10+ meaningful DM conversations
- 3+ demo calls

---

## 10. Quick Wins for Immediate Reach

### Today
1. Update LinkedIn headline to: "Building Medha | AI for construction document intelligence | IIT Madras '25 | Researcher"
2. Update LinkedIn featured section with Medha landing page
3. Connect with 20 construction/VDC professionals in Dubai/GCC

### This Week
1. Post Template 1 (Problem Hook)
2. Comment meaningfully on 10 posts from VDC/BIM influencers
3. Join 3 LinkedIn groups: "BIM/VDC Professionals," "Construction Technology," "Dubai Construction"

### This Month
1. Post 3x per week consistently
2. Get featured in one ConTech newsletter or podcast
3. Reach 1,000+ followers in construction/AI space

---

## 11. Influencers to Engage With

### Construction Tech
- James Benham (JBKnowledge)
- Sarah Buchner (Trunk Tools)
- Tooey Courtemanche (Procore)
- Salla Eckhardt (Microsoft / AEC)

### VDC/BIM
- Anyone posting about Navisworks/Revit workflows
- VDC coordinators at major GCs
- Dubai-based BIM consultants

### AI Research
- Andrej Karpathy (for technical credibility)
- Yann LeCun (for memory/MeMo discussions)
- Domain-specific AI builders

**Tactic:** Comment thoughtfully on their posts for 2 weeks before posting your own. Build recognition.

---

## 12. Call-to-Action Matrix

| Post Type | CTA |
|-----------|-----|
| Problem posts | "What's your experience?" |
| Proof posts | "What document check eats your time?" |
| Research posts | "What did I get wrong?" |
| Ask for help | "Comment or DM" |
| Demo posts | "DM me for a 15-minute walkthrough" |

**Never use:** "Buy now," "Sign up," "Book a call" in early posts.
**Always use:** Open-ended questions that invite stories.
