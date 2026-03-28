# MBSE4U SysML v2 API Helpers

Generic helper functions for interacting with SysML v2 REST API. This library simplifies the process of querying projects, commits, and traversing the SysML v2 model structure.

## Installation

You can install this package via pip.

```bash
pip install mbse4u-sysmlv2-helpers
```

## Getting Started

Here is a simple example of how to connect to a server and list projects.

```python
import mbse4u_sysmlv2_helpers as api

SERVER_URL = "http://localhost:9000"

try:
    # Fetch all projects
    projects = api.get_projects(SERVER_URL)
    print(f"Found {len(projects)} projects.")

    for p in projects:
        print(f"- {p.get('name')} (ID: {p.get('@id')})")
        
        # Get commits for the first project
        commits = api.get_commits(SERVER_URL, p['@id'])
        if commits:
            latest_commit = commits[-1]
            print(f"  Latest commit: {latest_commit.get('id')}")

except Exception as e:
    print(f"Error: {e}")
```

## API Reference

### Project & Commit Management

- `get_projects(server_url: str, page_size: int = 256) -> List[Dict]`
  - Fetches and sorts projects alphabetically from the given server.

- `get_commits(server_url: str, project_id: str) -> List[Dict]`
  - Retrieves commit history for a specific project, sorted by creation date.

- `get_commit_url(server_url: str, project_id: str, commit_id: str) -> str`
  - Helper to construct the base URL for commit-specific queries.

### Caching

- `load_model_cache(server_url: str, project_id: str, commit_id: str, page_size: int = 256) -> int`
  - Loads all elements of a commit into an in-memory `ELEMENT_CACHE` to speed up subsequent queries. Returns the number of elements cached.

### Element Retrieval

- `get_element_fromAPI(query_url: str, element_id: str) -> Optional[Dict]`
  - Fetches a single element by ID, checking the local cache first.

- `get_elements_fromAPI(query_url: str, element_ids: List[str]) -> List[Dict]`
  - Batch retrieval of elements by a list of IDs.

- `get_elements_byDeclaredName_fromAPI(server_url: str, project_id: str, commit_id: str, name: str) -> List[Dict]`
  - Fetches elements by their `declaredName`. Includes logic to find elements that redefine a named element via `Redefinition` relationships.

- `get_elements_byKind_fromAPI(server_url: str, project_id: str, commit_id: str, kind: str) -> List[Dict]`
  - Query for all elements of a specific type (e.g., `'PartUsage'`, `'MetadataDefinition'`).

- `get_elements_byProperty_fromAPI(server_url: str, project_id: str, commit_id: str, property: str, value: str) -> List[Dict]`
  - Fetches elements matching a given property/value pair. Also resolves `Redefinition` relationships.

### Traversal & Structure

- `get_contained_elements(server_url, project_id, commit_id, element_id, kind, elementKind='ownedElement') -> List[Dict]`
  - Returns children of a specific type within an element's owned collection.

- `get_recursive_owned_elements(server_url, project_id, commit_id, start_element_id, kind, max_depth=5, current_depth=0) -> List[Dict]`
  - Recursively fetches descendants of a specific kind down to a maximum depth.

- `get_owned_usages(server_url, project_id, commit_id, owner, feature_name) -> List[Dict]`
  - Fetches owned usages for an element from both the Usage itself and its Definition.

- `check_specialization_hierarchy(query_url, element, super_element, visited=None) -> bool`
  - Recursively checks if an element specializes the given `super_element`. Uses a visited set to prevent infinite loops.

- `find_element_by_id(aggregated_results: List[Dict], target_id: str) -> Optional[Dict]`
  - Searches a list of elements for one matching a specific ID.

- `find_elements_specializing(server_url, project_id, commit_id, elements, super_element_name, element_kind=None) -> List[Dict]`
  - Filters a list to only include elements that specialize a given supertype (by qualified name).

### Feature & Attribute Access

- `get_feature(server_url, project_id, commit_id, owner, feature_name, feature_kind='AttributeUsage') -> Optional[Dict]`
  - Retrieves a specific feature element (by name and kind) from an owner element, including inherited features.

- `get_feature_value(server_url, project_id, commit_id, owner, feature_name, feature_kind='AttributeUsage') -> Union[str, int, float, None]`
  - Extracts the resolved value of a feature (attribute) from an element.

- `get_attribute_value_from_usage(query_url: str, attr_usage: Dict) -> Union[str, int, float, None]`
  - Low-level helper to extract and resolve a value from an `AttributeUsage` element, including literal values, enum references, and `FeatureChainExpression`.

- `getValueFromOperatorExpressionUnit(query_url: str, opExp: Dict) -> Optional[Dict]`
  - Helper to extract the value element from an `OperatorExpression` (e.g., for unit quantities).

### Metadata

- `get_metadata_ids_by_name(server_url, project_id, commit_id, metadata_shortnames: List[str]) -> Dict[str, str]`
  - Fetches the IDs of `MetadataDefinition` elements by their short names. Returns a mapping of short name → ID.

- `get_metadatausage_annotatedElement_ids(server_url, project_id, commit_id, metadefinition_dict: Dict[str, str]) -> Dict[str, List[str]]`
  - Retrieves the IDs of elements annotated with specific metadata definitions. Returns a mapping of metadata key → list of annotated element IDs.

### Element Relationships & Documentation

- `get_element_definition(server_url, project_id, commit_id, element: Dict) -> Optional[Dict]`
  - Retrieves the `Definition` element for a given usage element.

- `get_element_documentation(server_url, project_id, commit_id, element_id: str) -> Optional[List[str]]`
  - Retrieves the documentation body texts for a given element.

### Model Update

- `update_model_element(server_url, project_id, commit_id, element_id, feature_name, feature_value) -> str`
  - Creates a new commit that updates a single feature value on a model element. Returns the new commit ID.

## License

Copyright 2026 MBSE4U - Tim Weilkiens. Licensed under the Apache License, Version 2.0.
