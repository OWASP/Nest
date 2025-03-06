def get_typesense_params_for_index(index_name):
    """Return Typesense search parameters based on the index name."""
    # Common parameters across all indices
    params = {
        "num_typos": 2,
        "prioritize_exact_match": True,
        "highlight_full_fields": "",  # Equivalent to attributesToHighlight: []
        "drop_tokens_threshold": 1,  # Similar to removeWordsIfNoResults: allOptional
    }

    match index_name:
        case "issue":
            params["query_by"] = "title,summary,project_name,labels"
            params["query_by_weights"] = "5,3,2,1"
            params["include_fields"] = (
                "comments_count,created_at,hint,labels,project_name,project_url,repository_languages,summary,title,updated_at,url"
            )
            params["sort_by"] = "created_at:desc"

        case "chapter":
            params["query_by"] = "name,region,leaders,tags,summary"
            params["query_by_weights"] = "10,5,3,2,1"
            params["include_fields"] = (
                "_geoloc,created_at,is_active,key,leaders,name,region,related_urls,suggested_location,summary,tags,top_contributors,updated_at,url"
            )

        case "project":
            params["query_by"] = "name,summary,languages,topics,type"
            params["query_by_weights"] = "10,5,3,2,1"
            params["include_fields"] = (
                "contributors_count,forks_count,is_active,issues_count,key,languages,leaders,level,name,organizations,repositories_count,stars_count,summary,top_contributors,topics,type,updated_at,url"
            )
            params["sort_by"] = "stars_count:desc,updated_at:desc"

        case "committee":
            params["query_by"] = "name,summary,leaders"
            params["query_by_weights"] = "5,3,2"
            params["include_fields"] = (
                "created_at,key,leaders,name,related_urls,summary,top_contributors,updated_at,url"
            )
            params["sort_by"] = "updated_at:desc"

        case "user":
            params["query_by"] = "login,name,bio,company,location"
            params["query_by_weights"] = "10,8,5,3,2"
            params["include_fields"] = (
                "avatar_url,bio,company,created_at,email,followers_count,following_count,key,location,login,name,public_repositories_count,title,updated_at,url"
            )
            params["sort_by"] = "followers_count:desc"

        case _:
            params["query_by"] = "_all"

    return params
