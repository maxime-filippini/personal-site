# Separate deployment-bound posts from runtime content

Posts, including MDX interactive elements, will be compiled and deployed with the site; publishing a post therefore produces a new verified site deployment. Manually authored material stays in Git and follows that publication lifecycle. Mutable, non-executable information produced by an independent process may instead be read at runtime from R2 and updated without deploying the site. This boundary preserves safe and predictable compilation for executable MDX while allowing genuinely independent data to change on its own lifecycle.
