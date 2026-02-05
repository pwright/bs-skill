Generate a blockscape map for the domain of [referenced file]
### Requirements

* Output valid JSON only with the structure below (no commentary):

  * Model level:
    * `id`: required string, short/sluggy (lowercase, hyphen/underscore ok)
    * `title`: required string, human-friendly model title
    * `abstract`: optional string (plain text or simple HTML) that explains the landscape
    * `categories`: array of category objects

  * Each category has:
    * `id` (short, lowercase, unique)
    * `title` (human-friendly)
    * `items`: array of component objects

      * each item has:
        * `id` (short, lowercase, unique across all categories)
        * `name` (human-friendly)
        * optional `logo` (e.g., "logos/[slug].svg")
        * optional `external` (string URL) pointing to external documentation or reference material for that item
        * optional `color` (hex string) for tile tint
        * optional `deps`: array of item `id`s this item depends on (when present, must reference defined items only)
        * optional `stage`: integer 1-4 for Wardley maps only (1=genesis, 2=custom, 3=product, 4=commodity/service). Include only when the user explicitly asks for a Wardley model/series.
* Use 3-6/7 categories and 2-6/7 items per category. Prefer clarity over exhaustiveness.
* Order categories roughly from abstract to concrete.
* Model visible user value via vertical position (things closer to the user are higher). Ensure `deps` reflect a flow from higher-value items to their underlying enablers.
* (Optional) You may imply horizontal evolution/maturity via category naming or item grouping. Only include the `stage` field when explicitly asked for a Wardley map/series.
* Keep all identifiers ASCII, hyphen-separated where needed.

### Domain Guidance

In one paragraph, summarize the domain's user-visible goals and the key enabling components. Use that understanding to choose categories and dependencies.

### Output

If the user asks for a 'series', create an array of json using the following criteria.

Return only the JSON matching this schema:

```
{
  "id": "[model-id]",
  "title": "[Model Title]",
  "abstract": "[Short description or HTML snippet, optional]",
  "categories": [
    {
      "id": "[category-id]",
      "title": "[Category Title]",
      "items": [
        { "id": "[item-id]", "name": "[Item Name]", "deps": ["[id]"] }
      ]
    }
  ]
}
```

### Validation Checklist (the model should self-check before returning):

* Top-level `id` and `title` are present and non-empty; if `abstract` is provided, it is non-empty.
* All provided `deps` reference existing item IDs.
* No duplicate `id`s across all items.
* 3-6/7 categories; each has 2-6/7 items.
* JSON parses.

---

## One-shot Example (Machine Learning Model Deployment)

Prompt to paste

Generate a Blockscape value-chain JSON for the domain of machine learning model deployment.

### Requirements

* Output valid JSON only with this structure (no commentary).
* Use 3 - 6/7 categories, 3-6/7 items each.
* Order from abstract (user-facing) to concrete (infrastructure).
* Vertical axis is visible user value; `deps` should point from user-visible items down to enablers they rely on.
* Optional `logo` paths may use placeholders like "logos/[slug].svg".

### Domain Guidance

Users need reliable predictions surfaced via APIs/UI, backed by versioned models, observability, and scalable infra. Security and governance span across.

### Output (JSON only)

```
{
  "categories": [
    {
      "id": "experience",
      "title": "User Experience",
      "items": [
        { "id": "prediction-api", "name": "Prediction API", "deps": ["model-serving", "authz"], "external": "https://example.com/api.html"},
        { "id": "batch-scoring", "name": "Batch Scoring", "deps": ["feature-store", "orchestration"] },
        { "id": "ui-console", "name": "Ops Console", "deps": ["monitoring", "logging"] }
      ]
    },
    {
      "id": "models",
      "title": "Models & Data",
      "items": [
        { "id": "model-serving", "name": "Model Serving", "deps": ["container-runtime", "autoscaling"] },
        { "id": "model-registry", "name": "Model Registry", "deps": ["artifact-store"] },
        { "id": "feature-store", "name": "Feature Store", "deps": ["data-pipelines"] }
      ]
    },
    {
      "id": "platform",
      "title": "Platform Services",
      "items": [
        { "id": "monitoring", "name": "Monitoring", "deps": ["metrics-backend"] },
        { "id": "logging", "name": "Logging", "deps": ["log-backend"] },
        { "id": "authz", "name": "AuthN/Z", "deps": ["secrets"] },
        { "id": "orchestration", "name": "Orchestration", "deps": ["container-runtime"] }
      ]
    },
    {
      "id": "infrastructure",
      "title": "Infrastructure",
      "items": [
        { "id": "autoscaling", "name": "Autoscaling", "deps": ["metrics-backend"] },
        { "id": "container-runtime", "name": "Container Runtime", "deps": [] },
        { "id": "artifact-store", "name": "Artifact Store", "deps": [] },
        { "id": "data-pipelines", "name": "Data Pipelines", "deps": [] },
        { "id": "metrics-backend", "name": "Metrics Backend", "deps": [] },
        { "id": "log-backend", "name": "Log Backend", "deps": [] },
        { "id": "secrets", "name": "Secrets Management", "deps": [] }
      ]
    }
  ]
}
```

---

## Tips

* Keep names user-friendly; keep ids short and consistent.
* If an item feels too broad, introduce a new category rather than bloating `deps`.
* If there's a link (external), use the favicon from the website as logo
* If you're unsure about `logo`, omit it; you can add paths later.

The following map shows color conventions:

```
{
  "id": "conventions",
  "title": "Color Conventions",
  "abstract": "Reference for color conventions.",
  "categories": [
    {
      "id": "color-conventions",
      "title": "Color conventions",
      "items": [
        {
          "id": "old",
          "name": "Old",
          "color": "#000000",
          "deps": []
        },
        {
          "id": "new",
          "name": "New",
          "color": "#FFFFFF",
          "deps": []
        },
        {
          "id": "important",
          "name": "Important",
          "deps": [],
          "color": "#FF0000"
        }
      ]
    }
  ]
}
```
