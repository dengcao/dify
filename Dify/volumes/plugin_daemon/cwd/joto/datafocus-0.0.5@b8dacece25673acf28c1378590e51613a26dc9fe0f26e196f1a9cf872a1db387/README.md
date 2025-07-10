## English
### Overview
DataFocus includes two tools, FocusSQL and FocusGPT. FocusSQL is the Hallucination controllable Text2SQL component，FocusGPT is the fast response ChatBI. 

### There are already so many Text-to-SQL frameworks. Why do we still need another one?
In simple terms, FocusSQL adopts a two-step SQL generation solution, which enables control over the hallucinations of LLM and truly builds the trust of non-technical users in the generated SQL results.

Below is the comparison table between FocusSQL and others:

#### Comparison Analysis Table
Here’s a side-by-side comparison of DataFocus plugin with other LLM-based frameworks:

| **Feature** | **Traditional LLM Frameworks** | **FocusSQL** |
| --- | --- | --- |
| Generation Process | Black box, direct SQL generation | Transparent, two-step (keywords + SQL) |
| Hallucination Risk | High, depends on model quality | Low, controllable (keyword verification) |
| Speed | Slow, relies on large model inference | Fast, deterministic keyword-to-SQL |
| Cost | High, requires advanced models | Low, reduces reliance on large models |
| Non-Technical User Friendliness | Low, hard to verify results | High, easy keyword checking |




The following will introduce how to configure and an example demonstration.

### 1. Apply for DataFocus Token
If you don't have the DataFocus application yet, please apply for one on the [DataFocus Website](https://www.datafocus.ai/en).  
Log in to your DataFocus application. Click **Admin** > **Interface Authentication** > **Bearer Token** > **New Bearer Token**, to create a new token and get _the token value_.  


