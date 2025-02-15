# OWASP Chapter

- [1. Property `OWASP Chapter > blog`](#blog)
- [2. Property `OWASP Chapter > country`](#country)
- [3. Property `OWASP Chapter > events`](#events)
  - [3.1. OWASP Chapter > events > events items](#events_items)
- [4. Property `OWASP Chapter > leaders`](#leaders)
  - [4.1. OWASP Chapter > leaders > Leader](#leaders_items)
    - [4.1.1. Property `OWASP Chapter > leaders > Leader > email`](#leaders_items_email)
    - [4.1.2. Property `OWASP Chapter > leaders > Leader > github`](#leaders_items_github)
    - [4.1.3. Property `OWASP Chapter > leaders > Leader > name`](#leaders_items_name)
    - [4.1.4. Property `OWASP Chapter > leaders > Leader > slack`](#leaders_items_slack)
- [5. Property `OWASP Chapter > meetup-group`](#meetup-group)
- [6. Property `OWASP Chapter > name`](#name)
- [7. Property `OWASP Chapter > region`](#region)
- [8. Property `OWASP Chapter > sponsors`](#sponsors)
  - [8.1. OWASP Chapter > sponsors > Sponsor](#sponsors_items)
    - [8.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`](#sponsors_items_description)
    - [8.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [8.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`](#sponsors_items_name)
    - [8.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`](#sponsors_items_url)
- [9. Property `OWASP Chapter > tags`](#tags)
  - [9.1. OWASP Chapter > tags > tags items](#tags_items)
- [10. Property `OWASP Chapter > website`](#website)

**Title:** OWASP Chapter

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP chapter schema.

| Property                         | Pattern | Type            | Deprecated | Definition | Title/Description                    |
| -------------------------------- | ------- | --------------- | ---------- | ---------- | ------------------------------------ |
| - [blog](#blog )                 | No      | string          | No         | -          | Chapter's blog.                      |
| + [country](#country )           | No      | string          | No         | -          | Country.                             |
| - [events](#events )             | No      | array of string | No         | -          | Event URLs related to the chapter.   |
| + [leaders](#leaders )           | No      | array           | No         | -          | Leaders of the chapter.              |
| - [meetup-group](#meetup-group ) | No      | string          | No         | -          | Meetup group.                        |
| + [name](#name )                 | No      | string          | No         | -          | The unique name of the chapter.      |
| - [region](#region )             | No      | string          | No         | -          | Region.                              |
| - [sponsors](#sponsors )         | No      | array           | No         | -          | Sponsors of the chapter.             |
| + [tags](#tags )                 | No      | array of string | No         | -          | Tags for the chapter                 |
| - [website](#website )           | No      | string          | No         | -          | The official website of the chapter. |

## <a name="blog"></a>1. Property `OWASP Chapter > blog`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Chapter's blog.

## <a name="country"></a>2. Property `OWASP Chapter > country`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Country.

## <a name="events"></a>3. Property `OWASP Chapter > events`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Event URLs related to the chapter.

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

### <a name="events_items"></a>3.1. OWASP Chapter > events > events items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="leaders"></a>4. Property `OWASP Chapter > leaders`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

**Description:** Leaders of the chapter.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 2                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description       |
| ------------------------------- | ----------------- |
| [Leader](#leaders_items)        | A chapter leader. |

### <a name="leaders_items"></a>4.1. OWASP Chapter > leaders > Leader

**Title:** Leader

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | No             |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/leader |

**Description:** A chapter leader.

| Property                           | Pattern | Type           | Deprecated | Definition | Title/Description           |
| ---------------------------------- | ------- | -------------- | ---------- | ---------- | --------------------------- |
| - [email](#leaders_items_email )   | No      | string or null | No         | -          | The leader's email address. |
| + [github](#leaders_items_github ) | No      | string         | No         | -          | The GitHub username.        |
| - [name](#leaders_items_name )     | No      | string or null | No         | -          | Leader's name.              |
| - [slack](#leaders_items_slack )   | No      | string or null | No         | -          | The Slack username.         |

#### <a name="leaders_items_email"></a>4.1.1. Property `OWASP Chapter > leaders > Leader > email`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |
| **Format**   | `email`          |

**Description:** The leader's email address.

#### <a name="leaders_items_github"></a>4.1.2. Property `OWASP Chapter > leaders > Leader > github`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The GitHub username.

| Restrictions                      |                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9-]{1,39}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9-%5D%7B1%2C39%7D%24) |

#### <a name="leaders_items_name"></a>4.1.3. Property `OWASP Chapter > leaders > Leader > name`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** Leader's name.

#### <a name="leaders_items_slack"></a>4.1.4. Property `OWASP Chapter > leaders > Leader > slack`

|              |                  |
| ------------ | ---------------- |
| **Type**     | `string or null` |
| **Required** | No               |

**Description:** The Slack username.

| Restrictions                      |                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9._-]{1,21}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9._-%5D%7B1%2C21%7D%24) |

## <a name="meetup-group"></a>5. Property `OWASP Chapter > meetup-group`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Meetup group.

## <a name="name"></a>6. Property `OWASP Chapter > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of the chapter.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="region"></a>7. Property `OWASP Chapter > region`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Region.

## <a name="sponsors"></a>8. Property `OWASP Chapter > sponsors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Sponsors of the chapter.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description        |
| ------------------------------- | ------------------ |
| [Sponsor](#sponsors_items)      | A chapter sponsor. |

### <a name="sponsors_items"></a>8.1. OWASP Chapter > sponsors > Sponsor

**Title:** Sponsor

|                           |                 |
| ------------------------- | --------------- |
| **Type**                  | `object`        |
| **Required**              | No              |
| **Additional properties** | Not allowed     |
| **Defined in**            | #/$defs/sponsor |

**Description:** A chapter sponsor.

| Property                                      | Pattern | Type   | Deprecated | Definition | Title/Description                        |
| --------------------------------------------- | ------- | ------ | ---------- | ---------- | ---------------------------------------- |
| - [description](#sponsors_items_description ) | No      | string | No         | -          | A brief description of the sponsor.      |
| - [logo](#sponsors_items_logo )               | No      | string | No         | -          | The URL of the sponsor's logo.           |
| + [name](#sponsors_items_name )               | No      | string | No         | -          | The name of the sponsor or organization. |
| + [url](#sponsors_items_url )                 | No      | string | No         | -          | The URL of the sponsor.                  |

#### <a name="sponsors_items_description"></a>8.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor.

#### <a name="sponsors_items_logo"></a>8.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo.

#### <a name="sponsors_items_name"></a>8.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization.

#### <a name="sponsors_items_url"></a>8.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>9. Property `OWASP Chapter > tags`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

**Description:** Tags for the chapter

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

### <a name="tags_items"></a>9.1. OWASP Chapter > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="website"></a>10. Property `OWASP Chapter > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `url`    |

**Description:** The official website of the chapter.

----------------------------------------------------------------------------------------------------------------------------
Generated using [json-schema-for-humans](https://github.com/coveooss/json-schema-for-humans) on 2025-02-15 at 23:42:31 +0530
