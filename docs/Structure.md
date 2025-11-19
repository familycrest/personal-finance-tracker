# Project File Structure

The project's structure is as follows:

```
personal_finance_tracker/   - The root directory. `manage.py` and repository files sit here
    apps/                   - Where our apps sit. Refer to docs/Sitemap.md
        accounts/
        finances/
    base/                   - Handles `/`, `/dashboard/`, `/api/`, and redirects to the apps
    docs/                   - Our general documentation
        test_docs/          - Documentation for testing operations
        use_case_sequences/ - Use case diagrams
    static/                 - Static JS, CSS, and media assets
    templates/              - Templates that are shared between many different parts of the project
    tests/                  - Tests and associated fixtures/assets
```

Please ensure any changes you make adhere with this structure. Double-check before you commit.

Git will usually give you a sign when a commit is in conflict with the structure, as it will say that you've created/removed way more new files than you remember/expected. Now is a good time to check if you've copied or deleted something by accident.
-
