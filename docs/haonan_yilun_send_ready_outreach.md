# Haonan/Yilun Send-Ready Outreach

Not evidence: `true`.
Current decision: `STRONG_REVISE`.
Readiness: `17/21` requirements satisfied; `4` blocking external-evidence gaps.
First-email word count: `189`.

Purpose: keep the actual first contact crisp, honest, and aligned with the strengthened Paper 119 package. This document is the send-ready layer; the longer outreach package remains the private reasoning layer.

## Send Rule

- Lead with Paper 119 as a skill-seam world/action model for behavior composition.
- Mention CoStream as the primary fit anchor in the first email.
- Mention no secondary paper in the first email. If a later technical reply needs one, use exactly one of OAT or SIMPACT.
- Send the one-page memo and four-page preview first.
- Keep the External evidence closure brief and operator packet as follow-up artifacts only.
- Do not pitch Haonan as responsible for supplying the missing proof.
- Do not mention Yilun as the outreach motive.

## First Email

```text
Subject: Seam certification for compositional robot behaviors

Hi Haonan,

I'm Jason Wang, an independent researcher working on adaptive physical world/action models for robot behavior composition.

I have a submission-shaped project on local skill-seam certification: before chaining two skills, the model predicts whether the next skill's basin can take over, whether a small repair/probe is enough, or whether the transition should be rejected. The strongest local evidence is on hard handoff regimes where naive sequencing looks feasible but fails through basin mismatch, high-energy barriers, or contact-mode discontinuity.

I thought of CoStream because it makes behavior composition the right object of study. My project is complementary: not another behavior module, but a seam critic for deciding when composed behaviors should be accepted, repaired, probed, or abstained from.

The current package is honest about its boundary: it has a clean local draft and validation protocol, but still needs independent real or accepted high-fidelity validation. I would value your advice on whether this seam-certification layer is scientifically useful to test in a behavior-composition stack.

Would you be open to a short chat?

Best,
Jason
```

## Follow-Up

```text
Subject: Re: Seam certification for compositional robot behaviors

Hi Haonan,

Just a brief follow-up. I made a one-page memo and a four-page technical preview for the seam-certification idea. The core question is whether a behavior-composition stack benefits from a separate handoff critic that can accept, repair, probe, or reject seams before execution.

No worries if now is not a good time. I would still appreciate any quick pointer on whether this direction seems useful or misguided.

Best,
Jason
```

## If He Responds Positively

```text
Thanks, that would be great.

The cleanest next step from my side is to send the one-page memo and four-page preview, then ask one falsification question: which behavior-composition setting would be the cleanest test for a seam critic? I can own implementation, analysis, writing, and ablations around the seam layer. I would not want to treat you as responsible for supplying the missing proof; the current validation packet is there so the proof burden is explicit and independently checkable.
```

## Attachment Sequence

### first_email

Send:
- `outreach/paper119_one_page_memo.pdf`
- `outreach/paper119_four_page_preview.pdf`

Do not send:
- full generated PDF as the only artifact
- operator-release bundle
- long validation artifact catalog
- many Haonan/Yilun paper references

### after_interest

Send:
- `docs/external_evidence_closure_brief.md`
- `results/external_operator_packet.md`
- `external_validation/operator_release_bundle_README.md`

Do not send:
- raw logs or videos before real evidence exists
- any claim that strict external evidence has passed

## Guardrails

- The ask is whether the seam critic is worth testing, not whether Haonan will provide the validation layer.
- The claim is a bounded local mechanism claim until independent real or accepted high-fidelity evidence exists.
- The agenda identity is adaptive physical world/action models for embodied agents; contact-rich manipulation is a testbed only.
- The outreach success criterion is a scientifically useful falsification path, not access theater.

## Machine-Checked Constraints

- `primary_first_email_anchor`: CoStream
- `secondary_first_email_anchor`: none
- `max_first_email_words`: 190
- `haonan_role`: fit/falsification advice and possible collaboration, not supplier of the missing proof
- `yilun_route`: only discuss Yilun if Haonan engages on the scientific fit; do not mention access as a motive
- `current_status_line`: 17/21 readiness, 4 blocking external-evidence gaps, STRONG_REVISE
