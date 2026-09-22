# Publishing Releases

The PyPI package name remains `breeze-widget`. Releases are published from
`Taron686/breeze-widget-public` using GitHub Actions and PyPI Trusted Publishing.

## One-time PyPI Setup

In the existing project's **Publishing** settings, add a GitHub publisher:

| Field | Value |
| --- | --- |
| Owner | `Taron686` |
| Repository | `breeze-widget-public` |
| Workflow filename | `publish.yml` |
| Environment | `pypi` |

No long-lived PyPI API token is required.

## Release Steps

1. Update the version in `pyproject.toml` and commit the release changes.
2. Push the commit to this repository.
3. Publish a GitHub release for the matching version tag, or manually run
   **Upload Python Package to PyPI** from the Actions tab. Use one trigger per
   version; PyPI does not allow replacing previously uploaded files.
4. The workflow runs the test suite on Windows, builds the source distribution
   and wheel, checks their metadata, and uploads them to the existing PyPI
   project.
5. Verify the published version, README image, and project links on PyPI.

The README image is stored in `docs/breezewidget.png` and uses an absolute public
URL so it can also be displayed on PyPI.
