# WhatsApp Scripts

**Context:** India has 500M+ WhatsApp users. Construction PMs live on WhatsApp.

## QR Code Campaign

**Poster text for construction sites:**
```
┌─────────────────────────────────┐
│  ASK YOUR PROJECT A QUESTION    │
│                                 │
│  [QR CODE]                      │
│                                 │
│  Scan → Type "concrete strength"│
│  → Get answer in 10 seconds     │
│                                 │
│  Powered by Medha               │
└─────────────────────────────────┘
```

## Auto-Reply Flow

**User scans QR → WhatsApp opens:**
```
Welcome to Medha Document Intelligence.

Reply with your project code to get started:
• Type DEMO for a sample project
• Type your project code if registered

Try asking:
"What is the concrete strength?"
"Show me fire protection specs"
"Draft an RFI about HVAC ductwork"
```

## Broadcast Message (Existing Customers)

```
📋 *Project Update: [Project Name]*

Medha found 3 potential contradictions in this week's document updates:

1. Structural spec vs. drawing note (Section C-12)
2. Fire protection spacing vs. architectural plan
3. HVAC gauge vs. mechanical spec

Tap to review: [link]

Questions? Reply here.
```

## India-Specific Notes
- WhatsApp Business API required for automation
- Hinglish (Hindi + English) messaging preferred for field workers
- Voice message support for workers who prefer speaking
- Payment via UPI link in chat for monthly subscriptions
