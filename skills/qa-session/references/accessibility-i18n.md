# Accessibility, compatibility and i18n session pack

Use when a charter's quality attribute is `interaction-capability` or `compatibility`: accessibility, browser, OS and device support, localization and text handling.

## Authority: fail closed

The following are local checks:
- rendering a page from a local build;
- running accessibility rules or a headless browser against it;
- exercising text and locale APIs in-process.

Each of these needs its own approval:
- signing in with a live account;
- testing a deployed site you do not own;
- installing browsers or assistive technology;
- recruiting or recording people.

Without approval, record the attempt as `inconclusive` and stop.

## Population and scope

Name:
- the conformance target, such as WCAG 2.2 AA, or the stated support baseline;
- the pages or components, states and full journeys in scope;
- the populations and input modes considered, such as keyboard only, screen reader, zoom or reflow, touch, reduced motion, RTL script or an IME.

Anything outside it stays unevaluated.

## Environment

Record:
- browser and engine versions, OS and device, viewport and zoom;
- any assistive technology, its version and settings;
- locale, script and time zone;
- the rule engine and its version.

A result holds only for the stack it ran on.

## Oracle

- **Accessibility:**
  - the criterion or rule identifier;
  - the expected name, role, state, focus order or announcement;
  - for a journey, task completion by the named input mode.
- **Compatibility:** the same observable behavior across the baseline matrix.
- **i18n:** results from the platform's locale data, with test text that includes:
  - long expansion and mixed RTL/LTR text;
  - combining marks, emoji and zero-width characters;
  - plural forms, locale-sensitive dates and numbers, and DST edges.

A scanner's score is not an oracle.

## Uncertainty

Automated rules cover only part of any criterion. Keep `cantTell`, `untested` and `unsupported` outcomes as `inconclusive`; never coerce them to pass. A page sample does not support a whole-product claim. No session substitutes for testing with disabled users; say so in the report.

## Stop conditions

Stop on any of these:
- an authorization boundary;
- a stack unavailable without installing something;
- a required login;
- target drift;
- the charter budget.

## Evidence

Keep:
- the exact commands and rule configuration;
- the stack record;
- raw rule output and accessibility-tree or DOM snapshots;
- screenshots at each zoom or locale tried;
- keyboard and focus transcripts;
- the matrix cells run and not run.
