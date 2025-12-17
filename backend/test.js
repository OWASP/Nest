// import "dotenv/config";
import { algoliasearch } from "algoliasearch";

const client = algoliasearch(
    process.env.DJANGO_ALGOLIA_APPLICATION_ID,
    process.env.DJANGO_ALGOLIA_WRITE_API_KEY
);

// name of your index
const indexName = "local_issues";

async function addLabelToAll() {
    let page = 0;
    const batchSize = 1000;
    let updates = [];

    while (true) {
        // search a page of hits
        const res = await client.searchSingleIndex({
            indexName,
            searchParams: {
                query: "",
                page: page,
                hitsPerPage: batchSize,
                attributesToRetrieve: ["objectID"]
            }
        });

        const hits = res.hits;
        if (!hits || hits.length === 0) break;

        // prepare partial updates
        for (const hit of hits) {
            updates.push({
                objectID: hit.objectID,
                // clear any existing idx_labels while setting idx_tags
                idx_labels: [],
                idx_tags: ["good first issue", "help wanted"]
            });
            // if (updates.length >= 10) break;
        }

        if (updates.length >= batchSize) {
            await client.partialUpdateObjects({
                indexName,
                objects: updates,
                createIfNotExists: false
            });
            updates = [];
        }

        page++;
        if (page >= res.nbPages) break;
    }

    if (updates.length) {
        await client.partialUpdateObjects({
            indexName,
            objects: updates,
            createIfNotExists: false
        });
    }

    console.log("✔ Added label to all issues");
}

addLabelToAll().catch(console.error);