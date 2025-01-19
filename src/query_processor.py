"""Process a query by parsing input, cloning a repository, and generating a summary."""

from config import MAX_DISPLAY_SIZE
from gitingest.query_ingestion import run_ingest_query
from gitingest.query_parser import ParsedQuery, parse_query
from gitingest.repository_clone import CloneConfig, clone_repo

async def process_api_query(
    input_text: str,
    max_file_size: int,
    pattern_type: str = "exclude",
    pattern: str = "",
) -> dict:
    """Process a query for the API endpoint."""
    if pattern_type == "include":
        include_patterns = pattern
        exclude_patterns = None
    elif pattern_type == "exclude":
        exclude_patterns = pattern
        include_patterns = None
    else:
        raise ValueError(f"Invalid pattern type: {pattern_type}")

    try:
        parsed_query: ParsedQuery = await parse_query(
            source=input_text,
            max_file_size=max_file_size,
            from_web=True,
            include_patterns=include_patterns,
            ignore_patterns=exclude_patterns,
        )
        if not parsed_query.url:
            raise ValueError("The 'url' parameter is required.")

        clone_config = CloneConfig(
            url=parsed_query.url,
            local_path=str(parsed_query.local_path),
            commit=parsed_query.commit,
            branch=parsed_query.branch,
        )
        await clone_repo(clone_config)
        summary, tree, content = run_ingest_query(parsed_query)
        with open(f"{clone_config.local_path}.txt", "w", encoding="utf-8") as f:
            f.write(tree + "\n" + content)

        return {
            "summary": summary,
            "tree": tree,
            "content": content,
            "ingest_id": parsed_query.id,
        }

    except Exception as e:
        return {"error": str(e)}
