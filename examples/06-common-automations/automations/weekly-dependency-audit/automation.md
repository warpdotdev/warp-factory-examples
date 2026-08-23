---
triggers:
  - provider: schedule
    event: cron_fired
    schedule:
      name: weekly-dependency-audit
      cron: "0 9 * * 1"
---
Run the weekly dependency audit. List outdated and vulnerable dependencies,
apply safe minor and patch upgrades on a branch, run the tests, and open a
PR with the changes and a summary of anything that needs a human decision.
