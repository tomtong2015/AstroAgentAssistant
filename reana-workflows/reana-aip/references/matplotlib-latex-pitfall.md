# Matplotlib + LaTeX Math + Python f-strings

## Pitfall
Using f-strings with LaTeX math delimiters (`$\phi$`, `$\alpha$`, etc.) in matplotlib
titles/text triggers a `SyntaxWarning: invalid escape sequence '\p'` (or '\a', etc.)
because Python's f-string parser sees `\$` as a (non-existent) escape sequence.

## Broken
```python
phi = (1 + np.sqrt(5)) / 2
ax.set_title(f"Golden Spiral  --  $\phi = {phi:.5f}$")  # SyntaxWarning!
```

## Fixed
Use a raw f-string **or** — preferred — a raw string with `.format()`:
```python
phi = (1 + np.sqrt(5)) / 2
ax.set_title(r"Golden Spiral  --  $\phi = {p:.5f}$".format(p=phi))
```

### Why `.format()` on `r"..."`?
- `r"..."` tells Python "don't interpret backslash escapes" → no SyntaxWarning.
- `.format()` injects the Python variable after the string is parsed.
- The `r` prefix is safe because the `\\phi` is actually `\phi` in the raw string,
  which is valid LaTeX for matplotlib's mathtext renderer.

### If you MUST use f-strings
Prefix with `r`:
```python
ax.set_title(f"Golden Spiral  --  $\\phi = {phi:.5f}$")  # still warns in some Python versions
```
The `r""` prefix is the cleanest fix, but `.format()` on `r"..."` is the most compatible
across Python versions (Python 3.12+ is stricter about raw-f-string warnings).
