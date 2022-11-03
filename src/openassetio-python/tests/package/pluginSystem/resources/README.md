# Plugin System Test Resources

This directory contains resources for the plugin system tests.

## pathA, pathB, pathC, symlinkPath, entryPoint

These sub-directories contain minimal implementations of two
`PluginSystemPlugins`:

- `PackagePlugin` : A plugin implemented in a python package.
- `ModulePlugin` A plugin implemented in a single-file python module.

`PackagePlugin` is available via `pathB`, and
`entryPoint/site-packages`. `ModulePlugin` is installed in `pathA`
and `pathC`.

`symlinkPath` exposes `pathA` and `pathB` plugins via symlinks.

These permutations allow path precedence and traversal behaviors
to be properly tested.
