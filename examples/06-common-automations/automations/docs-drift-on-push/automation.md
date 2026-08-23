---
triggers:
  - provider: github
    event: push
    filter:
      repos: [acme/api-service]
      branches: [main]
      paths: ["api/**"]
---
A push to the default branch changed files under `api/`. Check whether the
documentation still matches the changed code. If it drifted, open a docs
PR; if it matches, do nothing.
