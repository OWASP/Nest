"""Typesense search parameters based on the index name."""


def get_typesense_params_for_index(index_name):
    """Return Typesense search parameters based on the index name."""
    # Common attributes
    params = {
        "num_typos": 2,
        "prioritize_exact_match": True,
        "highlight_full_fields": "",  # Equivalent to attributesToHighlight: []
        "drop_tokens_threshold": 1,  # Similar to removeWordsIfNoResults: allOptional
    }

    match index_name:
        case "issue":
            # searchable attributes
            params["query_by"] = (
                "title,project_name,repository_name,labels,repository_languages,project_description,repository_description,project_tags,repository_topics,author_login,author_name,summary,project_level"
            )
            # weights of searchable attributes
            params["query_by_weights"] = "7,7,7,6,6,5,5,4,4,3,3,2,1"
            # equivalent to attributesToRetrieve
            params["include_fields"] = (
                "comments_count,created_at,hint,labels,project_name,project_url,repository_languages,summary,title,updated_at,url"
            )
            # sort by fields
            params["sort_by"] = "created_at:desc,comments_count:desc,repository_stars_count:desc"

        case "chapter":
            params["query_by"] = (
                "name,leaders,top_contributors.login,top_contributors.name,top_suggested_location,country,region,postal_code,tags"
            )
            params["query_by_weights"] = "10,5,4,4,2,2,2,2,1"
            params["include_fields"] = (
                "_geoloc,created_at,is_active,key,leaders,name,region,related_urls,suggested_location,summary,tags,top_contributors,updated_at,url"
            )
            params["sort_by"] = "created_at:asc,updated_at:desc"

        case "project":
            params["query_by"] = (
                "name,repositories.description,repositories.name,custom_tags,languages,tags,topics,description,companies,organizations,leaders,top_contributors.login,top_contributors.name,level"
            )
            params["query_by_weights"] = "8,7,7,6,6,6,6,5,4,4,3,2,2,1"
            params["include_fields"] = (
                "contributors_count,forks_count,is_active,issues_count,key,languages,leaders,level,name,organizations,repositories_count,stars_count,summary,top_contributors,topics,type,updated_at,url"
            )
            params["sort_by"] = "level_raw:desc,stars_count:desc,updated_at:desc"

        case "committee":
            params["query_by"] = "name,leaders,top_contributors.login,top_contributors.name,tags"
            params["query_by_weights"] = "4,3,2,2,1"
            params["include_fields"] = (
                "created_at,key,leaders,name,related_urls,summary,top_contributors,updated_at,url"
            )
            params["sort_by"] = "name:asc,created_at:asc,updated_at:desc"

        case "user":
            params["query_by"] = "email,login,name,company,location,bio"
            params["query_by_weights"] = "3,3,3,2,2,1"
            params["include_fields"] = (
                "avatar_url,bio,company,created_at,email,followers_count,following_count,key,location,login,name,public_repositories_count,title,updated_at,url"
            )
            params["sort_by"] = "max_contributions_count:desc,created_at:desc,followers_count:desc"

        case _:
            params["query_by"] = "_all"

    return params
