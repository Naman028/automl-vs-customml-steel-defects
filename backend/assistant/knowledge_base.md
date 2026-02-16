# Industrial Defect Assistant Knowledge Base

## Defect overview
This assistant explains steel surface defects and provides QA guidance.
It does not replace human inspection.

## Crazing (Cr)
Fine, shallow cracks on the surface caused by thermal stress or rapid cooling.
Often appears as a network of thin lines.

## Inclusion (In)
Non-metallic particles or impurities trapped in the metal during processing.
Often seen as darker or irregular spots.

## Patches (Pa)
Local surface imperfections that look like irregular patches or areas of uneven finish.
Can be caused by roll wear or inconsistent cooling.

## Pitted Surface (PS)
Small holes or pits on the surface due to corrosion or trapped gas.
Often appears as tiny, scattered depressions.

## Rolled-in Scale (RS)
Oxide scale pressed into the surface during rolling.
Often appears as elongated dark marks aligned with rolling direction.

## Scratches (Sc)
Linear marks caused by mechanical contact or debris during processing.
Often appear as straight or slightly curved lines.

## Interpreting predictions
Predictions are based on image quality, lighting, and training data.
Use top-k results to see close alternatives.
Low confidence or small differences between classes should be treated as uncertain.

## Metal types (general)
Steel is an iron-carbon alloy; alloys can change appearance and defect patterns.
Aluminum and copper surfaces have different reflectivity and textures, which can affect model performance.

## Limitations
The model may confuse visually similar defects (e.g., scratches vs rolled-in scale).
Domain shift (different camera, lighting, or material) can reduce accuracy.

## Q/A guidance
If a user asks "why this defect?", explain top-k alternatives and confidence.
If a user asks "how to fix", provide prevention or inspection tips, not guarantees.
If a user asks "what is X", use the defect overview sections.
If a question is outside scope, say you do not know and suggest expert review.

## Example questions
Q: Why did it predict scratches instead of inclusion?
A: Compare top-k results, note visual similarity, and mention lighting or focus issues.

Q: What does rolled-in scale look like?
A: Elongated dark marks aligned with the rolling direction.

Q: How to reduce false positives?
A: Improve lighting consistency, clean the surface, and use sharper images.

Q: Which defect is most severe?
A: Severity depends on product use and inspection policy, not just defect name.
