# Skill graph

| ID | Competency | Difficulty | Hours | Prerequisites |
|---|---|---|---:|---|
| programming_logic | programming_fundamentals | Beginner | 8 | — |
| data_structures | programming_fundamentals | Beginner | 8 | programming_logic |
| modular_design | programming_fundamentals | Beginner | 6 | programming_logic |
| error_testing | programming_fundamentals | Intermediate | 6 | modular_design |
| version_control | programming_fundamentals | Beginner | 4 | programming_logic |
| http_fundamentals | backend_foundations | Beginner | 10 | programming_logic |
| service_runtime | backend_foundations | Beginner | 8 | http_fundamentals |
| data_modeling | database_engineering | Beginner | 10 | data_structures |
| sql_queries | database_engineering | Beginner | 10 | data_modeling |
| transactions_indexes | database_engineering | Intermediate | 10 | sql_queries |
| identity_basics | authentication | Intermediate | 8 | http_fundamentals |
| secure_credentials | authentication | Intermediate | 8 | identity_basics |
| access_control | authentication | Intermediate | 8 | identity_basics |
| api_contracts | api_development | Intermediate | 10 | http_fundamentals, data_modeling |
| api_implementation | api_development | Intermediate | 14 | api_contracts, secure_credentials, sql_queries |
| api_quality | api_development | Intermediate | 8 | api_implementation, error_testing |

```text
programming_logic -> data_structures -> data_modeling -> sql_queries -> transactions_indexes
programming_logic -> modular_design -> error_testing
programming_logic -> http_fundamentals -> service_runtime -> identity_basics -> secure_credentials
identity_basics -> access_control
http_fundamentals + data_modeling -> api_contracts
api_contracts + secure_credentials + sql_queries -> api_implementation -> api_quality
```

