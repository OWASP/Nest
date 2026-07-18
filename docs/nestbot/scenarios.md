# NestBot Scenario Matrix

| # | User message | Router decision | Expected bot response |
|---|---|---|---|
| 1 | "how do I contribute to OWASP?" | `general_owasp` | Contribution guide + #contribute link |
| 2 | "what is juice shop?" | `project-juice-shop` | Redirect to #project-juiceshop |
| 3 | "how do I apply for GSoC?" | `gsoc` | Redirect to #gsoc |
| 4 | "what's the weather today?" | `off_topic` | Silently ignored by QuestionDetector |
| 5 | "who maintains the cheat sheet series?" | `general_owasp` | RAG answer from project data |
| 6 | "is there a chapter in Berlin?" | `general_owasp` | RAG answer from chapter data |
| 7 | "how do I report a security issue?" | `general_owasp` | Security policy link |
| 8 | "how does nettacker work?" | `project-nettacker` | Redirect to #project-nettacker |
| 9 | "what is threat dragon?" | `project-threat-dragon` | Redirect to #project-threat-dragon |
| 10 | "how do I set up nest locally?" | `project-nest` | Redirect to #project-nest |
| 11 | "how to get a mentor at OWASP?" | `mentors` | Redirect to #mentors |
| 12 | "how do I sponsor OWASP?" | `sponsorship` | Redirect to #sponsorship |
| 13 | "are there any security jobs?" | `jobs` | Redirect to #jobs |
| 14 | "what is devsecops?" | `devsecops` | Redirect to #devsecops |
| 15 | "how to do threat modeling?" | `threat-modeling` | Redirect to #threat-modeling |
| 16 | "what is appsec?" | `appsec` | Redirect to #appsec |
| 17 | "OWASP top 10 list" | `appsec` | Redirect to #appsec |
| 18 | "how to donate to OWASP?" | `sponsorship` | Redirect to #sponsorship |
| 19 | "is there a contribution guide?" | `contribute` | Redirect to #contribute |
| 20 | "STRIDE threat modelling methodology" | `threat-modeling` | Redirect to #threat-modeling |
| 21 | "what is WebGoat?" | `project-juice-shop` | Redirect to #project-juiceshop |
| 22 | "who is on the OWASP board?" | `general_owasp` | RAG answer from board data |
| 23 | "what projects does OWASP have?" | `general_owasp` | RAG answer listing projects |
| 24 | "how do I become an OWASP member?" | `general_owasp` | RAG answer with membership info |
| 25 | "what events does OWASP run?" | `general_owasp` | RAG answer from event data |
| 26 | "what is google summer of code?" | `gsoc` | Redirect to #gsoc |
| 27 | "DevSecOps pipeline setup" | `devsecops` | Redirect to #devsecops |
| 28 | "NestBot is not answering" | `project-nest` | Redirect to #project-nest |
| 29 | "OWASP chapter in Tokyo" | `general_owasp` | RAG answer from chapter data |
| 30 | "what programming languages does OWASP use?" | `general_owasp` | RAG answer from project data |
| 31 | "how to run nettacker scan?" | `project-nettacker` | Redirect to #project-nettacker |
| 32 | "what is PASTA threat modeling?" | `threat-modeling` | Redirect to #threat-modeling |
| 33 | "tell me a joke" | `off_topic` | Silently ignored by QuestionDetector |
| 34 | "what is the OWASP license?" | `general_owasp` | RAG answer |
| 35 | "how do I join the OWASP mentorship program?" | `mentors` | Redirect to #mentors |
