# OWASP Committee Schema

- [1. Property `OWASP Committee Schema > community`](#community)
  - [1.1. OWASP Committee Schema > community > Community](#community_items)
    - [1.1.1. Property `OWASP Committee Schema > community > Community > description`](#community_items_description)
    - [1.1.2. Property `OWASP Committee Schema > community > Community > platform`](#community_items_platform)
    - [1.1.3. Property `OWASP Committee Schema > community > Community > url`](#community_items_url)
- [2. Property `OWASP Committee Schema > description`](#description)
- [3. Property `OWASP Committee Schema > events`](#events)
  - [3.1. OWASP Committee Schema > events > Event](#events_items)
    - [3.1.1. Property `OWASP Committee Schema > events > Event > description`](#events_items_description)
    - [3.1.2. Property `OWASP Committee Schema > events > Event > title`](#events_items_title)
    - [3.1.3. Property `OWASP Committee Schema > events > Event > url`](#events_items_url)
- [4. Property `OWASP Committee Schema > logo`](#logo)
  - [4.1. OWASP Committee Schema > logo > Logo](#logo_items)
    - [4.1.1. Property `OWASP Committee Schema > logo > Logo > small`](#logo_items_small)
    - [4.1.2. Property `OWASP Committee Schema > logo > Logo > medium`](#logo_items_medium)
    - [4.1.3. Property `OWASP Committee Schema > logo > Logo > large`](#logo_items_large)
- [5. Property `OWASP Committee Schema > mailing_list`](#mailing_list)
  - [5.1. OWASP Committee Schema > mailing_list > Mailing List](#mailing_list_items)
    - [5.1.1. Property `OWASP Committee Schema > mailing_list > Mailing List > description`](#mailing_list_items_description)
    - [5.1.2. Property `OWASP Committee Schema > mailing_list > Mailing List > email`](#mailing_list_items_email)
    - [5.1.3. Property `OWASP Committee Schema > mailing_list > Mailing List > title`](#mailing_list_items_title)
    - [5.1.4. Property `OWASP Committee Schema > mailing_list > Mailing List > url`](#mailing_list_items_url)
- [6. Property `OWASP Committee Schema > meeting_minutes`](#meeting_minutes)
  - [6.1. OWASP Committee Schema > meeting_minutes > Meeting Minutes](#meeting_minutes_items)
    - [6.1.1. Property `OWASP Committee Schema > meeting_minutes > Meeting Minutes > date`](#meeting_minutes_items_date)
    - [6.1.2. Property `OWASP Committee Schema > meeting_minutes > Meeting Minutes > url`](#meeting_minutes_items_url)
- [7. Property `OWASP Committee Schema > members`](#members)
  - [7.1. OWASP Committee Schema > members > Leader](#members_items)
    - [7.1.1. Property `OWASP Committee Schema > members > Leader > email`](#members_items_email)
    - [7.1.2. Property `OWASP Committee Schema > members > Leader > github`](#members_items_github)
    - [7.1.3. Property `OWASP Committee Schema > members > Leader > name`](#members_items_name)
    - [7.1.4. Property `OWASP Committee Schema > members > Leader > role`](#members_items_role)
    - [7.1.5. Property `OWASP Committee Schema > members > Leader > slack`](#members_items_slack)
- [8. Property `OWASP Committee Schema > name`](#name)
- [9. Property `OWASP Committee Schema > resources`](#resources)
  - [9.1. OWASP Committee Schema > resources > resources items](#resources_items)
    - [9.1.1. Property `OWASP Committee Schema > resources > resources items > title`](#resources_items_title)
    - [9.1.2. Property `OWASP Committee Schema > resources > resources items > type`](#resources_items_type)
    - [9.1.3. Property `OWASP Committee Schema > resources > resources items > url`](#resources_items_url)
- [10. Property `OWASP Committee Schema > scope`](#scope)
- [11. Property `OWASP Committee Schema > social_media`](#social_media)
  - [11.1. OWASP Committee Schema > social_media > Social media](#social_media_items)
    - [11.1.1. Property `OWASP Committee Schema > social_media > Social media > description`](#social_media_items_description)
    - [11.1.2. Property `OWASP Committee Schema > social_media > Social media > platform`](#social_media_items_platform)
    - [11.1.3. Property `OWASP Committee Schema > social_media > Social media > url`](#social_media_items_url)
- [12. Property `OWASP Committee Schema > sponsors`](#sponsors)
  - [12.1. OWASP Committee Schema > sponsors > Sponsor](#sponsors_items)
    - [12.1.1. Property `OWASP Committee Schema > sponsors > Sponsor > description`](#sponsors_items_description)
    - [12.1.2. Property `OWASP Committee Schema > sponsors > Sponsor > logo`](#sponsors_items_logo)
    - [12.1.3. Property `OWASP Committee Schema > sponsors > Sponsor > name`](#sponsors_items_name)
    - [12.1.4. Property `OWASP Committee Schema > sponsors > Sponsor > url`](#sponsors_items_url)
- [13. Property `OWASP Committee Schema > tags`](#tags)
  - [13.1. OWASP Committee Schema > tags > tags items](#tags_items)
- [14. Property `OWASP Committee Schema > website`](#website)

**Title:** OWASP Committee Schema

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** OWASP Committee Schema

| Property                               | Pattern | Type            | Deprecated | Definition | Title/Description                                      |
| -------------------------------------- | ------- | --------------- | ---------- | ---------- | ------------------------------------------------------ |
| - [community](#community )             | No      | array           | No         | -          | Community platforms associated with the committee.     |
| + [description](#description )         | No      | string          | No         | -          | Description of the committee's purpose and activities. |
| - [events](#events )                   | No      | array           | No         | -          | Events organized or sponsored by the committee.        |
| - [logo](#logo )                       | No      | array           | No         | -          | Logo information for the project.                      |
| - [mailing_list](#mailing_list )       | No      | array           | No         | -          | Mailing list associated with the committee.            |
| - [meeting_minutes](#meeting_minutes ) | No      | array           | No         | -          | Meeting minutes of the committee.                      |
| + [members](#members )                 | No      | array           | No         | -          | Members of the committee.                              |
| + [name](#name )                       | No      | string          | No         | -          | The unique name of the committee                       |
| - [resources](#resources )             | No      | array of object | No         | -          | Resources provided by the committee.                   |
| + [scope](#scope )                     | No      | string          | No         | -          | Scope and purpose of committee.                        |
| - [social_media](#social_media )       | No      | array           | No         | -          | Social media information of the committee.             |
| - [sponsors](#sponsors )               | No      | array           | No         | -          | Sponsors of the committee.                             |
| + [tags](#tags )                       | No      | array of string | No         | -          | Tags associated with the committee                     |
| - [website](#website )                 | No      | string          | No         | -          | The official website of the committee.                 |

## <a name="community"></a>1. Property `OWASP Committee Schema > community`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Community platforms associated with the committee.

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

### <a name="community_items"></a>1.1. OWASP Committee Schema > community > Community

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

#### <a name="community_items_description"></a>1.1.1. Property `OWASP Committee Schema > community > Community > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the community.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="community_items_platform"></a>1.1.2. Property `OWASP Committee Schema > community > Community > platform`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** The platform used by the community

Must be one of:
* "discord"
* "slack"

#### <a name="community_items_url"></a>1.1.3. Property `OWASP Committee Schema > community > Community > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the community.

## <a name="description"></a>2. Property `OWASP Committee Schema > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Description of the committee's purpose and activities.

## <a name="events"></a>3. Property `OWASP Committee Schema > events`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Events organized or sponsored by the committee.

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

### <a name="events_items"></a>3.1. OWASP Committee Schema > events > Event

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

#### <a name="events_items_description"></a>3.1.1. Property `OWASP Committee Schema > events > Event > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_title"></a>3.1.2. Property `OWASP Committee Schema > events > Event > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of the event

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="events_items_url"></a>3.1.3. Property `OWASP Committee Schema > events > Event > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL of the event

## <a name="logo"></a>4. Property `OWASP Committee Schema > logo`

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

### <a name="logo_items"></a>4.1. OWASP Committee Schema > logo > Logo

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

#### <a name="logo_items_small"></a>4.1.1. Property `OWASP Committee Schema > logo > Logo > small`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 192x192 pixels.

#### <a name="logo_items_medium"></a>4.1.2. Property `OWASP Committee Schema > logo > Logo > medium`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 256x256 pixels.

#### <a name="logo_items_large"></a>4.1.3. Property `OWASP Committee Schema > logo > Logo > large`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Logo size should be 512x512 pixels.

## <a name="mailing_list"></a>5. Property `OWASP Committee Schema > mailing_list`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Mailing list associated with the committee.

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

### <a name="mailing_list_items"></a>5.1. OWASP Committee Schema > mailing_list > Mailing List

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

#### <a name="mailing_list_items_description"></a>5.1.1. Property `OWASP Committee Schema > mailing_list > Mailing List > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_email"></a>5.1.2. Property `OWASP Committee Schema > mailing_list > Mailing List > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="mailing_list_items_title"></a>5.1.3. Property `OWASP Committee Schema > mailing_list > Mailing List > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Title of mailing list

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 10 |

#### <a name="mailing_list_items_url"></a>5.1.4. Property `OWASP Committee Schema > mailing_list > Mailing List > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** URL to mailing list

## <a name="meeting_minutes"></a>6. Property `OWASP Committee Schema > meeting_minutes`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Meeting minutes of the committee.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be           | Description                       |
| ----------------------------------------- | --------------------------------- |
| [Meeting Minutes](#meeting_minutes_items) | Meeting minutes of the committee. |

### <a name="meeting_minutes_items"></a>6.1. OWASP Committee Schema > meeting_minutes > Meeting Minutes

**Title:** Meeting Minutes

|                           |                         |
| ------------------------- | ----------------------- |
| **Type**                  | `object`                |
| **Required**              | No                      |
| **Additional properties** | Any type allowed        |
| **Defined in**            | #/$defs/meeting_minutes |

**Description:** Meeting minutes of the committee.

| Property                               | Pattern | Type   | Deprecated | Definition | Title/Description           |
| -------------------------------------- | ------- | ------ | ---------- | ---------- | --------------------------- |
| + [date](#meeting_minutes_items_date ) | No      | string | No         | -          | Date of the meeting         |
| + [url](#meeting_minutes_items_url )   | No      | string | No         | -          | Link to the meeting minutes |

#### <a name="meeting_minutes_items_date"></a>6.1.1. Property `OWASP Committee Schema > meeting_minutes > Meeting Minutes > date`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `date`   |

**Description:** Date of the meeting

#### <a name="meeting_minutes_items_url"></a>6.1.2. Property `OWASP Committee Schema > meeting_minutes > Meeting Minutes > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Link to the meeting minutes

## <a name="members"></a>7. Property `OWASP Committee Schema > members`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

**Description:** Members of the committee.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 2                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description               |
| ------------------------------- | ------------------------- |
| [Leader](#members_items)        | Leaders of the committee. |

### <a name="members_items"></a>7.1. OWASP Committee Schema > members > Leader

**Title:** Leader

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/members  |

**Description:** Leaders of the committee.

| Property                           | Pattern | Type             | Deprecated | Definition | Title/Description |
| ---------------------------------- | ------- | ---------------- | ---------- | ---------- | ----------------- |
| - [email](#members_items_email )   | No      | string           | No         | -          | E-mail address    |
| - [github](#members_items_github ) | No      | string           | No         | -          | GitHub username   |
| + [name](#members_items_name )     | No      | string           | No         | -          | Full name         |
| + [role](#members_items_role )     | No      | enum (of string) | No         | -          | Role of leader    |
| - [slack](#members_items_slack )   | No      | string           | No         | -          | Slack username    |

#### <a name="members_items_email"></a>7.1.1. Property `OWASP Committee Schema > members > Leader > email`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `email`  |

**Description:** E-mail address

#### <a name="members_items_github"></a>7.1.2. Property `OWASP Committee Schema > members > Leader > github`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** GitHub username

| Restrictions                      |                                                                                                   |
| --------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9-]{1,39}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9-%5D%7B1%2C39%7D%24) |

#### <a name="members_items_name"></a>7.1.3. Property `OWASP Committee Schema > members > Leader > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Full name

| Restrictions   |   |
| -------------- | - |
| **Min length** | 3 |

#### <a name="members_items_role"></a>7.1.4. Property `OWASP Committee Schema > members > Leader > role`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

**Description:** Role of leader

Must be one of:
* "Board Representative"
* "Board Of Director member"
* "Chair"
* "Member"
* "Vice Chair"
* "Secretary"
* "Staff Contact"

#### <a name="members_items_slack"></a>7.1.5. Property `OWASP Committee Schema > members > Leader > slack`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Slack username

| Restrictions                      |                                                                                                       |
| --------------------------------- | ----------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-zA-Z0-9._-]{1,21}$``` [Test](https://regex101.com/?regex=%5E%5Ba-zA-Z0-9._-%5D%7B1%2C21%7D%24) |

## <a name="name"></a>8. Property `OWASP Committee Schema > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The unique name of the committee

| Restrictions   |   |
| -------------- | - |
| **Min length** | 8 |

## <a name="resources"></a>9. Property `OWASP Committee Schema > resources`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of object` |
| **Required** | No                |

**Description:** Resources provided by the committee.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be     | Description |
| ----------------------------------- | ----------- |
| [resources items](#resources_items) | -           |

### <a name="resources_items"></a>9.1. OWASP Committee Schema > resources > resources items

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

| Property                           | Pattern | Type   | Deprecated | Definition | Title/Description                        |
| ---------------------------------- | ------- | ------ | ---------- | ---------- | ---------------------------------------- |
| + [title](#resources_items_title ) | No      | string | No         | -          | Title of the resource                    |
| + [type](#resources_items_type )   | No      | string | No         | -          | Type of resource (e.g., 'guide', 'tool') |
| + [url](#resources_items_url )     | No      | string | No         | -          | Link to access the resource              |

#### <a name="resources_items_title"></a>9.1.1. Property `OWASP Committee Schema > resources > resources items > title`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Title of the resource

#### <a name="resources_items_type"></a>9.1.2. Property `OWASP Committee Schema > resources > resources items > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Type of resource (e.g., 'guide', 'tool')

#### <a name="resources_items_url"></a>9.1.3. Property `OWASP Committee Schema > resources > resources items > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** Link to access the resource

## <a name="scope"></a>10. Property `OWASP Committee Schema > scope`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Scope and purpose of committee.

## <a name="social_media"></a>11. Property `OWASP Committee Schema > social_media`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Social media information of the committee.

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

### <a name="social_media_items"></a>11.1. OWASP Committee Schema > social_media > Social media

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

#### <a name="social_media_items_description"></a>11.1.1. Property `OWASP Committee Schema > social_media > Social media > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Description of the social media platform

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="social_media_items_platform"></a>11.1.2. Property `OWASP Committee Schema > social_media > Social media > platform`

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

#### <a name="social_media_items_url"></a>11.1.3. Property `OWASP Committee Schema > social_media > Social media > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the social media profile.

## <a name="sponsors"></a>12. Property `OWASP Committee Schema > sponsors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** Sponsors of the committee.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description      |
| ------------------------------- | ---------------- |
| [Sponsor](#sponsors_items)      | A sponsor entity |

### <a name="sponsors_items"></a>12.1. OWASP Committee Schema > sponsors > Sponsor

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

#### <a name="sponsors_items_description"></a>12.1.1. Property `OWASP Committee Schema > sponsors > Sponsor > description`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** A brief description of the sponsor

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_logo"></a>12.1.2. Property `OWASP Committee Schema > sponsors > Sponsor > logo`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor's logo

#### <a name="sponsors_items_name"></a>12.1.3. Property `OWASP Committee Schema > sponsors > Sponsor > name`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** The name of the sponsor or organization

| Restrictions   |   |
| -------------- | - |
| **Min length** | 5 |

#### <a name="sponsors_items_url"></a>12.1.4. Property `OWASP Committee Schema > sponsors > Sponsor > url`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |
| **Format**   | `uri`    |

**Description:** The URL of the sponsor.

## <a name="tags"></a>13. Property `OWASP Committee Schema > tags`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | Yes               |

**Description:** Tags associated with the committee

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

### <a name="tags_items"></a>13.1. OWASP Committee Schema > tags > tags items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

## <a name="website"></a>14. Property `OWASP Committee Schema > website`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |
| **Format**   | `uri`    |

**Description:** The official website of the committee.

| Restrictions   |   |
| -------------- | - |
| **Min length** | 4 |

----------------------------------------------------------------------------------------------------------------------------
