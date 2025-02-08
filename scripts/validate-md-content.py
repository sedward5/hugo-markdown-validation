import os
import re
import yaml
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(SCRIPT_DIR, "../content")
SHORTCODES_DIR = os.path.join(SCRIPT_DIR, "../layouts/shortcodes")


def parse_front_matter(filepath):
    """Extract front matter as a dictionary."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r'^---(.*?)---', content, re.DOTALL)
    if match:
        return yaml.safe_load(match.group(1))
    return {}


def validate_image_paths(filepath, front_matter, verbose=False):
    """Validate featured_image and recipe.image in front matter."""
    errors = []
    base_dir = os.path.dirname(filepath)

    # Validate featured_image
    featured_image = front_matter.get("featured_image")
    if featured_image:
        image_path = resolve_image_path(base_dir, featured_image)
        exists = os.path.isfile(image_path)
        if verbose:
            print(f"  Featured image: '{featured_image}' - {'Exists' if exists else 'Missing'}")
        if not exists:
            errors.append(f"Missing featured_image '{featured_image}' in {filepath}")

    # Validate recipe.image
    recipe = front_matter.get("recipe", {})
    recipe_image = recipe.get("image")
    if recipe_image:
        image_path = resolve_image_path(base_dir, recipe_image)
        exists = os.path.isfile(image_path)
        if verbose:
            print(f"  Recipe image: '{recipe_image}' - {'Exists' if exists else 'Missing'}")
        if not exists:
            errors.append(f"Missing recipe.image '{recipe_image}' in {filepath}")

    return errors


def resolve_image_path(base_dir, img_path):
    """Resolve image path relative to the base directory or absolute in the content directory."""
    if img_path.startswith("/"):
        # Absolute path relative to the content directory
        return os.path.join(CONTENT_DIR, img_path.lstrip("/"))
    return os.path.join(base_dir, img_path)


def validate_relative_image_paths(filepath, verbose=False):
    """Validate relative image paths in Markdown content."""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all relative image paths
    image_paths = re.findall(r'!\[.*?\]\((?!http)(.*?)\)', content)
    base_dir = os.path.dirname(filepath)

    if verbose and image_paths:
        print("  Relative image references:")

    for img_path in image_paths:
        img_full_path = resolve_image_path(base_dir, img_path)
        exists = os.path.isfile(img_full_path)
        if verbose:
            print(f"    '{img_path}' - {'Exists' if exists else 'Missing'}")
        if not exists:
            errors.append(f"Missing relative image '{img_path}' in {filepath}")

    return errors


def validate_internal_links(filepath, verbose=False):
    """Validate internal page hyperlinks."""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find internal links of the form [Text](/some-path/)
    links = re.findall(r'\[.*?\]\((/[^)]+/)\)', content)

    if verbose and links:
        print("  Internal page references:")

    for link in links:
        linked_bundle_path = os.path.join(CONTENT_DIR, link.lstrip("/"), "index.md")
        exists = os.path.isfile(linked_bundle_path)
        if verbose:
            print(f"    '{link}' - {'Exists' if exists else 'Missing'}")
        if not exists:
            errors.append(f"Missing content bundle for link '{link}' in {filepath}")

    return errors


def validate_shortcodes(filepath, available_shortcodes, verbose=False):
    """Validate shortcode references in Markdown files."""
    errors = []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find all shortcode references ignoring closing tags
    shortcodes = re.findall(r'{{<\s*([^/\s]+)\s*.*?>}}', content)

    if verbose and shortcodes:
        print("  Shortcode references:")

    for shortcode in shortcodes:
        if verbose:
            print(f"    '{shortcode}' - {'Exists' if shortcode in available_shortcodes else 'Missing'}")
        if shortcode not in available_shortcodes:
            errors.append(f"Missing shortcode file '{shortcode}.html' referenced in {filepath}")

    return errors


def get_available_shortcodes():
    """Retrieve available shortcodes from the shortcodes directory."""
    return {
        os.path.splitext(file)[0]
        for file in os.listdir(SHORTCODES_DIR)
        if file.endswith(".html")
    }


def main():
    parser = argparse.ArgumentParser(description="Validate Markdown content for images, links, and shortcodes.")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output for file validation.")
    args = parser.parse_args()

    errors = []
    available_shortcodes = get_available_shortcodes()

    if args.verbose:
        print("Available shortcodes:")
        for shortcode in sorted(available_shortcodes):
            print(f"  - {shortcode}")

    for root, _, files in os.walk(CONTENT_DIR):
        for file in files:
            if file.endswith(".md"):
                filepath = os.path.join(root, file)

                if args.verbose:
                    print(f"\nProcessing file: {filepath}")

                # Validate front matter image paths
                front_matter = parse_front_matter(filepath)
                errors.extend(validate_image_paths(filepath, front_matter, verbose=args.verbose))

                # Validate relative image paths in content
                errors.extend(validate_relative_image_paths(filepath, verbose=args.verbose))

                # Validate internal links
                errors.extend(validate_internal_links(filepath, verbose=args.verbose))

                # Validate shortcodes
                errors.extend(validate_shortcodes(filepath, available_shortcodes, verbose=args.verbose))

    if errors:
        print("\nValidation errors found:")
        for error in errors:
            print(f"- {error}")
        exit(1)
    else:
        print("\nAll validations passed successfully.")


if __name__ == "__main__":
    main()
