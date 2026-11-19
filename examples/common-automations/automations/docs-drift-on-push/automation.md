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
documentation still matches the changed code. If it doesn't, open a
documentation pull request. If it matches, do nothing.
