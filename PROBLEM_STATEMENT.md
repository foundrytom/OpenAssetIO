# Problem Statement

This document attempts to capture the problem(s) OpenAssetIO is
attempting to solve in the specific context of Visual FX work for
film and television.

We pick this specific area as it was the motivation for the project.
Though there is nothing specific to Media & Entertaining within the core
API, its design was certainly influenced by simplifying a transition
from the approaches currently used in production.

## Background

Within post-production (VFX, et. al), work is generally distributed to
several vendors by the studio or production company responsible for a
project.

Historically, each vendor has invested heavily in building a "pipeline"
the allows their numerous artists to work collaboratively. This
generally involves integrating the software they use with some central
source of truth that manages the associated data.

This pipeline has often been the "secret sauce" for these vendors. As a
result, despite serving a common need, the specifics of its
implementation generally vary significantly between vendors.

In recent years, there has been a shift towards the adoption of common
data standards and open-source frameworks/tooling, but the business
logic of most pipelines still remains proprietary.

The rest of this document assumes a familiarity with this environment,
the workings of such pipelines and the challenges faced by their
maintainers when dealing with production at scale.

## Path-based referencing

> It is common for media creation tools to reference this managed data
> by its present location in a file system.

What do we mean by this? Lets look at a typing Compositing setup for
some augmentative VFX work for a feature film.

Compositing software is generally structured around a graph of nodes,
each of which performs a specific function. Every graph generally begins
with some node that loads source images. We shall refer to this as a
"read node".

Off-the-shelf compositing software generally supports loading source
images from files on the host machines file system (which may include
network mounts). When an artists desires to load a specific image they
do this by entering the file system path to the image into a parameter
of the read node.

The software's programming understands how to retrieve the pixel data
from this file, and the artist can now continue to work with the image.

This approach has many drawbacks when working at scale in a production
environment. We shall look at a few of these problems in more detail
below.

### Browsing

### Version management

### Correctly interpretation of data

### Creating new data in the correct place

### Accessing data across co-located sites

### Moving documents between platforms

### Performant access to data

### Handling non-file-based data

## Assets as a second-class citizen

### Ensuring the correct results

### Avoiding duplicate integration code

### Patching over application UI

### Avoiding stale data
