# Attribution and publication permissions

This document records provenance; it does not grant rights to third-party material.
Original project code is licensed under [MIT](../LICENSE), copyright Naman Patel.
Datasets, pretrained components, and third-party libraries keep their own licences;
the project MIT licence does not relicense those components.

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
- Naman Patel trained the AutoML Vision model on Google Cloud (Vertex AI AutoML)
  for a course project, as confirmed by the owner. Optional Vertex API support
  remains available; local TFLite is the default. The original cloud-job metadata
  is unavailable, so this provenance statement does not establish training membership.
- The GC10 head was trained locally using the existing NEU-trained backbone as a
  frozen feature extractor. It is not presented as an independently authored
  backbone architecture or end-to-end GC10 training.

## Data and assets

NEU and GC10 belong to their original providers; see [sources](../data/SOURCES.md).
Dataset images and generated checkpoints stay outside the source tree. The owner
has requested a versioned release of the custom NEU checkpoint, GC10 classifier
head, and owner-trained AutoML export. Release hashes and URLs are recorded in the
model registry. Publishing remains gated on the owner's release confirmation.

The reference photographs have been removed from the current tree because their
redistribution rights are unclear. Labelled placeholders are used instead.
Historical copies of those photos, model binaries and old demo credentials are
scheduled for removal using a fresh mirror clone and `git filter-repo`, subject
to separate owner approval. Current-tree removal does not itself remove history.
