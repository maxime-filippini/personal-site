---
title: Automate your CV with Typst and GitHub
posted_on: 2025-10-14
last_update: 2025-10-14
draft: false
abstract: >
    Creating and maintaining a professional CV often involves tedious formatting and versioning challenges. This post presents a fully automated workflow for building and hosting your CV using Typst and GitHub Actions. We leverage the separation between source code and compiled outputs to automate the reproducible parts of our process, and through that, ensure consistent formatting across versions and easy online distribution of our resume. 
---


Writing a resume can be a pain, mostly because it's something we only look at every few years (if we're lucky). Of course, choosing the right experiences and projects to put on it is a big part of the complexity of the task, but there are other aspects that can definitely be improved upon.

For example, **consistency of formatting** is paramount, and easy to mess up when using a tool like Microsoft Word. Similarly, **making sure you can always start off from your last resume**, and not have to start all over again, can be difficult, especially if you've changed computer or are not willing to keep paying for an Office 365 subscription. 

Finally, **distributing your CV** can also be made easier than having to send individual emails to whoever may be having an opportunity for you.

In this post, I'll show you one way of building your CV in plain text and have an automated system build a beautifully formatted PDF from it, upon every update of the contents.

## Writing the CV

In general, I recommend against writing documents using software like Microsoft Word, especially if you are tech savvy, because it couples contents and format to an extent that can be counterproductive. Of course, there are ways to make MS Word manageable, for example by making sure that named styles are used throughout the document, which will allow you to make sweeping format changes down the road.

