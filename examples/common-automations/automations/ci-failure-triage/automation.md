---
triggers:
  - provider: github
    event: workflow_run_completed
    filter:
      repos: [acme/api-service]
      branches: [main]
      conclusions: [failure]
---
A workflow run failed on the default branch. Read the run's logs and find
the failing step. If the cause is small and clear, open a pull request with a
fix. Otherwise, open an issue with the failing step, the error, the commit
range, and a link to the run.
