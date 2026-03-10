# PyPI Name Checker

UV Forge can check whether your chosen project name is available on PyPI before you build. This helps avoid naming conflicts with existing packages.

## How to use it

Click the **globe icon** next to the project name field. The button is enabled once the name passes local validation.

Results appear below the field:

| Colour     | Meaning                                  |
| ---------- | ---------------------------------------- |
| **Green**  | Name is available on PyPI                |
| **Red**    | Name is already taken                    |
| **Orange** | Could not reach PyPI (check your connection) |

## Name normalization

PyPI uses [PEP 503](https://peps.python.org/pep-0503/) normalization, which means `my_app`, `my-app`, and `My.App` are all treated as the same package name. UV Forge applies the same normalization before checking, so you'll get an accurate result regardless of how you format the name.

## Package validation in the Add Packages dialog

When adding packages via the Add Packages dialog, each package name is validated against PyPI in real time. This confirms the package actually exists on PyPI before adding it to your project, catching typos early.
