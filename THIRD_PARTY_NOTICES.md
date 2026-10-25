# Attribution and publication permissions

This document records provenance; it does not grant rights to third-party material.
The owner has not yet selected a licence for original project code.

## Architecture and software

- ResNet: Kaiming He, Xiangyu Zhang, Shaoqing Ren and Jian Sun,
  [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385).
  Implementation and pretrained-weight APIs come from
  [PyTorch/torchvision](https://github.com/pytorch/vision), distributed under its
  BSD-style licence. Architecture ownership and external pretraining are not claims
  of this project's original work. The provenance/terms of individual weight
  artifacts must be reviewed separately from the library licence.
- React, Vite, Radix UI, Tailwind and other frontend dependencies retain their own
  package licences and notices. Their versions are recorded in the npm lockfile.
- The AutoML TFLite model is an existing Google AutoML/course export. The original
  cloud job, training membership and permission to redistribute the export remain
  unverified. Optional Vertex API support is retained but does not imply cloud access.
- The GC10 head was trained locally using the existing NEU-trained backbone as a
  frozen feature extractor. It is not presented as an independently authored
  backbone architecture or end-to-end GC10 training.

## Data and assets

NEU and GC10 belong to their original providers; see [sources](data/SOURCES.md).
Dataset images and generated checkpoints are ignored. Publication of release
weights is pending owner approval and verified redistribution provenance; the
registry deliberately contains no invented release URLs.

Model binaries were untracked without deleting their local copies. Historical
model files and existing tracked frontend demonstration photographs predate this
cleanup. Their redistribution rights have not been established here. The weights
have not been removed from disk or Git history, and no history rewrite was made.
Before any public release, the owner must approve how to handle those existing
tracked artifacts and confirm or replace the demonstration assets' licences.
