# LLM Compliance Test Suite – Figma Design Spec

## Color Palette
- **Primary:** #1A237E (deep blue)
- **Accent:** #1976D2 (blue), #43A047 (green), #E53935 (red)
- **Background:** #E3F2FD (light blue), #F5F5F5 (neutral)
- **Text:** #212121 (dark), #757575 (secondary)

## Typography
- **Headings:** Roboto Slab, 24–32px, bold
- **Body:** Roboto, 16px, regular
- **Buttons:** Roboto, 16px, medium

## Icons
- Scales of justice (header)
- Shield/checkmark (health)
- Pencil (edit), Trash (delete), Play (run), Info (details)

## Layout & Components

### Header
- Left: App logo (scales of justice) + "LLM Compliance Test Suite"
- Right: Health indicator (● Backend: Online/Offline)

### Navigation Bar
- Tabs: Dashboard | Use Cases | Results | Docs/Help

### Dashboard
- Quick actions: [Run New Test] [Add Use Case] [View Results]
- Use Case Table:
  - Columns: Title | Description | Updated | Actions (Edit/Delete/Run)
- Add/Edit Use Case Modal:
  - Fields: Title, Description, Input Prompt, Expected Output, Tags
- Run Test Modal:
  - Select Use Case (dropdown), Parameter overrides, Submit
- Results Table:
  - Use Case | Status | Time | Result | Actions (View/Download)
- Result Details Modal:
  - Input, Output, Verdict, Logs, Download

### Docs/Help
- How to use, compliance criteria, troubleshooting

---

## Example Wireframe

```
+-------------------------------------------------------------+
| LLM Compliance Test Suite        [Backend: ● Online]        |
+-------------------------------------------------------------+
| Dashboard | Use Cases | Results | Docs/Help                 |
+-------------------------------------------------------------+
| [Run New Test] [Add Use Case] [View Results]               |
+-------------------------------------------------------------+
| Use Cases (Table)                                          |
| ---------------------------------------------------------  |
| | Title | Description | Updated | Actions (Edit/Delete) |  |
| ---------------------------------------------------------  |
| ...                                                       |
+-------------------------------------------------------------+
| [Add/Edit Use Case Modal]                                  |
+-------------------------------------------------------------+
| [Run Test Modal: Select Use Case, Params, Submit]          |
+-------------------------------------------------------------+
| Results (Table)                                            |
| ---------------------------------------------------------  |
| | Use Case | Status | Time | Result | Actions           |  |
| ---------------------------------------------------------  |
| ...                                                       |
+-------------------------------------------------------------+
| [Result Details Modal: Input, Output, Verdict, Logs]        |
+-------------------------------------------------------------+
```

---

## SVG Mockup
- See `frontend-mockup.svg` in the project root. You can import this SVG into Figma or export it as PNG for presentations.

---

## Usage
- Use this spec to create a Figma file with the described layout, colors, and components.
- The SVG mockup provides a visual starting point for the main dashboard screen. 