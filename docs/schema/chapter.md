# OWASP Chapter

- [1. Property `OWASP Chapter > blog`](#blog)
- [2. Property `OWASP Chapter > community`](#community)
  - [2.1. OWASP Chapter > community > Community](#community_items)
    - [2.1.1. Property `OWASP Chapter > community > Community > description`](#community_items_description)
    - [2.1.2. Property `OWASP Chapter > community > Community > platform`](#community_items_platform)
    - [2.1.3. Property `OWASP Chapter > community > Community > url`](#community_items_url)
- [3. Property `OWASP Chapter > country`](#country)
- [4. Property `OWASP Chapter > events`](#events)
  - [4.1. OWASP Chapter > events > events items](#events_items)
- [5. Property `OWASP Chapter > leaders`](#leaders)
  - [5.1. OWASP Chapter > leaders > Person](#leaders_items)
    - [5.1.1. Property `OWASP Chapter > leaders > Person > email`](#leaders_items_email)
    - [5.1.2. Property `OWASP Chapter > leaders > Person > github`](#leaders_items_github)
    - [5.1.3. Property `OWASP Chapter > leaders > Person > name`](#leaders_items_name)
    - [5.1.4. Property `OWASP Chapter > leaders > Person > slack`](#leaders_items_slack)
- [6. Property `OWASP Chapter > logo`](#logo)
  - [6.1. OWASP Chapter > logo > logo](#logo_items)
    - [6.1.1. Property `OWASP Chapter > logo > logo items > small`](#logo_items_small)
    - [6.1.2. Property `OWASP Chapter > logo > logo items > medium`](#logo_items_medium)
    - [6.1.3. Property `OWASP Chapter > logo > logo items > large`](#logo_items_large)
- [7. Property `OWASP Chapter > meetup-group`](#meetup-group)
- [8. Property `OWASP Chapter > name`](#name)
- [9. Property `OWASP Chapter > region`](#region)
- [10. Property `OWASP Chapter > social_media`](#social_media)
  - [10.1. OWASP Chapter > social_media > social_media](#social_media_items)
    - [10.1.1. Property `OWASP Chapter > social_media > social_media items > description`](#social_media_items_description)
    - [10.1.2. Property `OWASP Chapter > social_media > social_media items > platform`](#social_media_items_platform)
    - [10.1.3. Property `OWASP Chapter > social_media > social_media items > url`](#social_media_items_url)
- [11. Property `OWASP Chapter > sponsors`](#sponsors)
  - [11.1. OWASP Chapter > sponsors > Sponsor](#sponsors_items)
    - [11.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`](#sponsors_items_description)
    - [11.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [11.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`](#sponsors_items_name)
    - [11.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`](#sponsors_items_url)
- [12. Property `OWASP Chapter > tags`](#tags)
  - [12.1. OWASP Chapter > tags > tags items](#tags_items)
- [13. Property `OWASP Chapter > website`](#website)

**Title:** OWASP Chapter

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP chapter schema.

| Property                         | Pattern | Type            | Deprecated | Definition | Title/Description                                          |
| -------------------------------- | ------- | --------------- | ---------- | ---------- | ---------------------------------------------------------- |
| - [blog](#blog )                 | No      | string          | No         | -          | Chapter's blog.                                            |
| - [community](#community )       | No      | array           | No         | -          | A list of community platforms associated with the chapter. |
| + [country](#country )           | No      | string          | No         | -          | Country.                                                   |
| - [events](#events )             | No      | array of string | No         | -          | Event URLs related to the chapter.                         |
| + [leaders](#leaders )           | No      | array           | No         | -          | Leaders of the chapter.                                    |
| - [logo](#logo )                 | No      | array           | No         | -          | Logo for the chapter.                                      |
| - [meetup-group](#meetup-group ) | No      | string          | No         | -          | Meetup group.                                              |
| + [name](#name )                 | No      | string          | No         | -          | The unique name of the chapter.                            |
| - [region](#region )             | No      | string          | No         | -          | Region.                                                    |
| - [social_media](#social_media ) | No      | array           | No         | -          | Social media information for the chapter.                  |
| - [sponsors](#sponsors )         | No      | array           | No         | -          | Sponsors of the chapter.                                   |
| + [tags](#tags )                 | No      | array of string | No         | -          | Tags for the chapter                                       |
| - [website](#website )           | No      | string          | No         | -          | The official website of the chapter.                       |

## <a name="blog"></a>1. Property `OWASP Chapter > blog`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** Chapter's blog.

## <a name="community"></a>2. Property `OWASP Chapter > community`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** A list of community platforms associated with the chapter.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description          |
| ------------------------------- | -------------------- |
| [Community](#community_items)   | A chapter community. |

### <a name="community_items"></a>2.1. OWASP Chapter > community > Community

**Title:** Community

|                           |                   |
| ------------------------- | ----------------- |
| **Type**                  | `object`          |
| **Required**              | No                |
| **Additional properties** | Not allowed       |
| **Defined in**            | #/$defs/community |

**Description:** A chapter community.

| Property                                       | Pattern | Type             | Deprecated | Definition | Title/Description                     |
| ---------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ------------------------------------- |
| - [description](#community_items_description ) | No      | string           | No         | -          | A brief description of the community. |
| + [platform](#community_items_platform )       | No      | enum (of string) | No         | -          | The platform used by the community.   |
| + [url](#community_items_url )                 | No      | string           | No         | -          | The URL of the community.             |

#### <a name="community_items_description"></a>2.1.1. Property `OWASP Chapter > community > Community > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the community.

#### <a name="community_items_platform"></a>2.1.2. Property `OWASP Chapter > community > Community > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The platform used by the community.

Must be one of:
* "discord"
* "slack"

#### <a name="community_items_url"></a>2.1.3. Property `OWASP Chapter > community > Community > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the community.

## <a name="country"></a>3. Property `OWASP Chapter > country`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Country.

## <a name="events"></a>4. Property `OWASP Chapter > events`

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

### <a name="events_items"></a>4.1. OWASP Chapter > events > events items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

## <a name="leaders"></a>5. Property `OWASP Chapter > leaders`

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

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Person](#leaders_items)        | Person      |

### <a name="leaders_items"></a>5.1. OWASP Chapter > leaders > Person

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

#### <a name="leaders_items_email"></a>5.1.1. Property `OWASP Chapter > leaders > Person > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

#### <a name="leaders_items_github"></a>5.1.2. Property `OWASP Chapter > leaders > Person > github`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** GitHub username

| Restrictions                      |                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9-]{1,39}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9-%5D%7B1%2C39%7D%24) |

#### <a name="leaders_items_name"></a>5.1.3. Property `OWASP Chapter > leaders > Person > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Full name

#### <a name="leaders_items_slack"></a>5.1.4. Property `OWASP Chapter > leaders > Person > slack`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Slack username

| Restrictions                      |                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9._-]{1,21}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9._-%5D%7B1%2C21%7D%24) |

## <a name="logo"></a>6. Property `OWASP Chapter > logo`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Logo for the chapter.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description            |
| ------------------------------- | ---------------------- |
| [logo](#logo_items)             | A logo for the chapter |

### <a name="logo_items"></a>6.1. OWASP Chapter > logo > logo

|                           |              |
| ------------------------- | ------------ |
| **Type**                  | `object`     |
| **Required**              | No           |
| **Additional properties** | Not allowed  |
| **Defined in**            | #/$defs/logo |

**Description:** A logo for the chapter

| Property                        | Pattern | Type   | Deprecated | Definition | Title/Description                   |
| ------------------------------- | ------- | ------ | ---------- | ---------- | ----------------------------------- |
| + [small](#logo_items_small )   | No      | string | No         | -          | Logo size should be 192x192 pixels. |
| + [medium](#logo_items_medium ) | No      | string | No         | -          | Logo size should be 256x256 pixels. |
| + [large](#logo_items_large )   | No      | string | No         | -          | Logo size should be 512x512 pixels. |

#### <a name="logo_items_small"></a>6.1.1. Property `OWASP Chapter > logo > logo items > small`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 192x192 pixels.

#### <a name="logo_items_medium"></a>6.1.2. Property `OWASP Chapter > logo > logo items > medium`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 256x256 pixels.

#### <a name="logo_items_large"></a>6.1.3. Property `OWASP Chapter > logo > logo items > large`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 512x512 pixels.

## <a name="meetup-group"></a>7. Property `OWASP Chapter > meetup-group`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Meetup group.

## <a name="name"></a>8. Property `OWASP Chapter > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of the chapter.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="region"></a>9. Property `OWASP Chapter > region`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Region.

## <a name="social_media"></a>10. Property `OWASP Chapter > social_media`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Social media information for the chapter.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description                             |
| ----------------------------------- | --------------------------------------- |
| [social_media](#social_media_items) | A social media platform for the project |

### <a name="social_media_items"></a>10.1. OWASP Chapter > social_media > social_media

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

#### <a name="social_media_items_description"></a>10.1.1. Property `OWASP Chapter > social_media > social_media items > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of the social media platform

#### <a name="social_media_items_platform"></a>10.1.2. Property `OWASP Chapter > social_media > social_media items > platform`

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

#### <a name="social_media_items_url"></a>10.1.3. Property `OWASP Chapter > social_media > social_media items > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the social media profile.

## <a name="sponsors"></a>11. Property `OWASP Chapter > sponsors`

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

### <a name="sponsors_items"></a>11.1. OWASP Chapter > sponsors > Sponsor

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

#### <a name="sponsors_items_description"></a>11.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor.

#### <a name="sponsors_items_logo"></a>11.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo.

#### <a name="sponsors_items_name"></a>11.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization.

#### <a name="sponsors_items_url"></a>11.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>12. Property `OWASP Chapter > tags`

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

### <a name="tags_items"></a>12.1. OWASP Chapter > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="website"></a>13. Property `OWASP Chapter > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `url`    |

**Description:** The official website of the chapter.

----------------------------------------------------------------------------------------------------------------------------
