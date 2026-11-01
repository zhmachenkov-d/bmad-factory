# Security Policy

## Supported Versions

At this time, security fixes are provided for the **latest release** of
bmad-factory. Older versions are not actively supported, but critical issues
may be addressed on a best-effort basis if they affect current users.

| Version        | Supported          |
|----------------|--------------------|
| Latest release | :white_check_mark: |
| Older releases | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues,
discussions, or pull requests.**

Instead, use one of the following private channels:

1. **GitHub Private Vulnerability Reporting (preferred).**
   Go to the **Security** tab of this repository and click
   **Report a vulnerability**. This opens a private advisory visible only to
   you and the maintainer.
   Direct link: https://github.com/zhmachenkov-d/bmad-factory/security/advisories/new

2. **Email.**
   If you prefer not to use GitHub, send a message to
   **[zhmach@gmail.com](mailto:zhmach@gmail.com)**.

> **Note:** bmad-factory is currently maintained by a single person. I review
> every report personally, but I cannot guarantee a fixed response time.
> I will acknowledge your report as soon as I am able.

## What to Include in Your Report

To help me assess and fix the issue efficiently, please include:

- A description of the vulnerability and its potential impact.
- The affected file(s), path(s), or component(s).
- Step-by-step instructions to reproduce the issue.
- A proof of concept or exploit code, if available.
- Any suggested fix or mitigation, if you have one.
- Your preferred name/handle for credit (or let me know if you prefer to stay
  anonymous).

## Disclosure Policy

I follow **coordinated disclosure**. My goal is to:

1. Acknowledge your report as soon as possible.
2. Investigate and confirm the issue.
3. Develop and test a fix.
4. Publish a patched release and a security advisory.
5. Credit you in the advisory (unless you prefer otherwise).

Please give me a reasonable amount of time to address the issue before
disclosing it publicly. In return, I will keep you informed about the progress
and will not share your report with third parties without your consent.

## Security Updates

Security advisories will be published on the **Security** tab of this
repository. To stay informed, you can:

- Watch this repository and enable notifications for **Security alerts**.
- Check the **Security advisories** section periodically.

## Scope

This policy applies to the code and configuration shipped in the
`bmad-factory` repository. It does not cover vulnerabilities in third-party
dependencies; please report those to the respective upstream projects.

## Attribution

This security policy was inspired by common open-source templates and
guidance from [opensource.guide](https://opensource.guide/).
