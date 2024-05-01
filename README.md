## Rules support for HDPS naming conventions

HDPS naming rules are documented in the [core-wiki](https://github.com/hdps/core/wiki/Branch-naming-rules).

The build system needs to be able to extract the version, and any core dependency version from the currently checked-out branch.

In addition one or tw checks are performed:

1. Check that the corresponding version of the core is available in the [LKEB artifactory](https://lkeb-artifactory.lumc.nl).
2. If possible check that the artifactory version is newer than the last commit on the core branch in question ('stale' core check). This ensures that the binary version has been build more recently.

### Manual installing

To manually install this python package (e.g. for local conan testing)

```
pip install -v git+http://github.com/hdps/rulessupport.git@master
```


__Note:__ The latter check (the 'stale' core check) can only be performed if the build has access to the hdps Organizational access credentials. This is only available to private projects.
