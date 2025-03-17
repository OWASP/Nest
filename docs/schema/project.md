# OWASP Project

- [1. Property `OWASP Project > audience`](#audience)
- [2. Property `OWASP Project > blog`](#blog)
- [3. Property `OWASP Project > community`](#community)
  - [3.1. OWASP Project > community > Community](#community_items)
    - [3.1.1. Property `OWASP Project > community > Community > description`](#community_items_description)
    - [3.1.2. Property `OWASP Project > community > Community > platform`](#community_items_platform)
    - [3.1.3. Property `OWASP Project > community > Community > url`](#community_items_url)
- [4. Property `OWASP Project > demo`](#demo)
  - [4.1. OWASP Project > demo > demo items](#demo_items)
- [5. Property `OWASP Project > documentation`](#documentation)
  - [5.1. OWASP Project > documentation > documentation items](#documentation_items)
- [6. Property `OWASP Project > downloads`](#downloads)
  - [6.1. OWASP Project > downloads > downloads items](#downloads_items)
- [7. Property `OWASP Project > events`](#events)
  - [7.1. OWASP Project > events > Event](#events_items)
    - [7.1.1. Property `OWASP Project > events > Event > description`](#events_items_description)
    - [7.1.2. Property `OWASP Project > events > Event > title`](#events_items_title)
    - [7.1.3. Property `OWASP Project > events > Event > url`](#events_items_url)
- [8. Property `OWASP Project > leaders`](#leaders)
  - [8.1. OWASP Project > leaders > Person](#leaders_items)
    - [8.1.1. Property `OWASP Project > leaders > Person > email`](#leaders_items_email)
    - [8.1.2. Property `OWASP Project > leaders > Person > github`](#leaders_items_github)
    - [8.1.3. Property `OWASP Project > leaders > Person > name`](#leaders_items_name)
    - [8.1.4. Property `OWASP Project > leaders > Person > slack`](#leaders_items_slack)
- [9. Property `OWASP Project > level`](#level)
- [10. Property `OWASP Project > license`](#license)
- [11. Property `OWASP Project > logo`](#logo)
  - [11.1. OWASP Project > logo > Logo](#logo_items)
    - [11.1.1. Property `OWASP Project > logo > Logo > small`](#logo_items_small)
    - [11.1.2. Property `OWASP Project > logo > Logo > medium`](#logo_items_medium)
    - [11.1.3. Property `OWASP Project > logo > Logo > large`](#logo_items_large)
- [12. Property `OWASP Project > mailing_list`](#mailing_list)
  - [12.1. OWASP Project > mailing_list > Mailing List](#mailing_list_items)
    - [12.1.1. Property `OWASP Project > mailing_list > Mailing List > description`](#mailing_list_items_description)
    - [12.1.2. Property `OWASP Project > mailing_list > Mailing List > email`](#mailing_list_items_email)
    - [12.1.3. Property `OWASP Project > mailing_list > Mailing List > title`](#mailing_list_items_title)
    - [12.1.4. Property `OWASP Project > mailing_list > Mailing List > url`](#mailing_list_items_url)
- [13. Property `OWASP Project > name`](#name)
- [14. Property `OWASP Project > pitch`](#pitch)
- [15. Property `OWASP Project > repositories`](#repositories)
  - [15.1. OWASP Project > repositories > Repository](#repositories_items)
    - [15.1.1. Property `OWASP Project > repositories > Repository > changelog`](#repositories_items_changelog)
    - [15.1.2. Property `OWASP Project > repositories > Repository > code_of_conduct`](#repositories_items_code_of_conduct)
    - [15.1.3. Property `OWASP Project > repositories > Repository > contribution_guide`](#repositories_items_contribution_guide)
    - [15.1.4. Property `OWASP Project > repositories > Repository > description`](#repositories_items_description)
    - [15.1.5. Property `OWASP Project > repositories > Repository > name`](#repositories_items_name)
    - [15.1.6. Property `OWASP Project > repositories > Repository > url`](#repositories_items_url)
- [16. Property `OWASP Project > social_media`](#social_media)
  - [16.1. OWASP Project > social_media > Social media](#social_media_items)
    - [16.1.1. Property `OWASP Project > social_media > Social media > description`](#social_media_items_description)
    - [16.1.2. Property `OWASP Project > social_media > Social media > platform`](#social_media_items_platform)
    - [16.1.3. Property `OWASP Project > social_media > Social media > url`](#social_media_items_url)
- [17. Property `OWASP Project > sponsors`](#sponsors)
  - [17.1. OWASP Project > sponsors > Sponsor](#sponsors_items)
    - [17.1.1. Property `OWASP Project > sponsors > Sponsor > description`](#sponsors_items_description)
    - [17.1.2. Property `OWASP Project > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [17.1.3. Property `OWASP Project > sponsors > Sponsor > name`](#sponsors_items_name)
    - [17.1.4. Property `OWASP Project > sponsors > Sponsor > url`](#sponsors_items_url)
- [18. Property `OWASP Project > tags`](#tags)
  - [18.1. OWASP Project > tags > tags items](#tags_items)
- [19. Property `OWASP Project > type`](#type)
- [20. Property `OWASP Project > website`](#website)

**Title:** OWASP Project

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP project schema

| Property                           | Pattern | Type                        | Deprecated | Definition | Title/Description                                          |
| ---------------------------------- | ------- | --------------------------- | ---------- | ---------- | ---------------------------------------------------------- |
| + [audience](#audience )           | No      | enum (of string)            | No         | -          | The intended audience for the project.                     |
| - [blog](#blog )                   | No      | string                      | No         | -          | Project's blog.                                            |
| - [community](#community )         | No      | array                       | No         | -          | A list of community platforms associated with the project. |
| - [demo](#demo )                   | No      | array of string             | No         | -          | Optional URLs to the project demo.                         |
| - [documentation](#documentation ) | No      | array of string             | No         | -          | Optional URLs to project documentation.                    |
| - [downloads](#downloads )         | No      | array of string             | No         | -          | Optional list of download URLs.                            |
| - [events](#events )               | No      | array                       | No         | -          | Events related to the project.                             |
| + [leaders](#leaders )             | No      | array                       | No         | -          | Leaders of the project.                                    |
| + [level](#level )                 | No      | enum (of integer or number) | No         | -          | Project level.                                             |
| - [license](#license )             | No      | enum (of string)            | No         | -          | The license of the project.                                |
| - [logo](#logo )                   | No      | array                       | No         | -          | Logo information for the project.                          |
| - [mailing_list](#mailing_list )   | No      | array                       | No         | -          | The optional mailing list associated with the project.     |
| + [name](#name )                   | No      | string                      | No         | -          | The unique name of the project.                            |
| + [pitch](#pitch )                 | No      | string                      | No         | -          | The project pitch.                                         |
| - [repositories](#repositories )   | No      | array                       | No         | -          | Repositories associated with the project.                  |
| - [social_media](#social_media )   | No      | array                       | No         | -          | Social media information for the project                   |
| - [sponsors](#sponsors )           | No      | array                       | No         | -          | Sponsors of the project.                                   |
| + [tags](#tags )                   | No      | array of string             | No         | -          | Tags for the project                                       |
| + [type](#type )                   | No      | enum (of string)            | No         | -          | The type of the project: code, documentation or tool.      |
| - [website](#website )             | No      | string                      | No         | -          | The official website of the project.                       |

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

## <a name="community"></a>3. Property `OWASP Project > community`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** A list of community platforms associated with the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Community](#community_items)   | Community   |

### <a name="community_items"></a>3.1. OWASP Project > community > Community

**Title:** Community

|                           |                                    |
| ------------------------- | ---------------------------------- |
| **Type**                  | `object`                           |
| **Required**              | No                                 |
| **Additional properties** | Not allowed                        |
| **Defined in**            | common.json#/definitions/community |

**Description:** Community

| Property                                       | Pattern | Type             | Deprecated | Definition | Title/Description                     |
| ---------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ------------------------------------- |
| - [description](#community_items_description ) | No      | string           | No         | -          | A brief description of the community. |
| + [platform](#community_items_platform )       | No      | enum (of string) | No         | -          | The platform used by the community    |
| + [url](#community_items_url )                 | No      | string           | No         | -          | The URL of the community.             |

#### <a name="community_items_description"></a>3.1.1. Property `OWASP Project > community > Community > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the community.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="community_items_platform"></a>3.1.2. Property `OWASP Project > community > Community > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The platform used by the community

Must be one of:
* "discord"
* "slack"

#### <a name="community_items_url"></a>3.1.3. Property `OWASP Project > community > Community > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the community.

## <a name="demo"></a>4. Property `OWASP Project > demo`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Optional URLs to the project demo.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [demo items](#demo_items)       | -           |

### <a name="demo_items"></a>4.1. OWASP Project > demo > demo items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="documentation"></a>5. Property `OWASP Project > documentation`

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

### <a name="documentation_items"></a>5.1. OWASP Project > documentation > documentation items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="downloads"></a>6. Property `OWASP Project > downloads`

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

### <a name="downloads_items"></a>6.1. OWASP Project > downloads > downloads items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="events"></a>7. Property `OWASP Project > events`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Events related to the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Event](#events_items)          | Event       |

### <a name="events_items"></a>7.1. OWASP Project > events > Event

**Title:** Event

|                           |                                |
| ------------------------- | ------------------------------ |
| **Type**                  | `object`                       |
| **Required**              | No                             |
| **Additional properties** | Not allowed                    |
| **Defined in**            | common.json#/definitions/event |

**Description:** Event

| Property                                    | Pattern | Type   | Deprecated | Definition | Title/Description            |
| ------------------------------------------- | ------- | ------ | ---------- | ---------- | ---------------------------- |
| - [description](#events_items_description ) | No      | string | No         | -          | A brief description of event |
| - [title](#events_items_title )             | No      | string | No         | -          | Title of the event           |
| + [url](#events_items_url )                 | No      | string | No         | -          | URL of the event             |

#### <a name="events_items_description"></a>7.1.1. Property `OWASP Project > events > Event > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_title"></a>7.1.2. Property `OWASP Project > events > Event > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of the event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_url"></a>7.1.3. Property `OWASP Project > events > Event > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL of the event

## <a name="leaders"></a>8. Property `OWASP Project > leaders`

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

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Person](#leaders_items)        | Person      |

### <a name="leaders_items"></a>8.1. OWASP Project > leaders > Person

**Title:** Person

|                           |                                 |
| ------------------------- | ------------------------------- |
| **Type**                  | `object`                        |
| **Required**              | No                              |
| **Additional properties** | Not allowed                     |
| **Defined in**            | common.json#/definitions/person |

**Description:** Person

| Property                           | Pattern | Type   | Deprecated | Definition | Title/Description |
| ---------------------------------- | ------- | ------ | ---------- | ---------- | ----------------- |
| - [email](#leaders_items_email )   | No      | string | No         | -          | E-mail address    |
| + [github](#leaders_items_github ) | No      | string | No         | -          | GitHub username   |
| - [name](#leaders_items_name )     | No      | string | No         | -          | Full name         |
| - [slack](#leaders_items_slack )   | No      | string | No         | -          | Slack username    |

#### <a name="leaders_items_email"></a>8.1.1. Property `OWASP Project > leaders > Person > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="leaders_items_github"></a>8.1.2. Property `OWASP Project > leaders > Person > github`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** GitHub username

| Restrictions                      |                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9-]{1,39}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9-%5D%7B1%2C39%7D%24) |

#### <a name="leaders_items_name"></a>8.1.3. Property `OWASP Project > leaders > Person > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Full name

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="leaders_items_slack"></a>8.1.4. Property `OWASP Project > leaders > Person > slack`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Slack username

| Restrictions                      |                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9._-]{1,21}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9._-%5D%7B1%2C21%7D%24) |

## <a name="level"></a>9. Property `OWASP Project > level`

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

## <a name="license"></a>10. Property `OWASP Project > license`

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

## <a name="logo"></a>11. Property `OWASP Project > logo`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Logo information for the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Logo](#logo_items)             | A logo      |

### <a name="logo_items"></a>11.1. OWASP Project > logo > Logo

**Title:** Logo

|                           |                               |
| ------------------------- | ----------------------------- |
| **Type**                  | `object`                      |
| **Required**              | No                            |
| **Additional properties** | Not allowed                   |
| **Defined in**            | common.json#/definitions/logo |

**Description:** A logo

| Property                        | Pattern | Type   | Deprecated | Definition | Title/Description                   |
| ------------------------------- | ------- | ------ | ---------- | ---------- | ----------------------------------- |
| + [small](#logo_items_small )   | No      | string | No         | -          | Logo size should be 192x192 pixels. |
| + [medium](#logo_items_medium ) | No      | string | No         | -          | Logo size should be 256x256 pixels. |
| + [large](#logo_items_large )   | No      | string | No         | -          | Logo size should be 512x512 pixels. |

#### <a name="logo_items_small"></a>11.1.1. Property `OWASP Project > logo > Logo > small`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 192x192 pixels.

#### <a name="logo_items_medium"></a>11.1.2. Property `OWASP Project > logo > Logo > medium`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 256x256 pixels.

#### <a name="logo_items_large"></a>11.1.3. Property `OWASP Project > logo > Logo > large`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 512x512 pixels.

## <a name="mailing_list"></a>12. Property `OWASP Project > mailing_list`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** The optional mailing list associated with the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description |
| ----------------------------------- | ----------- |
| [Mailing List](#mailing_list_items) | Mail List   |

### <a name="mailing_list_items"></a>12.1. OWASP Project > mailing_list > Mailing List

**Title:** Mailing List

|                           |                                       |
| ------------------------- | ------------------------------------- |
| **Type**                  | `object`                              |
| **Required**              | No                                    |
| **Additional properties** | Not allowed                           |
| **Defined in**            | common.json#/definitions/mailing_list |

**Description:** Mail List

| Property                                          | Pattern | Type   | Deprecated | Definition | Title/Description           |
| ------------------------------------------------- | ------- | ------ | ---------- | ---------- | --------------------------- |
| - [description](#mailing_list_items_description ) | No      | string | No         | -          | Description of mailing list |
| - [email](#mailing_list_items_email )             | No      | string | No         | -          | E-mail address              |
| - [title](#mailing_list_items_title )             | No      | string | No         | -          | Title of mailing list       |
| + [url](#mailing_list_items_url )                 | No      | string | No         | -          | URL to mailing list         |

#### <a name="mailing_list_items_description"></a>12.1.1. Property `OWASP Project > mailing_list > Mailing List > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_email"></a>12.1.2. Property `OWASP Project > mailing_list > Mailing List > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="mailing_list_items_title"></a>12.1.3. Property `OWASP Project > mailing_list > Mailing List > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_url"></a>12.1.4. Property `OWASP Project > mailing_list > Mailing List > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL to mailing list

## <a name="name"></a>13. Property `OWASP Project > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of the project.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="pitch"></a>14. Property `OWASP Project > pitch`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The project pitch.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="repositories"></a>15. Property `OWASP Project > repositories`

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

| Each item of this array must be   | Description  |
| --------------------------------- | ------------ |
| [Repository](#repositories_items) | A repository |

### <a name="repositories_items"></a>15.1. OWASP Project > repositories > Repository

**Title:** Repository

|                           |                                     |
| ------------------------- | ----------------------------------- |
| **Type**                  | `object`                            |
| **Required**              | No                                  |
| **Additional properties** | Not allowed                         |
| **Defined in**            | common.json#/definitions/repository |

**Description:** A repository

| Property                                                        | Pattern | Type   | Deprecated | Definition | Title/Description              |
| --------------------------------------------------------------- | ------- | ------ | ---------- | ---------- | ------------------------------ |
| - [changelog](#repositories_items_changelog )                   | No      | string | No         | -          | Link to the changelog          |
| - [code_of_conduct](#repositories_items_code_of_conduct )       | No      | string | No         | -          | Link to the code of conduct    |
| - [contribution_guide](#repositories_items_contribution_guide ) | No      | string | No         | -          | Link to the contribution guide |
| - [description](#repositories_items_description )               | No      | string | No         | -          | Repository description         |
| - [name](#repositories_items_name )                             | No      | string | No         | -          | Repository name                |
| + [url](#repositories_items_url )                               | No      | string | No         | -          | The repository URL.            |

#### <a name="repositories_items_changelog"></a>15.1.1. Property `OWASP Project > repositories > Repository > changelog`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Link to the changelog

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="repositories_items_code_of_conduct"></a>15.1.2. Property `OWASP Project > repositories > Repository > code_of_conduct`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Link to the code of conduct

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="repositories_items_contribution_guide"></a>15.1.3. Property `OWASP Project > repositories > Repository > contribution_guide`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Link to the contribution guide

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="repositories_items_description"></a>15.1.4. Property `OWASP Project > repositories > Repository > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Repository description

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="repositories_items_name"></a>15.1.5. Property `OWASP Project > repositories > Repository > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Repository name

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="repositories_items_url"></a>15.1.6. Property `OWASP Project > repositories > Repository > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The repository URL.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

## <a name="social_media"></a>16. Property `OWASP Project > social_media`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Social media information for the project

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description                             |
| ----------------------------------- | --------------------------------------- |
| [Social media](#social_media_items) | A social media platform for the project |

### <a name="social_media_items"></a>16.1. OWASP Project > social_media > Social media

**Title:** Social media

|                           |                                       |
| ------------------------- | ------------------------------------- |
| **Type**                  | `object`                              |
| **Required**              | No                                    |
| **Additional properties** | Not allowed                           |
| **Defined in**            | common.json#/definitions/social_media |

**Description:** A social media platform for the project

| Property                                          | Pattern | Type             | Deprecated | Definition | Title/Description                        |
| ------------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ---------------------------------------- |
| - [description](#social_media_items_description ) | No      | string           | No         | -          | Description of the social media platform |
| + [platform](#social_media_items_platform )       | No      | enum (of string) | No         | -          | The type of social media platform.       |
| + [url](#social_media_items_url )                 | No      | string           | No         | -          | The URL of the social media profile.     |

#### <a name="social_media_items_description"></a>16.1.1. Property `OWASP Project > social_media > Social media > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of the social media platform

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="social_media_items_platform"></a>16.1.2. Property `OWASP Project > social_media > Social media > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The type of social media platform.

Must be one of:
* "bluesky"
* "linkedin"
* "x"
* "youtube"

#### <a name="social_media_items_url"></a>16.1.3. Property `OWASP Project > social_media > Social media > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the social media profile.

## <a name="sponsors"></a>17. Property `OWASP Project > sponsors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Sponsors of the project.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description      |
| ------------------------------- | ---------------- |
| [Sponsor](#sponsors_items)      | A sponsor entity |

### <a name="sponsors_items"></a>17.1. OWASP Project > sponsors > Sponsor

**Title:** Sponsor

|                           |                                  |
| ------------------------- | -------------------------------- |
| **Type**                  | `object`                         |
| **Required**              | No                               |
| **Additional properties** | Not allowed                      |
| **Defined in**            | common.json#/definitions/sponsor |

**Description:** A sponsor entity

| Property                                      | Pattern | Type   | Deprecated | Definition | Title/Description                       |
| --------------------------------------------- | ------- | ------ | ---------- | ---------- | --------------------------------------- |
| - [description](#sponsors_items_description ) | No      | string | No         | -          | A brief description of the sponsor      |
| - [logo](#sponsors_items_logo )               | No      | string | No         | -          | The URL of the sponsor's logo           |
| + [name](#sponsors_items_name )               | No      | string | No         | -          | The name of the sponsor or organization |
| + [url](#sponsors_items_url )                 | No      | string | No         | -          | The URL of the sponsor.                 |

#### <a name="sponsors_items_description"></a>17.1.1. Property `OWASP Project > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_logo"></a>17.1.2. Property `OWASP Project > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo

#### <a name="sponsors_items_name"></a>17.1.3. Property `OWASP Project > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_url"></a>17.1.4. Property `OWASP Project > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>18. Property `OWASP Project > tags`

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

### <a name="tags_items"></a>18.1. OWASP Project > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="type"></a>19. Property `OWASP Project > type`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The type of the project: code, documentation or tool.

Must be one of:
* "code"
* "documentation"
* "tool"

## <a name="website"></a>20. Property `OWASP Project > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The official website of the project.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 4 |

----------------------------------------------------------------------------------------------------------------------------
