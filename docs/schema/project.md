# OWASP Project

- [1. Property `OWASP Project > audience`](#audience)
- [2. Property `OWASP Project > blog`](#blog)
- [3. Property `OWASP Project > demo`](#demo)
- [4. Property `OWASP Project > documentation`](#documentation)
  - [4.1. OWASP Project > documentation > documentation items](#documentation_items)
- [5. Property `OWASP Project > downloads`](#downloads)
  - [5.1. OWASP Project > downloads > downloads items](#downloads_items)
- [6. Property `OWASP Project > events`](#events)
  - [6.1. OWASP Project > events > events items](#events_items)
- [7. Property `OWASP Project > leaders`](#leaders)
  - [7.1. OWASP Project > leaders > Leader](#leaders_items)
    - [7.1.1. Property `OWASP Project > leaders > Leader > email`](#leaders_items_email)
    - [7.1.2. Property `OWASP Project > leaders > Leader > github`](#leaders_items_github)
    - [7.1.3. Property `OWASP Project > leaders > Leader > name`](#leaders_items_name)
    - [7.1.4. Property `OWASP Project > leaders > Leader > slack`](#leaders_items_slack)
- [8. Property `OWASP Project > level`](#level)
- [9. Property `OWASP Project > license`](#license)
- [10. Property `OWASP Project > mailing-list`](#mailing-list)
- [11. Property `OWASP Project > name`](#name)
- [12. Property `OWASP Project > pitch`](#pitch)
- [13. Property `OWASP Project > repositories`](#repositories)
  - [13.1. OWASP Project > repositories > Repository](#repositories_items)
    - [13.1.1. Property `OWASP Project > repositories > Repository > changelog`](#repositories_items_changelog)
    - [13.1.2. Property `OWASP Project > repositories > Repository > code_of_conduct`](#repositories_items_code_of_conduct)
    - [13.1.3. Property `OWASP Project > repositories > Repository > contribution_guide`](#repositories_items_contribution_guide)
    - [13.1.4. Property `OWASP Project > repositories > Repository > description`](#repositories_items_description)
    - [13.1.5. Property `OWASP Project > repositories > Repository > name`](#repositories_items_name)
    - [13.1.6. Property `OWASP Project > repositories > Repository > url`](#repositories_items_url)
- [14. Property `OWASP Project > sponsors`](#sponsors)
  - [14.1. OWASP Project > sponsors > Sponsor](#sponsors_items)
    - [14.1.1. Property `OWASP Project > sponsors > Sponsor > description`](#sponsors_items_description)
    - [14.1.2. Property `OWASP Project > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [14.1.3. Property `OWASP Project > sponsors > Sponsor > name`](#sponsors_items_name)
    - [14.1.4. Property `OWASP Project > sponsors > Sponsor > url`](#sponsors_items_url)
- [15. Property `OWASP Project > tags`](#tags)
  - [15.1. OWASP Project > tags > tags items](#tags_items)
- [16. Property `OWASP Project > type`](#type)
- [17. Property `OWASP Project > website`](#website)

**Title:** OWASP Project

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP schema.

| Property                           | Pattern | Type                        | Deprecated | Definition | Title/Description                                      |
| ---------------------------------- | ------- | --------------------------- | ---------- | ---------- | ------------------------------------------------------ |
| + [audience](#audience )           | No      | enum (of string)            | No         | -          | The intended audience for the project.                 |
| - [blog](#blog )                   | No      | string                      | No         | -          | Project's blog.                                        |
| - [demo](#demo )                   | No      | string                      | No         | -          | Optional URL to the project demo.                      |
| - [documentation](#documentation ) | No      | array of string             | No         | -          | Optional URLs to project documentation.                |
| - [downloads](#downloads )         | No      | array of string             | No         | -          | Optional list of download URLs.                        |
| - [events](#events )               | No      | array of string             | No         | -          | Event URLs related to the project.                     |
| + [leaders](#leaders )             | No      | array                       | No         | -          | Leaders of the project.                                |
| + [level](#level )                 | No      | enum (of integer or number) | No         | -          | Project level.                                         |
| - [license](#license )             | No      | enum (of string)            | No         | -          | The license of the project.                            |
| - [mailing-list](#mailing-list )   | No      | string                      | No         | -          | The optional mailing list associated with the project. |
| + [name](#name )                   | No      | string                      | No         | -          | The unique name of the project.                        |
| + [pitch](#pitch )                 | No      | string                      | No         | -          | The project pitch.                                     |
| - [repositories](#repositories )   | No      | array                       | No         | -          | Repositories associated with the project.              |
| - [sponsors](#sponsors )           | No      | array                       | No         | -          | Sponsors of the project.                               |
| + [tags](#tags )                   | No      | array of string             | No         | -          | Tags for the project                                   |
| + [type](#type )                   | No      | enum (of string)            | No         | -          | The type of the project: code, documentation or tool.  |
| - [website](#website )             | No      | string                      | No         | -          | The official website of the project.                   |

## <a name="audience"></a>1. Property `OWASP Project > audience`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The intended audience for the project.

Must be one of:
* "breaker"
* "builder"
* "defender"

## <a name="blog"></a>2. Property `OWASP Project > blog`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Project's blog.

## <a name="demo"></a>3. Property `OWASP Project > demo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Optional URL to the project demo.

## <a name="documentation"></a>4. Property `OWASP Project > documentation`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Optional URLs to project documentation.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be             | Description |
| ------------------------------------------- | ----------- |
| [documentation items](#documentation_items) | -           |

### <a name="documentation_items"></a>4.1. OWASP Project > documentation > documentation items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="downloads"></a>5. Property `OWASP Project > downloads`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Optional list of download URLs.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description |
| ----------------------------------- | ----------- |
| [downloads items](#downloads_items) | -           |

### <a name="downloads_items"></a>5.1. OWASP Project > downloads > downloads items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="events"></a>6. Property `OWASP Project > events`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Event URLs related to the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [events items](#events_items)   | -           |

### <a name="events_items"></a>6.1. OWASP Project > events > events items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="leaders"></a>7. Property `OWASP Project > leaders`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

**Description:** Leaders of the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 2                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description       |
| ------------------------------- | ----------------- |
| [Leader](#leaders_items)        | A project leader. |

### <a name="leaders_items"></a>7.1. OWASP Project > leaders > Leader

**Title:** Leader

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | No             |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/leader |

**Description:** A project leader.

| Property                           | Pattern | Type           | Deprecated | Definition | Title/Description           |
| ---------------------------------- | ------- | -------------- | ---------- | ---------- | --------------------------- |
| - [email](#leaders_items_email )   | No      | string or null | No         | -          | The leader's email address. |
| + [github](#leaders_items_github ) | No      | string         | No         | -          | The GitHub username.        |
| - [name](#leaders_items_name )     | No      | string or null | No         | -          | Leader's name.              |
| - [slack](#leaders_items_slack )   | No      | string or null | No         | -          | The Slack username.         |

#### <a name="leaders_items_email"></a>7.1.1. Property `OWASP Project > leaders > Leader > email`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |
| **Format**   | `email`          |

**Description:** The leader's email address.

#### <a name="leaders_items_github"></a>7.1.2. Property `OWASP Project > leaders > Leader > github`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The GitHub username.

| Restrictions                      |                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9-]{1,39}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9-%5D%7B1%2C39%7D%24) |

#### <a name="leaders_items_name"></a>7.1.3. Property `OWASP Project > leaders > Leader > name`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** Leader's name.

#### <a name="leaders_items_slack"></a>7.1.4. Property `OWASP Project > leaders > Leader > slack`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** The Slack username.

| Restrictions                      |                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9._-]{1,21}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9._-%5D%7B1%2C21%7D%24) |

## <a name="level"></a>8. Property `OWASP Project > level`

**Title:** Project level.

|              |                               |
| ------------ | ----------------------------- |
| **Type**     | `enum (of integer or number)` |
| **Required** | Yes                           |
| **Default**  | `2`                           |

**Description:** The numeric level of the project.

Must be one of:
* 2
* 3
* 3.5
* 4

## <a name="license"></a>9. Property `OWASP Project > license`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** The license of the project.

Must be one of:
* "AGPL-3.0"
* "Apache-2.0"
* "BSD-2-Clause"
* "BSD-3-Clause"
* "CC-BY-4.0"
* "CC-BY-SA-4.0"
* "CC0-1.0"
* "EUPL-1.2"
* "GPL-2.0"
* "GPL-3.0"
* "LGPL-2.1"
* "LGPL-3.0"
* "MIT"
* "MPL-2.0"
* "OTHER"

## <a name="mailing-list"></a>10. Property `OWASP Project > mailing-list`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The optional mailing list associated with the project.

## <a name="name"></a>11. Property `OWASP Project > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of the project.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="pitch"></a>12. Property `OWASP Project > pitch`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The project pitch.

## <a name="repositories"></a>13. Property `OWASP Project > repositories`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Repositories associated with the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be   | Description           |
| --------------------------------- | --------------------- |
| [Repository](#repositories_items) | A project repository. |

### <a name="repositories_items"></a>13.1. OWASP Project > repositories > Repository

**Title:** Repository

|                           |                    |
| ------------------------- | ------------------ |
| **Type**                  | `object`           |
| **Required**              | No                 |
| **Additional properties** | Not allowed        |
| **Defined in**            | #/$defs/repository |

**Description:** A project repository.

| Property                                                        | Pattern | Type           | Deprecated | Definition | Title/Description               |
| --------------------------------------------------------------- | ------- | -------------- | ---------- | ---------- | ------------------------------- |
| - [changelog](#repositories_items_changelog )                   | No      | string or null | No         | -          | Link to the changelog.          |
| - [code_of_conduct](#repositories_items_code_of_conduct )       | No      | string or null | No         | -          | Link to the code of conduct.    |
| - [contribution_guide](#repositories_items_contribution_guide ) | No      | string or null | No         | -          | Link to the contribution guide. |
| - [description](#repositories_items_description )               | No      | string         | No         | -          | Repository description.         |
| - [name](#repositories_items_name )                             | No      | string         | No         | -          | Repository name.                |
| + [url](#repositories_items_url )                               | No      | string         | No         | -          | The repository URL.             |

#### <a name="repositories_items_changelog"></a>13.1.1. Property `OWASP Project > repositories > Repository > changelog`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** Link to the changelog.

#### <a name="repositories_items_code_of_conduct"></a>13.1.2. Property `OWASP Project > repositories > Repository > code_of_conduct`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** Link to the code of conduct.

#### <a name="repositories_items_contribution_guide"></a>13.1.3. Property `OWASP Project > repositories > Repository > contribution_guide`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** Link to the contribution guide.

#### <a name="repositories_items_description"></a>13.1.4. Property `OWASP Project > repositories > Repository > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Repository description.

#### <a name="repositories_items_name"></a>13.1.5. Property `OWASP Project > repositories > Repository > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Repository name.

#### <a name="repositories_items_url"></a>13.1.6. Property `OWASP Project > repositories > Repository > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The repository URL.

## <a name="sponsors"></a>14. Property `OWASP Project > sponsors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Sponsors of the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description        |
| ------------------------------- | ------------------ |
| [Sponsor](#sponsors_items)      | A project sponsor. |

### <a name="sponsors_items"></a>14.1. OWASP Project > sponsors > Sponsor

**Title:** Sponsor

|                           |                 |
| ------------------------- | --------------- |
| **Type**                  | `object`        |
| **Required**              | No              |
| **Additional properties** | Not allowed     |
| **Defined in**            | #/$defs/sponsor |

**Description:** A project sponsor.

| Property                                      | Pattern | Type   | Deprecated | Definition | Title/Description                        |
| --------------------------------------------- | ------- | ------ | ---------- | ---------- | ---------------------------------------- |
| - [description](#sponsors_items_description ) | No      | string | No         | -          | A brief description of the sponsor.      |
| - [logo](#sponsors_items_logo )               | No      | string | No         | -          | The URL of the sponsor's logo.           |
| + [name](#sponsors_items_name )               | No      | string | No         | -          | The name of the sponsor or organization. |
| + [url](#sponsors_items_url )                 | No      | string | No         | -          | The URL of the sponsor.                  |

#### <a name="sponsors_items_description"></a>14.1.1. Property `OWASP Project > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor.

#### <a name="sponsors_items_logo"></a>14.1.2. Property `OWASP Project > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo.

#### <a name="sponsors_items_name"></a>14.1.3. Property `OWASP Project > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization.

#### <a name="sponsors_items_url"></a>14.1.4. Property `OWASP Project > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>15. Property `OWASP Project > tags`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

**Description:** Tags for the project

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 3                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [tags items](#tags_items)       | -           |

### <a name="tags_items"></a>15.1. OWASP Project > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="type"></a>16. Property `OWASP Project > type`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The type of the project: code, documentation or tool.

Must be one of:
* "code"
* "documentation"
* "tool"

## <a name="website"></a>17. Property `OWASP Project > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `url`    |

**Description:** The official website of the project.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 4 |

----------------------------------------------------------------------------------------------------------------------------
Generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans) on 2025-02-15 at 23:28:38 +0530
