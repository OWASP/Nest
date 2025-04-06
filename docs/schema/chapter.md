# OWASP Chapter

- [1. Property `OWASP Chapter > blog`](#blog)
- [2. Property `OWASP Chapter > community`](#community)
  - [2.1. OWASP Chapter > community > Community](#community_items)
    - [2.1.1. Property `OWASP Chapter > community > Community > description`](#community_items_description)
    - [2.1.2. Property `OWASP Chapter > community > Community > platform`](#community_items_platform)
    - [2.1.3. Property `OWASP Chapter > community > Community > url`](#community_items_url)
- [3. Property `OWASP Chapter > country`](#country)
- [4. Property `OWASP Chapter > events`](#events)
  - [4.1. OWASP Chapter > events > Event](#events_items)
    - [4.1.1. Property `OWASP Chapter > events > Event > description`](#events_items_description)
    - [4.1.2. Property `OWASP Chapter > events > Event > title`](#events_items_title)
    - [4.1.3. Property `OWASP Chapter > events > Event > url`](#events_items_url)
- [5. Property `OWASP Chapter > leaders`](#leaders)
  - [5.1. OWASP Chapter > leaders > Person](#leaders_items)
    - [5.1.1. Property `OWASP Chapter > leaders > Person > email`](#leaders_items_email)
    - [5.1.2. Property `OWASP Chapter > leaders > Person > github`](#leaders_items_github)
    - [5.1.3. Property `OWASP Chapter > leaders > Person > name`](#leaders_items_name)
    - [5.1.4. Property `OWASP Chapter > leaders > Person > slack`](#leaders_items_slack)
- [6. Property `OWASP Chapter > logo`](#logo)
  - [6.1. OWASP Chapter > logo > Logo](#logo_items)
    - [6.1.1. Property `OWASP Chapter > logo > Logo > small`](#logo_items_small)
    - [6.1.2. Property `OWASP Chapter > logo > Logo > medium`](#logo_items_medium)
    - [6.1.3. Property `OWASP Chapter > logo > Logo > large`](#logo_items_large)
- [7. Property `OWASP Chapter > mailing_list`](#mailing_list)
  - [7.1. OWASP Chapter > mailing_list > Mailing List](#mailing_list_items)
    - [7.1.1. Property `OWASP Chapter > mailing_list > Mailing List > description`](#mailing_list_items_description)
    - [7.1.2. Property `OWASP Chapter > mailing_list > Mailing List > email`](#mailing_list_items_email)
    - [7.1.3. Property `OWASP Chapter > mailing_list > Mailing List > title`](#mailing_list_items_title)
    - [7.1.4. Property `OWASP Chapter > mailing_list > Mailing List > url`](#mailing_list_items_url)
- [8. Property `OWASP Chapter > meetup_group`](#meetup_group)
- [9. Property `OWASP Chapter > name`](#name)
- [10. Property `OWASP Chapter > region`](#region)
- [11. Property `OWASP Chapter > social_media`](#social_media)
  - [11.1. OWASP Chapter > social_media > Social media](#social_media_items)
    - [11.1.1. Property `OWASP Chapter > social_media > Social media > description`](#social_media_items_description)
    - [11.1.2. Property `OWASP Chapter > social_media > Social media > platform`](#social_media_items_platform)
    - [11.1.3. Property `OWASP Chapter > social_media > Social media > url`](#social_media_items_url)
- [12. Property `OWASP Chapter > sponsors`](#sponsors)
  - [12.1. OWASP Chapter > sponsors > Sponsor](#sponsors_items)
    - [12.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`](#sponsors_items_description)
    - [12.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [12.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`](#sponsors_items_name)
    - [12.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`](#sponsors_items_url)
- [13. Property `OWASP Chapter > tags`](#tags)
  - [13.1. OWASP Chapter > tags > tags items](#tags_items)
- [14. Property `OWASP Chapter > website`](#website)

**Title:** OWASP Chapter

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP chapter schema

| Property                         | Pattern | Type            | Deprecated | Definition | Title/Description                                          |
| -------------------------------- | ------- | --------------- | ---------- | ---------- | ---------------------------------------------------------- |
| - [blog](#blog )                 | No      | string          | No         | -          | Chapter's blog.                                            |
| - [community](#community )       | No      | array           | No         | -          | A list of community platforms associated with the chapter. |
| + [country](#country )           | No      | string          | No         | -          | Country.                                                   |
| - [events](#events )             | No      | array           | No         | -          | Events related to the project.                             |
| + [leaders](#leaders )           | No      | array           | No         | -          | Leaders of the chapter.                                    |
| - [logo](#logo )                 | No      | array           | No         | -          | Logo for the chapter.                                      |
| - [mailing_list](#mailing_list ) | No      | array           | No         | -          | The optional mailing list associated with the chapter.     |
| - [meetup_group](#meetup_group ) | No      | string          | No         | -          | Meetup group.                                              |
| + [name](#name )                 | No      | string          | No         | -          | The unique name of chapter.                                |
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

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Community](#community_items)   | Community   |

### <a name="community_items"></a>2.1. OWASP Chapter > community > Community

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

#### <a name="community_items_description"></a>2.1.1. Property `OWASP Chapter > community > Community > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the community.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="community_items_platform"></a>2.1.2. Property `OWASP Chapter > community > Community > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The platform used by the community

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

| Restrictions   |   |
| -------------- | - |
| **Min length** | 1 |

## <a name="events"></a>4. Property `OWASP Chapter > events`

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

### <a name="events_items"></a>4.1. OWASP Chapter > events > Event

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

#### <a name="events_items_description"></a>4.1.1. Property `OWASP Chapter > events > Event > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_title"></a>4.1.2. Property `OWASP Chapter > events > Event > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of the event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_url"></a>4.1.3. Property `OWASP Chapter > events > Event > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL of the event

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

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

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

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

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
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [Logo](#logo_items)             | A logo      |

### <a name="logo_items"></a>6.1. OWASP Chapter > logo > Logo

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

#### <a name="logo_items_small"></a>6.1.1. Property `OWASP Chapter > logo > Logo > small`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 192x192 pixels.

#### <a name="logo_items_medium"></a>6.1.2. Property `OWASP Chapter > logo > Logo > medium`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 256x256 pixels.

#### <a name="logo_items_large"></a>6.1.3. Property `OWASP Chapter > logo > Logo > large`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 512x512 pixels.

## <a name="mailing_list"></a>7. Property `OWASP Chapter > mailing_list`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** The optional mailing list associated with the chapter.

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

### <a name="mailing_list_items"></a>7.1. OWASP Chapter > mailing_list > Mailing List

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

#### <a name="mailing_list_items_description"></a>7.1.1. Property `OWASP Chapter > mailing_list > Mailing List > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_email"></a>7.1.2. Property `OWASP Chapter > mailing_list > Mailing List > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="mailing_list_items_title"></a>7.1.3. Property `OWASP Chapter > mailing_list > Mailing List > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_url"></a>7.1.4. Property `OWASP Chapter > mailing_list > Mailing List > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL to mailing list

## <a name="meetup_group"></a>8. Property `OWASP Chapter > meetup_group`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Meetup group.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 1 |

## <a name="name"></a>9. Property `OWASP Chapter > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of chapter.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

## <a name="region"></a>10. Property `OWASP Chapter > region`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Region.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 1 |

## <a name="social_media"></a>11. Property `OWASP Chapter > social_media`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Social media information for the chapter.

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

### <a name="social_media_items"></a>11.1. OWASP Chapter > social_media > Social media

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

#### <a name="social_media_items_description"></a>11.1.1. Property `OWASP Chapter > social_media > Social media > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of the social media platform

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="social_media_items_platform"></a>11.1.2. Property `OWASP Chapter > social_media > Social media > platform`

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

#### <a name="social_media_items_url"></a>11.1.3. Property `OWASP Chapter > social_media > Social media > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the social media profile.

## <a name="sponsors"></a>12. Property `OWASP Chapter > sponsors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Sponsors of the chapter.

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

### <a name="sponsors_items"></a>12.1. OWASP Chapter > sponsors > Sponsor

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

#### <a name="sponsors_items_description"></a>12.1.1. Property `OWASP Chapter > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_logo"></a>12.1.2. Property `OWASP Chapter > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo

#### <a name="sponsors_items_name"></a>12.1.3. Property `OWASP Chapter > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_url"></a>12.1.4. Property `OWASP Chapter > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>13. Property `OWASP Chapter > tags`

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

### <a name="tags_items"></a>13.1. OWASP Chapter > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="website"></a>14. Property `OWASP Chapter > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The official website of the chapter.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 4 |

----------------------------------------------------------------------------------------------------------------------------