But the best solution is, in my opinion, to write documents in a plain text format which will then be processed by a specific piece of software to convert it to the desired output format. For example, using a tool like [Pandoc](https://pandoc.org/), you can use the same `.md` file and turn it into HTML pages, slide shows, and even `.docx` files. 

For publications and resumes, whose target formats are usually limited to PDF documents, [Typst](https://typst.app/) is an excellent format to consider. 

Typst is both a language and a piece of software that takes files written in that language (using the `.typ` extension) and produces PDF documents. It can be easily installed using an OS package manager (e.g. Homebrew on macOS), and run via a terminal. For example, if you type the following in your terminal:

```console
typst --help
```

you should see:

```console
Typst 0.13.1

Usage: typst [OPTIONS] <COMMAND>

Commands:
  compile  Compiles an input file into a supported output format [aliases: c]
  watch    Watches an input file and recompiles on changes [aliases: w]

(truncated for brevity)
```

Converting Typst files to PDFs is as easy as calling `typst compile` or `typst watch` on your `.typ` file. Alternatively, you can install the [Tinymist Typst VSCode extension](https://marketplace.visualstudio.com/items?itemName=myriad-dreamin.tinymist), which will allow you to run these commands directly inside of VSCode, and get a live preview pane in the editor.

![](/assets/typst-vscode.png)

Fundamentally, a Typst document can look a lot like Markdown, e.g.

```typst
= This is a heading

This text will be *bold*.

== This is a sub-heading

This is some inline math: $1 + 1 = 2$.

This is some block math:

$
    1 + 1 = 2
$

This is a simple list with nested items:

- Item 1
- Item 2
    - Sub-item 1
    - Sub-item 2
```

But we can also add **typesetting information** and even define custom functions to use in our document:

```typst
#set page(paper: "a4")          // This will define our page format
#set heading(numbering: "1.")   // This will define how our headings are shown

// This is a function that allows us to place elements in a 2x2 grid
#let two-by-two(
  top-left: "",
  top-right: "",
  bottom-left: "",
  bottom-right: "",
) = {
  // The brackets indicate "markup mode", i.e. everything within should be rendered
  // as is. In this mode, we prefix variables with a pound sign to refer to said
  // variable.
  [
    #top-left #h(1fr) #top-right \
    #bottom-left #h(1fr) #bottom-right
  ]
}

// The root of the document is always in "markup mode".

*This is text that will be rendered bold.*

// Here, we're passing markup to our function. Typst allows us to mix and match
// code and markup in a way that is very convenient.
#two-by-two(
    top-left: [
        $1+1=$
    ],
    top-right: [
        $2$
    ]
)
```

For my own resume, I define a `work` function that will apply a common layout that I can reuse throughout. However, because this function does not apply any formatting to the list describing the work experience, I can simply write that list after the call to `work`, i.e.

```typst
== Work Experience

#work(
  title: "Senior Manager - Financial Risk Management",
  location: "Luxembourg",
  company: "Deloitte Luxembourg",
  dates: dates-helper(start-date: "Oct 2023", end-date: "Present"),
)
- Acted as technical leader for a team of Python developers, including a taskforce focused on the use of artificial intelligence
- Developed and facilitated technical training sessions on financial risk management (incl. liquidity risk, sustainability risk)
- Led the development of internal libraries for risk calculations and workflow coordination for our department's reporting activities.
- Led advisory projects focused on the validation of models used by the risk management functions of Luxembourg ManCos (Value-at-Risk, Liquidity framework).
```

If you want to take a look at what my resume page looks like in Typst, check out [this file](https://github.com/maxime-filippini/resume/blob/develop/Maxime%20Filippini%20-%20CV.typ). For this file to be as concise as it is, I use a `lib.typ` file that contains functions and formatting utilities used in the resume.

## Generating and hosting the CV

Compiling your CV manually on your laptop with the `typst` command works well, but we can take it a step further.

Since Typst files are just plain text, they can be easily tracked using a version control system like Git. By hosting the Git repository on [GitHub](https://github.com/), we get the added benefit of a centralized source of truth that can be cloned on other devices, as we need it.

Finally, GitHub allows us to automate the build process so that a fresh PDF version of the resume is generated automatically whenever a change is pushed to the `.typ` file.

```callout
In our situation, the `.typ` file can be seen as "source code", from which we wish to derive [artifacts](https://en.wikipedia.org/wiki/Artifact_(software_development)). Here, the sole artifact we care about is the "compiled" version of our source code, i.e. the PDF.
```

On GitHub, we can define tasks to run automatically whenever we push new changes using [GitHub actions](https://github.com/features/actions). To set up such a workflow using GitHub actions, we add a `build.yaml` file in `.github/workflows` inside the repository, and include the following content:

```yaml
name: Build Typst document
on: [push, workflow_dispatch]

permissions:
  contents: write

jobs:
  build_typst_documents:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v3
      - name: Typst
        uses: lvignoli/typst-action@main
        with:
          source_file: "Maxime Filippini - CV.typ"

      - name: Upload PDF file
        uses: actions/upload-artifact@v4
        with:
          name: PDF
          path: "*.pdf"

      - name: Get current date
        id: date
        run: echo "DATE=$(date +%Y-%m-%d-%H:%M)" >> $GITHUB_ENV

      - name: Release
        uses: softprops/action-gh-release@v1
        if: github.ref_type == 'tag'
        with:
          name: "${{ github.ref_name }} — ${{ env.DATE }}"
          files: "Maxime Filippini - CV.pdf"
```

The steps of the action are relatively simple:

- First, the contents of the repository are obtained (this is called "checking out" the repository);
- Then, `typst` is called, via the pre-made action `lvignoli/typst-action@main`;
- Then, the resulting PDF gets uploaded as an artifact for use in subsequent steps; and
- Finally, the PDF is attached to a release on the repository if the commit has a [tag](https://git-scm.com/book/ms/v2/Git-Basics-Tagging) attached to it.

Now, whenever we commit a change to our CV on our machine, and attach a tag to it that indicates a version number (e.g. `v2.0.0`), the workflow will run and a PDF will be produced in a release, as shown below:

![](/assets/github-release.png)

As a result of this, we now have our CV hosted on GitHub, and we just have to send the link to whoever is interested. Said link will take the following form:

```console
    https://github.com/<your-name>/<your-repo>/releases/latest/download/<file-name>.pdf
```

For my resume, the link is the following: 

```callout
[Maxime.Filippini.-.CV.pdf](https://github.com/maxime-filippini/resume/releases/latest/download/Maxime.Filippini.-.CV.pdf)
```

## Conclusion

Typst is a powerful tool that can do much more than what is needed for a CV. If you think this is a tool you could get some use out of, head over to the [tutorial](https://typst.app/docs/tutorial/) or the [GitHub repository](https://github.com/typst/typst), and start exploring!

Besides how cool Typst is, the main idea to take away from the approach proposed here is the idea of **deriving artifacts** from source files, which can generally be automated and run in a reproducible way for all users. A more common application of this idea is the generation of code documentation, using tools like [mkdocstrings](https://mkdocstrings.github.io/).

Finally, if you want to see the way my CV was built using Typst, check out the [repository](https://github.com/maxime-filippini/resume).
