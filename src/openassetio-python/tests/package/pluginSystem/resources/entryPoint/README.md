# Entry Point discovery test plugin

The Python plugin system (`openassetio.pluginSystem.PythonPluginSystem`)
allows manager plugins to be discovered through exposed package entry
points.

One way `importlib` does this by checking `.dist-info` suffixed
directories adjacent to any package on `sys.path`. This is somewhat
convenient as it allows us to provide the required directory structure
on disk as a test fixture without needing to invoke `pip` (which despite
being a python module, does not seem provide a python API).

This directory contains the source (`src`), and a working deployment
(`site-packages`), that can be appended to `sys.path` to facilitate the
testing of entry-point based plugin discovery.

> Note:
> The package provides an OpenAssetIO `ManagerPlugin` with the same
> identifier as the peer in `../pathB/packagedPlugin` to facilitate
> discovery precedence logic testing.

## Use in tests

Extend `sys.path`:

```python
sys.path.append('/path/to/entryPoint/site-packages')
```

##  Making changes

Update the package code in `src`, then, from this directory:

```bash
python -m pip install ./src -t ./site-packages
```

The `dist-info` dir will contain an additional `direct_url.json` file
(which is mandated for path-based/local installs). This is not required,
for our uses and leaks information about your local dev environment so
should be removed.

```bash
rm ./site-packages/packaged_plugin-0.0.0.dist-info/direct_url.json
```

You can now commit these changes (both to `src` and `site-packages` as
normal.