![](https://cdn.nlark.com/yuque/0/2025/png/28274763/1744714560311-eebf7fed-41f1-46dc-8121-b3401ed97af3.png)

  
If you have a DataFocus private deployment environment, you can get Token on your own environment.

### 2. Fill in the configuration in Dify
Install DataFocus from Marketplace and fill **token** and **host** in the authorization page.Token is the value obtained in the previous step.If you have a DataFocus private deployment environment, host is your environment host. Otherwise, the SAAS environment address can be used by default.

### 3. Use the tool
DataFocus includes two tools, FocusSQL and FocusGPT.

#### FocusSQL
FocusSQL is a natural language to SQL plugin based on keyword parsing.  


![](https://cdn.nlark.com/yuque/0/2025/png/28274763/1744714560721-d4fe3afb-7df1-485a-8e19-d88ecd9a7ddd.png)

##### Output Variable JSON
| **Name** | **Type** | **Description** |
| --- | --- | --- |
| content | string | Generated SQL statements |
| question | string | Generated keywords |
| type | string | Return type |


Output Example

```plain
JSON



1{
2  "content": "select tbl_1882337315366133767.区域 as col_10715907381350065719,sum(tbl_1882337315366133767.销售数量) as col_9787758666777884439 from string tbl_1882337315366133767 group by tbl_1882337315366133767.区域 order by tbl_1882337315366133767.区域",
3  "question": "区域 销售数量的总和",
4  "type": "sql"
5}
```

#### FocusGPT
FocusGPT is an intelligent query plugin that supports multiple rounds of conversations, which allow you query data from your database.  
FocusGPT not only can return query SQL but also return query result to you.  


![](https://cdn.nlark.com/yuque/0/2025/png/28274763/1744714560442-f54ee0cb-561e-43d4-8bce-17645f2b1a4e.png)

##### Output Variable JSON
| **name** | **type** | **Description** |
| --- | --- | --- |
| code | number | Status code |
| columns | [[object]] | Two-dimensional array storing query results |
| count | number | Number of rows returned |
| duration | string | Query execution time, in seconds (s) |
| headers | [object] | Column header information for the two-dimensional array columns |
| » display | string | Display name of the column header |
| » name | string | Original column name of the header |
| » suf | string | Prefix of the column header, indicating aggregation method |
| sql | [object] | SQL corresponding to the query data |
| »select_clause | string | SQL corresponding to the query data |
| title | string | Keywords generated from parsing |


Output Example

```plain
JSON



1{
2  "code": 0,
3  "columns": [
4    [
5      "2024-12-01 00:00:00.000",
6      4901
7    ],
8    [
9      "2025-01-01 00:00:00.000",
10      4408
11    ],
12    [
13      "2025-02-01 00:00:00.000",
14      4223
15    ],
16    [
17      "2025-03-01 00:00:00.000",
18      4987
19    ]
20  ],
21  "count": 4,
22  "duration": "0.334571",
23  "headers": [
24    {
25      "display": "订单日期(MONTHLY)",
26      "name": "订单日期",
27      "suf": "MONTHLY"
28    },
29    {
30      "display": "销售数量(SUM)",
31      "name": "销售数量",
32      "suf": "SUM"
33    }
34  ],
35  "sql": {
36    "from_clause": "",
37    "group_by_clause": "",
38    "having_clause": "",
39    "order_by_clause": "",
40    "select_clause": "select date_trunc('month', \"电商销售数据gauss\".\"订单日期\") as col_0,sum(\"电商销售数据gauss\".\"销售数量\") as col_1 from \"电商销售数据gauss\" group by date_trunc('month', \"电商销售数据gauss\".\"订单日期\") order by date_trunc('month', \"电商销售数据gauss\".\"订单日期\")",
41    "where_clause": ""
42  },
43  "title": "每月 销售数量"
44}
```

#### Configuration
FocusSQL and FocusGPT have similar configuration. Below are the functions and usage instructions of each parameter

| **Parameter** | **Description** |
| --- | --- |
| Language | Language environment, only support _Chinese_ and _English_ |
| Query Statement | Natural language input by users |
| Table Name | Target data table for query |
| Data Model | Custom model parameter entry |
| Output SQL Type | Output SQL Type |
| Conversation Id | Unique identifier of the session, which allow tool identify and maintain session state |
| Action | The behavior of tool execution currently includes two types: obtaining table lists and dialogues |
| Datasource Type | Types of external data sources connected. If datasource type was selected, the connection parameters below need to be filled in |
| Host | host |
| Port | port |
| DB user | user |
| DB Password | password |
| Database Name | database name |
| JDBC | JDBC |
| Schema | Schema name |


#### Model Parameters
The data model needs to pass in a JSON string, and the structure of the model is as follows

##### Structure
| **Name** | **Type** | **Required** | **Description** |
| --- | --- | --- | --- |
| type | string | Yes | Database type |
| version | string | Yes | Database version, eg: 8.0 |
| tables | [object] | Yes | Table structure list |
| » tableDisplayName | string | No | Table display name |
| » tableName | string | No | Original table name |
| » columns | [object] | No | Columns structure list |
| »» columnDisplayName | string | Yes | Column display name |
| »» columnName | string | Yes | Original column name |
| »» dataType | string | Yes | Column data type |
| »» aggregation | string | Yes | Column default aggregation |
| relations | [object] | Yes | Association relationship list |
| » conditions | [object] | No | Associated conditions |
| »» dstColName | string | No | Dimension original column name |
| »» srcColName | string | No | Fact original column name |
| » dimensionTable | string | No | Dimension original table name |
| » factTable | string | No | Fact original table name |
| » joinType | string | No | Association type |


##### Parameter values
###### type
| **DataBase** | **Value** |
| --- | --- |
| MySQL | mysql |
| ClickHouse | clickhouse |
| Impala | impala |


###### dataType
| **DataType** | **Value** |
| --- | --- |
| Boolean | boolean |
| Integer | int |
| Long integer | bigint |
| Float | double |
| String | string |
| Timestamp | timestamp |
| Date type | date |
| Time type | time |


###### aggregation
| **Aggregation** | **Value** |
| --- | --- |
| Sum | SUM |
| Mean | AVERAGE |
| Min | MIN |
| Max | MAX |
| Count | COUNT |
| Number of deduplicates | COUNT_DISTINCT |
| Variance | VARIANCE |
| Standard deviation | STD_DEVIATION |
| None | NONE |


###### joinType
| **Assocation** | **Value** |
| --- | --- |
| Left association | LEFT JOIN |
| Right association | RIGHT JOIN |
| Internal | INNER JOIN |
| Fully associative | FULL JOIN |


##### Example
model

```plain
JSON



1{
2  "type": "mysql",
3  "version": "8.0",
4  "tables": [
5    {
6      "tableDisplayName": "string",
7      "tableName": "string",
8      "columns": [
9        {
10          "columnDisplayName": null,
11          "columnName": null,
12          "dataType": null,
13          "aggregation": null
14        }
15      ]
16    }
17  ],
18  "relations": [
19    {
20      "conditions": [
21        {
22          "dstColName": null,
23          "srcColName": null
24        }
25      ],
26      "dimensionTable": "string",
27      "factTable": "string",
28      "joinType": "LEFT JOIN"
29    }
30  ]
31}
```

### Consult
![](https://github.com/FocusSearch/focus_mcp_sql/raw/main/wechat-qrcode.png) WeChat: datafocus2018

[DataFocus Discord](https://discord.com/invite/AVufPnpaad)




