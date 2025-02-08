# Hugo Content Validator

A Python-based project designed to **validate content files in a Hugo site**, ensuring your Markdown files have valid image references, shortcodes, and internal page links. This project includes a custom GitHub Action to automate the validation process on every push or pull request. More details in this [blog post](https://sedward5.com/iba-cocktail-challenge). 

## Features

- **Image Validation:**  
  Ensures that:
  - `featured_image` and `recipe.image` specified in the front matter exist in the same content bundle.
  - Relative image links in Markdown are present in the repository.
  
- **Shortcode Validation:**  
  Checks that all shortcodes used in Markdown files have corresponding `.html` files in the `layouts/shortcodes/` directory.

- **Internal Link Validation:**  
  Detects internal hyperlinks (e.g., `[Post 2](/post-2/)`) and verifies that the referenced content bundle (`/content/post-2/index.md`) exists.

- **Verbose Output (Optional):**  
  Prints detailed validation results, including checked images, shortcodes, and internal links.

---

## Installation

### Prerequisites

- Python 3.7 or higher  
- `pyyaml` library (install it with `pip install pyyaml`)

---

## Usage

### **1. Manual Script Execution**

To run the validation script locally, execute:

```bash
    python scripts/validate_hugo_content.py --base-path . --verbose
```

**Options:**  
- `--base-path`: The root directory of your Hugo site (default: current directory).  
- `--verbose`: Enables detailed output.

---

### **2. GitHub Action Integration**

The GitHub Action defined in `.github/workflows/validate-content.yml` will automatically validate content on pushes and pull requests.

To enable it, follow these steps:

1. Place the `validate_hugo_content.py` script in `scripts/`.  
2. Ensure the workflow file is located at `.github/workflows/validate-content.yml`.  
3. Commit and push your changes.

#### Example Workflow Configuration

```yaml
    name: Validate Hugo Content

    on:
      push:
        branches:
          - main
      pull_request:

    jobs:
      validate:
        runs-on: ubuntu-latest
        steps:
          - name: Check out code
            uses: actions/checkout@v3

          - name: Set up Python
            uses: actions/setup-python@v4
            with:
              python-version: '3.9'

          - name: Install dependencies
            run: pip install pyyaml

          - name: Validate Hugo content
            run: python scripts/validate_hugo_content.py --verbose
```

---

## Output Examples

### **Sample Errors**

```
    Missing relative image '/post-1/featured-image.webp' in content/post-1/index.md
    Missing shortcode 'nonexistent-shortcode' in content/post-2/index.md
    Missing internal bundle '/post-3/' referenced in content/post-4/index.md
```

---

## Contributing

Feel free to submit issues or pull requests to improve this tool.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
