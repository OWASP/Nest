"I've worked on similar PRs before involving breadcrumb logic (specifically HIDDEN_SEGMENTS in 
frontend/src/hooks/useBreadcrumbs.ts
). The pattern we follow there is to hide intermediate segments precisely because the parent page acts as a "Hub"—providing context and navigation to what lies beneath.

I think we should apply that same philosophy here. Since this is a community-first project, the /community page shouldn't just be a directory; it should be a dynamic Community Hub that showcases the pulse of the project.

Here is my expanded idea for what this page should include:

Project Pulse: Recent releases, live GitHub activity streams, and commit stats.
People: Highlights for New Members, Maintainers, and Sponsors.
Resources: A dedicated FAQ section and quick navigation cards to Chapters/Organizations.
Community Highlights: Spotlights on active contributors or chapters.
This approach transforms the page from a simple list into a landing page that actually reflects the vibrant activity of the community. We can start with a few of these modules (like the intro and stats) and iterate to add the live feeds."

# Role
Act as a Senior Frontend Engineer specializing in Next.js, TypeScript, and Component Design.


we have to make a page.tsx for /community its currently not present 

we have HIDDEN_SEGMENTS in frontend/src/hooks/useBreadcrumbs.ts , look at the parent link 
eg :http://localhost:3000/my/mentorship/programs/test-program/modules/test-module

we have modules in hidden segments , but the parent link is programs programs which has test program info and modules cards

make something similar to it , but /community , look at the ideas and maintain consistency of design , reuse code from /components and /utils 

The goal is to avoid making this page a simple directory. Instead, it must follow the "Community Hub" philosophy—a dynamic landing page that showcases the pulse of the project, similar to how our `/programs` page functions as a hub for its sub-modules.

# Reference Architecture
Please analyze the existing architecture for the pages in HIDDEN_SEGMENT in usebreadcrubs.tsx (specifically how it handles parent links and module cards) and apply that same logic here.

keep in mind file str