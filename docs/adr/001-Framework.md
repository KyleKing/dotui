# Framework Selection

- Status: Proposed
- Date: 2022-08-01

Technical Story: Choosing a good framework is important

## Comparison

| Criteria           | [Textual](https://github.com/Textualize/textual) | [BubbleTea](https://github.com/charmbracelet/bubbletea) | `ncurses` |
| ------------------ | --------------------------------------------- | --------------------------------------------- |
| Ease of use?       | High | Medium - b/c I would need to learn Go | Low |
| Stability?         | Low, undergoing major changes for CSS Support | High | High |
| Confidence in lTS? | High. Rich-CLI is very popular                | High | High |
| Sufficient Widgets | In early stages and [missing widgets like Edit](https://github.com/Textualize/textual/discussions/365#discussioncomment-2663515) and major changes pending | Many | N/A |
| Notes | In Python | In Go... | TBD |

### Example Projects

#### Textual

- [Official List](https://www.textualize.io/textual/gallery)
    - [Official Example File and Code Viewer](https://github.com/Textualize/textual/blob/c9261f9e620cdda5484acad8680b49b496e067e3/examples/code_viewer.py)
- Two Apps with the Outlined Widget Style that I want
    - [htop-clone](https://github.com/nschloe/tiptop)
    - [objexplore](https://github.com/kylepollina/objexplore)
- [Sliding Panels](https://github.com/hdb/baywatch)
- Libraries
    - [General Input Widgets](https://github.com/sirfuzzalot/textual-inputs)

#### Bubble Tea

- [gh-dash](https://github.com/dlvhdr/gh-dash/blob/3ac7458b0f4ebb24d32d0756d2fff0cc79a45c78/go.mod#L7)
- \*[LazyGit](https://github.com/jesseduffield/lazygit/blob/6dfef08efc5c7f262194c0af35fd777428f33a1a/go.mod#L5) (\*[gocui](https://github.com/jesseduffield/gocui))

## Decision

Consider prototyping with `Textual` first on the `css` branch
